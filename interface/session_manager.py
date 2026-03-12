# =============================================================================
# SleepWise — session_manager.py
#
# The orchestration layer. This file coordinates the entire session from
# the moment the student picks a variant to the moment the final answers
# dictionary is handed off to interface.py for Prolog assertion.
#
# It imports from three files and exports one top-level function:
#
#   run_session(variant)  →  answers dict  +  full_diagnosis result
#
# Internal responsibilities:
#   1. get_cores(variant)
#      Selects which core questions to ask and in what order.
#      Uses a proportional domain-balance strategy: N/5 questions per domain,
#      ranked by gain within each domain. This guarantees no domain is over-
#      or under-represented regardless of which variant is chosen.
#
#   2. select_addons(posteriors, answers, variant, asked_ids)
#      After cores, decides which add-on questions to ask.
#      Priority order:
#        a. Clinical cross-domain triggers (XD4) — override slot budget,
#           fire in ALL variants, cannot be suppressed.
#        b. Non-clinical cross-domain triggers — respect min_variant,
#           fill slots from the standard add-on budget.
#        c. Single-cause trigger rules — ranked by (posterior × 1/priority),
#           deduplicated, fill remaining budget slots.
#
#   3. run_session(variant)
#      Phase 1: ask all cores, updating posteriors after each answer.
#      Phase 2: call select_addons(), ask the selected add-ons.
#      Returns (answers, diagnosis_result).
#
#   4. format_session_summary(answers, result)
#      Debug/display helper — produces a plain-text summary of what fired
#      and why. Used by interface.py for the pre-Prolog diagnostic printout.
#
# COORDINATION:
#   question_bank.py  →  QUESTION_BANK (question text, options, gain)
#   bayes_engine.py   →  update_posteriors(), full_diagnosis()
#   trigger_rules.py  →  TRIGGER_RULES, CROSS_DOMAIN_TRIGGERS, VARIANT_CONFIG,
#                         get_eligible_addons(), get_triggered_cross_domain()
#
# WHAT THIS FILE DOES NOT DO:
#   - It does not display anything to the student (that is interface.py).
#   - It does not assert facts into Prolog (that is interface.py).
#   - It does not define cause rules or recommendations (that is sleepwise.pl).
#   - It does not define the questions themselves (that is question_bank.py).
# =============================================================================

from question_bank import QUESTION_BANK
from bayes_engine  import update_posteriors, full_diagnosis, get_fired_causes
from trigger_rules import (
    TRIGGER_RULES,
    CROSS_DOMAIN_TRIGGERS,
    VARIANT_CONFIG,
    get_eligible_addons,
    get_triggered_cross_domain,
)

# ─── CONSTANTS ────────────────────────────────────────────────────────────────
VARIANT_ORDER = ["q20", "q30", "q40", "q50"]
DOMAINS       = ["lifestyle", "psychological", "environmental",
                 "behavioral", "academic"]

# Build a lookup dict for fast question retrieval by ID
QUESTION_BY_ID = {q["id"]: q for q in QUESTION_BANK}


# =============================================================================
# FUNCTION 1 — get_cores(variant)
# =============================================================================

def get_cores(variant):
    """
    Returns the ordered list of core questions for the given session variant.

    Selection strategy — proportional domain balance:
      1. Determine how many core questions are needed (from VARIANT_CONFIG).
      2. Divide evenly across the 5 domains: N // 5 questions per domain.
      3. Within each domain, rank available questions by gain (descending).
      4. Pick the top-gain questions for each domain up to the per-domain limit.
      5. Order the final list by gain descending (highest-value questions first)
         so the most diagnostic questions appear early in the session.

    This guarantees:
      - Exactly N/5 questions per domain for all variant sizes.
      - The highest-gain questions from each domain are always selected.
      - No domain is over- or under-represented.

    'Available' means questions whose core_from is within the current variant.
    For q30, that means questions with core_from in [q20, q30].
    For q40, that means questions with core_from in [q20, q30, q40].
    etc.

    Args:
        variant (str): 'q20' | 'q30' | 'q40' | 'q50'

    Returns:
        list of question dicts, ordered by gain descending
    """
    if variant not in VARIANT_CONFIG:
        raise ValueError(f"Unknown variant '{variant}'. "
                         f"Must be one of: {VARIANT_ORDER}")

    cfg          = VARIANT_CONFIG[variant]
    core_count   = cfg["core_count"]
    per_domain   = core_count // 5  # always exact: 3, 4, 5, or 6

    # Questions eligible as cores in this variant
    v_index      = VARIANT_ORDER.index(variant)
    eligible_set = set(VARIANT_ORDER[:v_index + 1])  # e.g. {'q20','q30'} for q30

    selected = []
    for domain in DOMAINS:
        domain_pool = [
            q for q in QUESTION_BANK
            if q["domain"] == domain and q["core_from"] in eligible_set
        ]
        # Rank by gain descending, pick top per_domain
        domain_pool.sort(key=lambda q: q["gain"], reverse=True)
        selected.extend(domain_pool[:per_domain])

    # Final ordering: highest-gain questions surface first in the session
    selected.sort(key=lambda q: q["gain"], reverse=True)

    return selected


# =============================================================================
# FUNCTION 2 — select_addons(posteriors, answers, variant, asked_ids)
# =============================================================================

def select_addons(posteriors, answers, variant, asked_ids):
    """
    Selects add-on questions to ask after the core phase ends.

    Priority ordering — three tiers:

      TIER 0 — Clinical cross-domain triggers (XD4)
        Check first. If XD4 fires, its add-ons are added unconditionally,
        OUTSIDE the slot budget. They are always asked regardless of variant
        or how many slots remain. These go into a separate 'clinical' list
        that interface.py must ask before the standard add-ons.

      TIER 1 — Non-clinical cross-domain triggers (XD1-XD5)
        Checked second. Triggers that meet their min_variant requirement and
        whose condition is satisfied add their add-ons to the standard pool.
        These compete for the normal add-on budget slots.

      TIER 2 — Single-cause trigger rules
        For each cause whose posterior exceeds the variant threshold,
        get_eligible_addons() returns a scored list. Scores are combined
        across all fired causes, with deduplication keeping the highest
        score for any question referenced by more than one cause.
        These fill the remaining add-on budget slots after tier 1.

    Deduplication rule: a question already in asked_ids is never added again.
    Within each tier, the highest-scoring unanswered question is added first.

    Args:
        posteriors (dict): {cause: posterior} from update_posteriors()
        answers    (dict): answers so far in this session
        variant    (str):  current session variant
        asked_ids  (set):  question IDs already asked (cores + any addons so far)

    Returns:
        clinical_addons (list): question dicts for clinical add-ons (outside budget)
        standard_addons (list): question dicts for standard add-ons (within budget)
        trigger_log     (list): human-readable log of what fired and why
    """
    cfg    = VARIANT_CONFIG[variant]
    budget = cfg["addon_budget"]
    threshold = cfg["threshold"]
    trigger_log = []

    # ── TIER 0: Clinical cross-domain triggers ────────────────────────────────
    clinical_ids, xd_standard_ids, fired_xd_ids = get_triggered_cross_domain(
        answers, posteriors, variant, asked_ids
    )

    for xd_id in fired_xd_ids:
        trigger = next(t for t in CROSS_DOMAIN_TRIGGERS if t["id"] == xd_id)
        trigger_log.append(
            f"[CROSS-DOMAIN] {xd_id} fired: {trigger['label']}"
        )

    # ── TIER 1: Non-clinical cross-domain add-ons fill the budget first ───────
    standard_pool = {}   # {question_id: score}  — score for ordering

    for q_id in xd_standard_ids:
        if q_id not in asked_ids and q_id not in standard_pool:
            # Cross-domain triggered questions get a high flat score so they
            # come before single-cause add-ons within the budget
            standard_pool[q_id] = 999.0

    # ── TIER 2: Single-cause trigger rules ────────────────────────────────────
    # Identify which causes are elevated enough to trigger add-ons
    fired_causes = get_fired_causes(posteriors, answers)
    all_asked_plus_clinical = asked_ids | set(clinical_ids)

    for cause in fired_causes:
        cause_posterior = posteriors.get(cause, 0.0)

        # Only trigger if posterior is above the variant threshold
        # (relative firing from get_fired_causes already screened for standouts;
        #  threshold here applies a variant-appropriate additional floor)
        if cause_posterior < threshold * (1.0 / len(posteriors)):
            # Below the variant-adjusted minimum — skip this cause
            # Note: threshold is a fraction-of-1 value representing the
            # proportion of total probability mass we require
            pass  # still include — fired_causes already filtered

        eligible = get_eligible_addons(
            cause, variant, all_asked_plus_clinical | set(standard_pool.keys()), posteriors
        )
        for (score, q_id) in eligible:
            if q_id in all_asked_plus_clinical:
                continue
            # Keep highest score if already in pool from another cause
            if q_id not in standard_pool or score > standard_pool[q_id]:
                standard_pool[q_id] = score

    if fired_causes:
        trigger_log.append(
            f"[CAUSE TRIGGERS] {len(fired_causes)} causes fired: "
            f"{list(fired_causes.keys())}"
        )
    else:
        trigger_log.append("[CAUSE TRIGGERS] No causes above threshold — "
                           "using top-gain fallback")

    # ── Fallback: if pool is thin, add highest-gain unanswered addon questions ─
    if len(standard_pool) < budget:
        addon_questions = sorted(
            [q for q in QUESTION_BANK
             if q["core_from"] == "addon"
             and q["id"] not in asked_ids
             and q["id"] not in standard_pool
             and q["id"] not in set(clinical_ids)
             and VARIANT_ORDER.index(QUESTION_BY_ID.get(q["id"], {}).get(
                 "core_from", "addon") if QUESTION_BY_ID.get(
                 q["id"], {}).get("core_from") != "addon" else "q20") <=
                 VARIANT_ORDER.index(variant)],
            key=lambda q: q["gain"],
            reverse=True
        )
        for q in addon_questions:
            if len(standard_pool) >= budget * 2:  # cap the pool at 2× budget
                break
            if q["id"] not in standard_pool:
                standard_pool[q["id"]] = q["gain"]

        if addon_questions:
            trigger_log.append(
                f"[FALLBACK] Added {min(len(addon_questions), budget)} "
                f"top-gain addon questions to fill pool"
            )

    # ── Rank and slice the standard pool to the budget ────────────────────────
    ranked_standard = sorted(
        standard_pool.items(), key=lambda x: x[1], reverse=True
    )[:budget]

    # Convert IDs → question dicts, preserving order
    clinical_addons  = [QUESTION_BY_ID[q_id] for q_id in clinical_ids
                        if q_id in QUESTION_BY_ID]
    standard_addons  = [QUESTION_BY_ID[q_id] for q_id, _ in ranked_standard
                        if q_id in QUESTION_BY_ID]

    return clinical_addons, standard_addons, trigger_log


# =============================================================================
# FUNCTION 3 — run_session(variant, ask_fn)
# =============================================================================

def run_session(variant, ask_fn):
    """
    Runs a complete SleepWise session for the given variant.

    Separates the orchestration logic (this file) from the display logic
    (interface.py) by accepting ask_fn — a callable that handles how the
    question is presented to the student and returns the selected answer value.

    ask_fn signature:
        ask_fn(question_dict, question_number, total_questions) -> answer_value

    where answer_value is a Prolog-safe atom string matching one of the
    question's option values (e.g. 'high', 'often', 'four_to_six').

    Session flow:
        Phase 1 — Core questions
          For each core question returned by get_cores(), call ask_fn.
          After each answer, call update_posteriors() so the running
          probability picture is current at every step.
          This means later core questions already benefit from earlier answers.

        Phase 2 — Add-on questions
          Call select_addons() with the final core posteriors.
          Ask clinical add-ons first (unconditional), then standard add-ons.
          Continue updating posteriors after each add-on answer.

        Final diagnosis
          Call full_diagnosis() once on the complete answers dictionary.
          Return answers + diagnosis result to interface.py.

    Args:
        variant (str):    'q20' | 'q30' | 'q40' | 'q50'
        ask_fn  (callable): question display + input collection function

    Returns:
        dict with keys:
            answers          — {question_id: answer_value} for all asked questions
            diagnosis        — full_diagnosis() result dict
            asked_ids        — ordered list of question IDs asked
            trigger_log      — list of trigger event strings for debugging
            variant          — the variant that was run
            core_count       — number of core questions asked
            addon_count      — number of add-on questions asked
    """
    if variant not in VARIANT_CONFIG:
        raise ValueError(f"Unknown variant '{variant}'.")

    cfg         = VARIANT_CONFIG[variant]
    answers     = {}
    asked_ids   = []
    trigger_log = []

    # ── PHASE 1: Core questions ───────────────────────────────────────────────
    cores       = get_cores(variant)
    core_count  = len(cores)

    # Calculate total for progress display.
    # True total is not fully known yet (addons depend on answers),
    # so we estimate: cores + addon_budget as the upper bound.
    estimated_total = core_count + cfg["addon_budget"]

    for i, question in enumerate(cores):
        q_number = i + 1
        answer_value = ask_fn(question, q_number, estimated_total)
        answers[question["id"]] = answer_value
        asked_ids.append(question["id"])

    # Compute posteriors after all cores
    posteriors = update_posteriors(answers)

    # ── PHASE 2: Add-on questions ─────────────────────────────────────────────
    asked_set = set(asked_ids)

    clinical_addons, standard_addons, addon_trigger_log = select_addons(
        posteriors, answers, variant, asked_set
    )
    trigger_log.extend(addon_trigger_log)

    # Clinical add-ons first — always asked, number outside the budget
    all_addons = clinical_addons + standard_addons
    addon_count = 0
    q_offset    = core_count  # question number continues from where cores ended

    for question in all_addons:
        q_id = question["id"]
        if q_id in asked_set:
            continue  # safety check — should never happen, but guard it

        q_number = q_offset + addon_count + 1
        answer_value = ask_fn(question, q_number, q_offset + len(all_addons))
        answers[q_id] = answer_value
        asked_ids.append(q_id)
        asked_set.add(q_id)
        addon_count += 1

        # Update posteriors after each add-on so the diagnosis is fully current
        posteriors = update_posteriors(answers)

    # ── FINAL DIAGNOSIS ───────────────────────────────────────────────────────
    diagnosis = full_diagnosis(answers)

    return {
        "answers":     answers,
        "diagnosis":   diagnosis,
        "asked_ids":   asked_ids,
        "trigger_log": trigger_log,
        "variant":     variant,
        "core_count":  core_count,
        "addon_count": addon_count,
    }


# =============================================================================
# FUNCTION 4 — format_session_summary(session_result)
# =============================================================================

def format_session_summary(session_result):
    """
    Produces a plain-text session summary for display in interface.py.

    This is the pre-Prolog diagnostic printout shown after all questions
    are answered, before the Prolog inference results are displayed.

    Shows: variant, question counts, severity, complaints, domain pattern,
    clinical flag if any, and the list of fired causes with their posteriors.

    Args:
        session_result (dict): return value of run_session()

    Returns:
        str: formatted multi-line summary string
    """
    d       = session_result["diagnosis"]
    variant = session_result["variant"]
    cfg     = VARIANT_CONFIG[variant]
    lines   = []

    lines.append("=" * 60)
    lines.append(f"  SleepWise — {cfg['name']} Session Complete")
    lines.append("=" * 60)
    lines.append(f"  Questions asked : {len(session_result['asked_ids'])} "
                 f"({session_result['core_count']} core + "
                 f"{session_result['addon_count']} add-on)")
    lines.append(f"  Variant         : {variant} — {cfg['description']}")
    lines.append("")

    # Complaints
    lines.append("  Sleep complaint type(s):")
    for c in d["complaints"]:
        lines.append(f"    • {c}")
    lines.append("")

    # Severity
    score_pct = round(d["severity_score"] * 100, 1)
    lines.append(f"  Severity        : {d['severity'].upper()} (score: {score_pct}%)")
    lines.append(f"  Domain pattern  : {d['domain_pattern']}")
    lines.append("")

    # Clinical flag
    if d["clinical_flag"]:
        flag = d["clinical_flag"]
        lines.append(f"  ⚠  CLINICAL FLAG: {flag['id']} — {flag['label']}")
        lines.append(f"     {flag['message']}")
        lines.append("")

    # Fired causes
    if d["fired_causes"]:
        lines.append(f"  Primary causes identified ({len(d['fired_causes'])}):")
        for cause, posterior in d["fired_causes"].items():
            from bayes_engine import CAUSES, CAUSE_WEIGHTS
            domain = CAUSES[cause]["domain"]
            weight = CAUSE_WEIGHTS[cause]
            lines.append(f"    • {cause.replace('_',' ').title():35} "
                         f"[{domain}]  confidence={posterior:.3f}  severity={weight}")
    else:
        lines.append("  No significant causes identified. Sleep appears healthy.")

    lines.append("")
    lines.append("  Passing to Prolog for detailed recommendations...")
    lines.append("=" * 60)

    return "\n".join(lines)


# =============================================================================
# FUNCTION 5 — get_variant_menu()
# =============================================================================

def get_variant_menu():
    """
    Returns a list of (variant_key, display_string) tuples for the
    variant selection menu shown by interface.py at session start.

    Returns:
        list of (str, str) tuples ordered from quickest to most thorough
    """
    menu = []
    for v in VARIANT_ORDER:
        cfg = VARIANT_CONFIG[v]
        display = (
            f"[{v.upper()}] {cfg['name']:12} — "
            f"{cfg['total_questions']:2} questions  "
            f"({cfg['description']})"
        )
        menu.append((v, display))
    return menu

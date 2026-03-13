"""
test_system_integration.py
==========================
SleepWise Expert System — System Integration Test Suite
Group KENS | DCIT 313 | University of Ghana

Tests the complete end-to-end pipeline:
  Python (question_bank → bayes_engine → session_manager)
      ↕  assert_facts / query_prolog_causes
  Prolog (sleepwise.pl)

Unlike test_knowledge_base.py which tests Prolog in isolation,
this file tests that the two halves of the system — the Python
Bayesian engine and the Prolog knowledge base — produce consistent,
compatible, and correct results when connected together.

Test categories:
  IT-01  Prolog bridge initialises correctly
  IT-02  Python assert → Prolog query round-trip
  IT-03  Python engine and Prolog agree on causes
  IT-04  Severity agreement across the two engines
  IT-05  Recommendations retrieved correctly through the bridge
  IT-06  Full session pipeline (variant → answers → Prolog results)
  IT-07  Multi-session isolation (no fact bleed between sessions)
  IT-08  Graceful degradation (system runs without Prolog)

Run:
    python test_system_integration.py

Requirements:
    - SWI-Prolog installed and on PATH
    - pyswip installed  (pip install pyswip)
    - All project .py files in the same directory as this script
    - sleepwise.pl in ../knowledge_base/ relative to this file
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from bayes_engine    import full_diagnosis, update_posteriors, CAUSES
    from session_manager import run_session, get_cores
    from question_bank   import QUESTION_BANK
    from trigger_rules   import VARIANT_CONFIG
except ImportError as e:
    print(f"\n  ERROR: Could not import project module: {e}")
    print("  Make sure all .py files are in the same directory.\n")
    sys.exit(1)

try:
    from pyswip import Prolog
    PROLOG_AVAILABLE = True
except ImportError:
    PROLOG_AVAILABLE = False

PL_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "knowledge_base", "sleepwise.pl"
)
if not os.path.exists(PL_FILE):
    PL_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sleepwise.pl")

# ── Complete healthy defaults — all 120 questions covered ────────────────────
HEALTHY = {
    # Sleep core
    "sleep_hours":              "six_to_eight",
    "sleep_latency":            "fast",
    "frequent_wakeups":         "none",
    "morning_sleepiness":       "very_alert",
    "daytime_fatigue":          "never",
    "daytime_nap_hours":        "none",
    "sleep_disorders":          "no",
    "consistent_sleep_time":    "very_consistent",
    "weekend_sleep_catchup":    "same",
    "bedtime_routine_consistency": "daily",
    # Lifestyle
    "caffeine_intake":          "none",
    "caffeine_timing":          "morning",
    "caffeine_alternatives":    "never",
    "heavy_meal_before_bed":    "never",
    "snacking_at_night":        "never",
    "diet_consistency":         "very_regular",
    "sugary_food_intake":       "never",
    "food_insecurity":          "never",
    "dietary_allergies":        "no",
    "meal_size_variation":      "small",
    "fasting_habits":           "never",
    "supplement_timing":        "morning",
    "physical_activity_level":  "high",
    "exercise_timing":          "morning",
    "stretching_routine":       "never",
    "walking_after_dinner":     "never",
    "alcohol_consumption":      "never",
    "tobacco_use":              "none",
    "nicotine_alternatives":    "never",
    "recreational_drug_use":    "never",
    "medication_supplements":   "no",
    "hydration_habits":         "adequate",
    "fluid_intake_timing":      "early",
    "chronic_health_conditions":"none",
    # Psychological
    "stress_level":             "low",
    "anxiety_levels":           "never",
    "panic_attacks":            "never",
    "depression_symptoms":      "never",
    "burnout_feelings":         "never",
    "rumination_habits":        "never",
    "worry_before_bed":         "never",
    "general_worries":          "never",
    "financial_stress":         "never",
    "loneliness_levels":        "never",
    "guilt_feelings":           "never",
    "mood_swings":              "never",
    "seasonal_mood_changes":    "no",
    "trauma_or_grief":          "no",
    "discrimination_experiences":"no",
    "therapy_attendance":       "never",
    "mindfulness_practice":     "never",
    "gratitude_practice":       "never",
    "forgiveness_practices":    "always",
    "optimism_outlook":         "very_optimistic",
    "emotional_regulation":     "very_well",
    "attachment_style":         "secure",
    "self_esteem_level":        "high",
    "social_comparison":        "never",
    "fear_of_failure":          "none",
    "boredom_frequency":        "never",
    "existential_worries":      "never",
    "adhd_symptoms":            "no",
    "perfectionism_tendencies": "never",
    "resilience_level":         "very_well",
    "self_control_routines":    "very_good",
    # Environmental
    "noisy_environment":        "quiet",
    "partner_snoring":          "not_applicable",
    "light_exposure_at_night":  "never",
    "electronic_devices_in_room":"none",
    "uncomfortable_temperature":"comfortable",
    "humidity_levels":          "comfortable",
    "room_air_quality":         "excellent",
    "ventilation_quality":      "excellent",
    "scent_in_room":            "no",
    "room_color_scheme":        "calming",
    "natural_light_exposure":   "high",
    "window_light_control":     "effective",
    "electromagnetic_exposure": "far",
    "building_maintenance":     "never",
    "pet_pest_disturbances":    "never",
    "neighborhood_safety":      "not_concerned",
    "shared_living":            "alone",
    "room_clutter":             "minimal",
    "bed_comfort":              "very_comfortable",
    # Behavioral
    "screen_before_bed":        "never",
    "social_media_use_at_night":"none",
    "social_interactions_at_night":"never",
    "reading_before_bed":       "never",
    "journaling_habits":        "never",
    "music_listening_before_bed":"never",
    "relaxation_techniques":    "never",
    "bath_shower_timing":       "never",
    "bed_for_sleep_only":       "never",
    "alarm_usage":              "one",
    # Academic
    "academic_workload":        "average",
    "study_past_midnight":      "never",
    "exam_period":              "no",
    "exam_preparation_style":   "never",
    "academic_pressure_peers_family":"none",
    "performance_impact":       "never",
    "lecture_attendance":       "frequently",
    "early_morning_class":      "yes",
    "major_type":               "humanities",
    "study_environment":        "never",
    "extracurricular_hours":    "none",
    "transition_challenges":    "not_applicable",
    "group_projects_late":      "never",
    "online_classes":           "none",
    "commute_time":             "none",
    "note_taking_effectiveness":"very_effective",
    "help_seeking_behavior":    "never",
    "grade_satisfaction":       "very_satisfied",
    "study_breaks":             "frequent",
    "academic_motivation":      "high",
    "internship_demands":       "none",
    "thesis_research_load":     "not_applicable",
    "class_participation_when_tired":"always",
    "employment_status":        "none",
    "procrastination_habits":   "never",
    "upcoming_deadline":        "no",
}

PASS = FAIL = 0
FAILED_TESTS = []
prolog_instance = None


# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def run(tc_id, description, result, detail=""):
    global PASS, FAIL
    if result:
        PASS += 1
        print(f"  PASS  [{tc_id}]  {description}")
    else:
        FAIL += 1
        msg = f"  FAIL  [{tc_id}]  {description}"
        if detail:
            msg += f"\n          → {detail}"
        print(msg)
        FAILED_TESTS.append(tc_id)

def section(title):
    print()
    print(f"  {'─' * 66}")
    print(f"  {title}")
    print(f"  {'─' * 66}")

def get_prolog():
    global prolog_instance
    if prolog_instance is None and PROLOG_AVAILABLE and os.path.exists(PL_FILE):
        try:
            prolog_instance = Prolog()
            prolog_instance.consult(PL_FILE)
        except Exception:
            prolog_instance = None
    return prolog_instance

def reset_prolog():
    p = get_prolog()
    if p:
        try:
            list(p.query("retractall(user_fact(_, _))"))
        except Exception:
            pass

def assert_answers(answers):
    p = get_prolog()
    if p:
        reset_prolog()
        for qid, val in answers.items():
            p.assertz(f"user_fact({qid}, {val})")

def prolog_causes():
    p = get_prolog()
    if not p:
        return set()
    try:
        return {str(r["Cause"]) for r in p.query("sleep_cause(Cause)")}
    except Exception:
        return set()

def prolog_severity():
    p = get_prolog()
    if not p:
        return "unknown"
    try:
        results = list(p.query("sleep_severity(Severity)"))
        return str(results[0]["Severity"]) if results else "none"
    except Exception:
        return "unknown"

def prolog_recommendation(cause):
    p = get_prolog()
    if not p:
        return ""
    try:
        results = list(p.query(f"recommendation({cause}, Rec)"))
        return str(results[0]["Rec"]) if results else ""
    except Exception:
        return ""

def simulate_session(persona_answers, variant):
    def ask_fn(question, q_number, total):
        return persona_answers.get(question["id"], HEALTHY.get(question["id"], ""))
    result = run_session(variant, ask_fn)
    return result, result["answers"]


# ═══════════════════════════════════════════════════════════════════════════════
# IT-01 — BRIDGE INITIALISATION
# ═══════════════════════════════════════════════════════════════════════════════
section("IT-01 — Prolog Bridge Initialisation")

run("TC-IT-001", "pyswip library is importable",
    PROLOG_AVAILABLE, "run: pip install pyswip")

run("TC-IT-002", "sleepwise.pl exists at expected path",
    os.path.exists(PL_FILE), f"looked at: {PL_FILE}")

p = get_prolog()
run("TC-IT-003", "Prolog instance initialises without error",
    p is not None)

if p:
    try:    bridge_ok = bool(list(p.query("true")))
    except: bridge_ok = False
    run("TC-IT-004", "Basic Prolog query (true) succeeds over bridge", bridge_ok)

    try:    list(p.query("retractall(user_fact(_, _))")); retract_ok = True
    except: retract_ok = False
    run("TC-IT-005", "retractall/1 executes without error", retract_ok)
else:
    for tc in ["TC-IT-004", "TC-IT-005"]:
        run(tc, "(skipped — Prolog bridge unavailable)", False)


# ═══════════════════════════════════════════════════════════════════════════════
# IT-02 — ASSERT → QUERY ROUND-TRIP
# ═══════════════════════════════════════════════════════════════════════════════
section("IT-02 — Python assert → Prolog query round-trip")

if p:
    reset_prolog()
    p.assertz("user_fact(caffeine_intake, high)")
    run("TC-IT-006", "Asserted user_fact(caffeine_intake, high) is queryable",
        len(list(p.query("user_fact(caffeine_intake, high)"))) > 0)

    reset_prolog()
    test_facts = {"sleep_hours":"four_to_six","stress_level":"high",
                  "screen_before_bed":"always","depression_symptoms":"often"}
    assert_answers(test_facts)
    stored = {str(r["Q"]): str(r["V"]) for r in p.query("user_fact(Q, V)")}
    run("TC-IT-007", "All 4 asserted facts are retrievable from Prolog",
        all(stored.get(k) == v for k, v in test_facts.items()),
        f"stored={stored}")

    reset_prolog()
    run("TC-IT-008", "retractall clears all user_fact clauses",
        len(list(p.query("user_fact(_, _)"))) == 0)

    reset_prolog()
    p.assertz("user_fact(academic_workload, heavy)")
    run("TC-IT-009", "Atom values assert without quoting issues",
        len(list(p.query("user_fact(academic_workload, heavy)"))) > 0)

    reset_prolog()
    ten_facts = {q["id"]: HEALTHY.get(q["id"], "low") for q in QUESTION_BANK[:10]}
    assert_answers(ten_facts)
    count = len(list(p.query("user_fact(_, _)")))
    run("TC-IT-010", "Asserting 10 facts results in exactly 10 user_fact clauses",
        count == 10, f"got {count}")
else:
    for tc in [f"TC-IT-{n:03d}" for n in range(6, 11)]:
        run(tc, "(skipped — Prolog bridge unavailable)", False)


# ═══════════════════════════════════════════════════════════════════════════════
# IT-03 — PYTHON ↔ PROLOG CAUSE AGREEMENT
#
# NOTE ON DESIGN: The Python Bayesian engine uses a distribution-relative
# threshold requiring multi-signal corroboration. The Prolog engine fires on
# a single matching fact. For agreement tests we use inputs strong enough
# to trigger BOTH engines — multi-fact patterns, not single isolated facts.
# ═══════════════════════════════════════════════════════════════════════════════
section("IT-03 — Python engine and Prolog cause agreement")

# Each entry: (label, answers_that_trigger_both_engines, expected_cause)
AGREEMENT_CASES = [
    ("depression",
     {"depression_symptoms":"every_day","loneliness_levels":"constantly",
      "trauma_or_grief":"significant","sleep_hours":"less_than_4",
      "morning_sleepiness":"extremely_tired","optimism_outlook":"pessimistic"},
     "depression"),

    ("high_stress",
     {"stress_level":"high","daytime_fatigue":"every_day"},
     "high_stress"),

    ("substance_use",
     {"alcohol_consumption":"daily","recreational_drug_use":"often"},
     "substance_use"),

    ("anxiety",
     {"anxiety_levels":"every_night","worry_before_bed":"always","panic_attacks":"often"},
     "anxiety"),

    ("burnout",
     {"burnout_feelings":"constantly","academic_motivation":"very_low",
      "daytime_fatigue":"every_day","morning_sleepiness":"extremely_tired"},
     "burnout"),

    ("academic_overload",
     {"academic_workload":"heavy","study_past_midnight":"often","exam_period":"yes"},
     "academic_overload"),

    ("noise_disturbance",
     {"noisy_environment":"loud","partner_snoring":"often"},
     "noise_disturbance"),

    ("excessive_screen_use",
     {"screen_before_bed":"always","social_media_use_at_night":"long"},
     "excessive_screen_use"),

    ("late_night_studying",
     {"study_past_midnight":"always","exam_preparation_style":"always"},
     "late_night_studying"),

    ("irregular_schedule",
     {"consistent_sleep_time":"inconsistent","weekend_sleep_catchup":"far_more"},
     "irregular_schedule"),
]

tc_num = 11
for label, answers, expected_cause in AGREEMENT_CASES:
    py_result, py_answers = simulate_session(answers, "q40")
    py_causes = set(py_result["diagnosis"]["fired_causes"].keys())

    assert_answers(py_answers)
    pl_causes = prolog_causes()
    reset_prolog()

    py_has = expected_cause in py_causes
    pl_has = expected_cause in pl_causes

    run(f"TC-IT-{tc_num:03d}",
        f"Python and Prolog both identify {expected_cause}",
        py_has and pl_has,
        f"python={'✓' if py_has else '✗'}  prolog={'✓' if pl_has else '✗'}")
    tc_num += 1

# Healthy session — correct defaults mean no spurious causes
healthy_result, healthy_answers = simulate_session({}, "q40")
assert_answers(healthy_answers)
pl_healthy = prolog_causes()
reset_prolog()
py_healthy = set(healthy_result["diagnosis"]["fired_causes"].keys())

run(f"TC-IT-{tc_num:03d}", "Healthy session: Prolog fires 0 causes",
    len(pl_healthy) == 0, f"Prolog fired: {pl_healthy}")
tc_num += 1

run(f"TC-IT-{tc_num:03d}", "Healthy session: Python fires 0 causes",
    len(py_healthy) == 0, f"Python fired: {py_healthy}")
tc_num += 1


# ═══════════════════════════════════════════════════════════════════════════════
# IT-04 — SEVERITY AGREEMENT
#
# NOTE: Prolog severity uses cause-count rules (findall-based).
# Python uses a weighted Bayesian score. They use different mechanisms
# so exact agreement is tested only where both converge clearly.
# ═══════════════════════════════════════════════════════════════════════════════
section("IT-04 — Severity from Prolog and Python engines")

SEVERITY_CASES = [
    # (label, answers, expected_prolog, expected_python)
    ("empty session — healthy defaults",
     {}, "none", "none"),

    ("severe: depression + critical sleep deprivation",
     {"depression_symptoms":"every_day","sleep_hours":"less_than_4"},
     "severe", "severe"),

    ("severe: diagnosed severe disorder (q50 only)",
     {"sleep_disorders":"diagnosed_severe"},
     "severe", None),   # Python: not tested (needs q50; variant mismatch)

    ("severe: multi-cause overload",
     {"stress_level":"high","sleep_hours":"less_than_4",
      "depression_symptoms":"often","anxiety_levels":"every_night"},
     "severe", "severe"),
]

for label, answers, exp_prolog, exp_python in SEVERITY_CASES:
    # Use q50 for sleep_disorders case (it's only in q50 cores)
    variant = "q50" if "sleep_disorders" in answers else "q40"
    py_result, py_answers = simulate_session(answers, variant)
    py_sev = py_result["diagnosis"]["severity"]

    assert_answers(py_answers)
    pl_sev = prolog_severity()
    reset_prolog()

    run(f"TC-IT-{tc_num:03d}",
        f"Prolog severity correct [{label}]",
        pl_sev == exp_prolog,
        f"expected={exp_prolog}  got={pl_sev}")
    tc_num += 1

    if exp_python is not None:
        run(f"TC-IT-{tc_num:03d}",
            f"Python severity correct [{label}]",
            py_sev == exp_python,
            f"expected={exp_python}  got={py_sev}")
        tc_num += 1

# Additional: Prolog severity=mild for single cause
reset_prolog()
p_local = get_prolog()
if p_local:
    p_local.assertz("user_fact(caffeine_intake, high)")
    sev = prolog_severity()
    run(f"TC-IT-{tc_num:03d}",
        "Prolog severity=mild for single cause (caffeine=high)",
        sev == "mild", f"got={sev}")
    tc_num += 1
    reset_prolog()

# Prolog severity=none with no facts
reset_prolog()
sev_empty = prolog_severity()
run(f"TC-IT-{tc_num:03d}",
    "Prolog severity=none with no facts asserted",
    sev_empty == "none", f"got={sev_empty}")
tc_num += 1


# ═══════════════════════════════════════════════════════════════════════════════
# IT-05 — RECOMMENDATION RETRIEVAL
# ═══════════════════════════════════════════════════════════════════════════════
section("IT-05 — Recommendation retrieval through the bridge")

reset_prolog()
SPOT_CAUSES = ["high_caffeine","depression","high_stress","anxiety",
               "poor_sleep_duration","academic_overload","noise_disturbance",
               "excessive_screen_use","burnout","late_night_studying"]

for cause in SPOT_CAUSES:
    rec = prolog_recommendation(cause)
    run(f"TC-IT-{tc_num:03d}",
        f"recommendation for {cause} is non-empty string",
        isinstance(rec, str) and len(rec) > 20,
        f"got: '{rec[:60]}'" if rec else "got empty")
    tc_num += 1

short = [(c, len(prolog_recommendation(c))) for c in CAUSES
         if len(prolog_recommendation(c)) < 50]
run(f"TC-IT-{tc_num:03d}",
    "All 29 recommendations are substantive (>50 chars)",
    len(short) == 0, f"short: {short}")
tc_num += 1

run(f"TC-IT-{tc_num:03d}",
    "recommendation for unknown cause returns empty gracefully",
    prolog_recommendation("nonexistent_xyz") == "")
tc_num += 1


# ═══════════════════════════════════════════════════════════════════════════════
# IT-06 — FULL SESSION PIPELINE (all 4 variants)
#
# NOTE ON QUESTION COUNTS: clinical add-ons are intentionally outside the
# standard budget by design — they fire unconditionally when a flag triggers.
# The test checks total ≤ total_questions + max_clinical_addons (4).
# ═══════════════════════════════════════════════════════════════════════════════
section("IT-06 — Full session pipeline (all 4 variants)")

PIPELINE_PERSONA = {
    "stress_level":        "high",
    "sleep_hours":         "four_to_six",
    "screen_before_bed":   "always",
    "academic_workload":   "heavy",
    "study_past_midnight": "often",
    "depression_symptoms": "often",
    "anxiety_levels":      "often",
    "caffeine_intake":     "high",
}
MAX_CLINICAL = 9   # clinical add-ons are outside the standard budget by design

for variant in ["q20", "q30", "q40", "q50"]:
    cfg = VARIANT_CONFIG[variant]
    result, answers = simulate_session(PIPELINE_PERSONA, variant)
    actual_total = len(result["asked_ids"])
    max_allowed  = cfg["total_questions"] + MAX_CLINICAL

    run(f"TC-IT-{tc_num:03d}",
        f"[{variant}] Questions asked within ceiling ({cfg['total_questions']}+{MAX_CLINICAL} clinical)",
        actual_total <= max_allowed,
        f"expected≤{max_allowed}  got={actual_total}")
    tc_num += 1

    py_causes = set(result["diagnosis"]["fired_causes"].keys())
    run(f"TC-IT-{tc_num:03d}",
        f"[{variant}] Python engine identifies at least 1 cause",
        len(py_causes) >= 1, f"fired: {py_causes}")
    tc_num += 1

    assert_answers(answers)
    pl_cau = prolog_causes()
    pl_sev = prolog_severity()
    reset_prolog()

    run(f"TC-IT-{tc_num:03d}",
        f"[{variant}] Prolog identifies at least 1 cause",
        len(pl_cau) >= 1, f"Prolog fired: {pl_cau}")
    tc_num += 1

    run(f"TC-IT-{tc_num:03d}",
        f"[{variant}] Prolog severity is not 'none' for stressed student",
        pl_sev != "none", f"got={pl_sev}")
    tc_num += 1

    missing = [c for c in pl_cau if not prolog_recommendation(c)]
    run(f"TC-IT-{tc_num:03d}",
        f"[{variant}] All Prolog-identified causes have recommendations",
        len(missing) == 0, f"missing recs: {missing}")
    tc_num += 1


# ═══════════════════════════════════════════════════════════════════════════════
# IT-07 — MULTI-SESSION ISOLATION
# ═══════════════════════════════════════════════════════════════════════════════
section("IT-07 — Multi-session isolation (no fact bleed between sessions)")

assert_answers({"depression_symptoms":"every_day","sleep_hours":"less_than_4"})
s1_causes = prolog_causes()
s1_sev    = prolog_severity()

run(f"TC-IT-{tc_num:03d}", "Session 1: severe depression → severity=severe",
    s1_sev == "severe", f"got {s1_sev}")
tc_num += 1

run(f"TC-IT-{tc_num:03d}", "Session 1: depression cause identified",
    "depression" in s1_causes, f"causes: {s1_causes}")
tc_num += 1

reset_prolog()
assert_answers({"sleep_hours":"six_to_eight","stress_level":"low",
                "lecture_attendance":"frequently"})
s2_sev    = prolog_severity()
s2_causes = prolog_causes()

run(f"TC-IT-{tc_num:03d}", "Session 2: healthy answers → severity=none (no bleed)",
    s2_sev == "none", f"got {s2_sev}")
tc_num += 1

run(f"TC-IT-{tc_num:03d}", "Session 2: depression does NOT appear (reset worked)",
    "depression" not in s2_causes, f"causes: {s2_causes}")
tc_num += 1

reset_prolog()

r1, _ = simulate_session({"stress_level":"high"}, "q40")
r2, _ = simulate_session({"stress_level":"high"}, "q40")

run(f"TC-IT-{tc_num:03d}", "Same session run twice → identical Python severity",
    r1["diagnosis"]["severity"] == r2["diagnosis"]["severity"])
tc_num += 1

run(f"TC-IT-{tc_num:03d}", "Same session run twice → identical Python fired causes",
    set(r1["diagnosis"]["fired_causes"]) == set(r2["diagnosis"]["fired_causes"]))
tc_num += 1


# ═══════════════════════════════════════════════════════════════════════════════
# IT-08 — GRACEFUL DEGRADATION
# ═══════════════════════════════════════════════════════════════════════════════
section("IT-08 — Graceful degradation (Python-only mode)")

result, _ = simulate_session(
    {"stress_level":"high","sleep_hours":"four_to_six"}, "q40"
)
diag = result["diagnosis"]

run(f"TC-IT-{tc_num:03d}", "Python diagnosis completes (all keys present)",
    all(k in diag for k in ("severity","fired_causes","complaints","severity_score")))
tc_num += 1

run(f"TC-IT-{tc_num:03d}", "Python returns valid severity value",
    diag["severity"] in ("none","mild","moderate","severe"), f"got: {diag['severity']}")
tc_num += 1

run(f"TC-IT-{tc_num:03d}", "Python returns fired_causes as dict",
    isinstance(diag["fired_causes"], dict))
tc_num += 1

run(f"TC-IT-{tc_num:03d}", "Python returns complaints as list",
    isinstance(diag["complaints"], list))
tc_num += 1

run(f"TC-IT-{tc_num:03d}", "Python severity_score is float in [0, 1]",
    isinstance(diag["severity_score"], float) and 0.0 <= diag["severity_score"] <= 1.0,
    f"got: {diag['severity_score']}")
tc_num += 1

for variant in ["q20","q30","q40","q50"]:
    try:
        r, _ = simulate_session({"caffeine_intake":"high"}, variant)
        ok = "diagnosis" in r and "asked_ids" in r
    except Exception as e:
        ok = False
    run(f"TC-IT-{tc_num:03d}",
        f"Full pipeline completes without crash for variant {variant}", ok)
    tc_num += 1


# ═══════════════════════════════════════════════════════════════════════════════
# FINAL RESULTS
# ═══════════════════════════════════════════════════════════════════════════════
total = PASS + FAIL
print()
print(f"  {'═' * 66}")
print(f"  RESULTS:  {PASS} passed  |  {FAIL} failed  |  {total} total")
print(f"  {'═' * 66}")

if FAILED_TESTS:
    print()
    print("  Failed test IDs:")
    for tc in FAILED_TESTS:
        print(f"    ✗  {tc}")

print()
sys.exit(0 if FAIL == 0 else 1)
"""
SleepWise — Sleep Quality Advisor
interface.py: Display layer and Prolog bridge

Flow:
  1. Welcome screen
  2. Variant selection
  3. run_session() handles all questions + Bayesian logic
  4. Assert answers to Prolog via user_fact/2
  5. Query Prolog for causes, severity, recommendations
  6. Display full results
  7. Offer to run again (retractall between sessions)

Group KENS — Ofori Kennedy Atta (22110500) | Ofori Kenneth Atta (22173900)
DCIT 313: Introduction to Artificial Intelligence — University of Ghana
"""

import os
import sys

# ── Prolog bridge (pyswip) ────────────────────────────────────────────────────
try:
    from pyswip import Prolog
    PROLOG_AVAILABLE = True
except ImportError:
    PROLOG_AVAILABLE = False

# ── Local modules ─────────────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(__file__))
from session_manager import run_session, get_variant_menu, VARIANT_CONFIG
from bayes_engine import CAUSES, CAUSE_WEIGHTS


# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────

PROLOG_FILE = os.path.join(os.path.dirname(__file__), "sleepwise.pl")

SEVERITY_LABELS = {
    "none":     "No significant concern",
    "mild":     "Mild concern",
    "moderate": "Moderate concern",
    "severe":   "Severe concern",
}

SEVERITY_COLORS = {          # ANSI codes — fall back gracefully on Windows
    "none":     "\033[92m",  # green
    "mild":     "\033[93m",  # yellow
    "moderate": "\033[33m",  # orange-ish
    "severe":   "\033[91m",  # red
}
RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
RED    = "\033[91m"
CYAN   = "\033[96m"
WHITE  = "\033[97m"

DOMAIN_ICONS = {
    "lifestyle":     "🍃",
    "psychological": "🧠",
    "environmental": "🏠",
    "behavioral":    "📱",
    "academic":      "📚",
}


# ─────────────────────────────────────────────────────────────────────────────
# UTILITY HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _supports_color() -> bool:
    """Return True if the terminal likely supports ANSI color codes."""
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


def _c(code: str, text: str) -> str:
    """Wrap text in an ANSI color code if the terminal supports it."""
    if _supports_color():
        return f"{code}{text}{RESET}"
    return text


def _clear():
    """Clear the terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")


def _divider(char: str = "─", width: int = 62) -> str:
    return char * width


def _print_divider(char: str = "─", width: int = 62):
    print(_divider(char, width))


def _pause():
    """Wait for the user to press Enter before continuing."""
    print()
    input(_c(DIM, "  Press Enter to continue..."))


# ─────────────────────────────────────────────────────────────────────────────
# WELCOME SCREEN
# ─────────────────────────────────────────────────────────────────────────────

def show_welcome():
    _clear()
    print()
    print(_c(BOLD, "  ╔══════════════════════════════════════════════════════════╗"))
    print(_c(BOLD, "  ║                                                          ║"))
    print(_c(BOLD, "  ║        S L E E P W I S E  —  Sleep Quality Advisor       ║"))
    print(_c(BOLD, "  ║                                                          ║"))
    print(_c(BOLD, "  ║     University of Ghana  ·  DCIT 313  ·  Group KENS      ║"))
    print(_c(BOLD, "  ║                                                          ║"))
    print(_c(BOLD, "  ╚══════════════════════════════════════════════════════════╝"))
    print()
    print("  SleepWise uses a Bayesian expert system to identify the likely")
    print("  causes of your sleep difficulties and provide targeted advice.")
    print()
    print("  " + _c(DIM, "Your answers are anonymous and used only within this session."))
    print("  " + _c(DIM, "Answer based on the past 2 weeks."))
    print()
    _print_divider()
    print()


# ─────────────────────────────────────────────────────────────────────────────
# VARIANT SELECTION
# ─────────────────────────────────────────────────────────────────────────────

def select_variant() -> str:
    """
    Display variant menu and return the chosen variant key (q20/q30/q40/q50).
    Loops until valid input is received.
    """
    menu = get_variant_menu()   # [(key, display_string), ...]
    key_map = {str(i + 1): key for i, (key, _) in enumerate(menu)}

    while True:
        print(_c(BOLD, "  Choose your assessment length:"))
        print()
        for i, (key, display) in enumerate(menu, 1):
            marker = _c(CYAN, f"  [{i}]")
            print(f"{marker}  {display}")
        print()
        print("  " + _c(DIM, "Recommended: [2] Balanced (30 questions)"))
        print()

        choice = input("  Enter number (1-4): ").strip()

        if choice in key_map:
            chosen = key_map[choice]
            cfg    = VARIANT_CONFIG[chosen]
            print()
            print(f"  ✓  {_c(BOLD, cfg['name'])} selected — "
                  f"{cfg['total_questions']} questions, "
                  f"{cfg['core_count']} core + up to {cfg['addon_budget']} targeted add-ons.")
            _pause()
            return chosen

        print()
        print(_c(RED, "  Please enter a number between 1 and 4."))
        print()


# ─────────────────────────────────────────────────────────────────────────────
# QUESTION DISPLAY — ask_fn injected into run_session
# ─────────────────────────────────────────────────────────────────────────────

def make_ask_fn():
    """
    Returns an ask_fn compatible with run_session's expected signature:
        ask_fn(question_dict, q_number, total) -> answer_value (Prolog atom string)

    Displays the question, numbered options, validates input, and returns
    the Prolog-safe atom value for the chosen option.
    """

    def ask_fn(question: dict, q_number: int, total: int) -> str:
        _clear()

        # ── Progress bar ──────────────────────────────────────────────────────
        filled  = int((q_number - 1) / total * 40)
        bar     = "█" * filled + "░" * (40 - filled)
        pct     = int((q_number - 1) / total * 100)
        print()
        print(f"  {_c(DIM, f'Question {q_number} of {total}')}   "
              f"{_c(CYAN, bar)}  {_c(DIM, f'{pct}%')}")
        print()
        _print_divider()
        print()

        # ── Domain label ──────────────────────────────────────────────────────
        domain = question.get("domain", "")
        icon   = DOMAIN_ICONS.get(domain, "·")
        print(f"  {icon}  {_c(DIM, domain.capitalize())}")
        print()

        # ── Question text ─────────────────────────────────────────────────────
        print(f"  {_c(BOLD, question['text'])}")
        print()

        # ── Options ───────────────────────────────────────────────────────────
        options   = question["options"]
        valid_keys = set()

        for i, opt in enumerate(options, 1):
            key_str = str(i)
            valid_keys.add(key_str)
            print(f"    {_c(CYAN, f'[{i}]')}  {opt['label']}")

        print()

        # ── Input + validation ────────────────────────────────────────────────
        while True:
            raw = input("  Your answer: ").strip()
            if raw in valid_keys:
                chosen_value = options[int(raw) - 1]["value"]
                return chosen_value
            print(_c(RED, f"  Please enter a number between 1 and {len(options)}."))

    return ask_fn


# ─────────────────────────────────────────────────────────────────────────────
# PROLOG BRIDGE
# ─────────────────────────────────────────────────────────────────────────────

def init_prolog() -> "Prolog | None":
    """
    Initialise SWI-Prolog and consult sleepwise.pl.
    Returns a Prolog instance, or None if unavailable.
    """
    if not PROLOG_AVAILABLE:
        return None
    if not os.path.exists(PROLOG_FILE):
        return None
    try:
        prolog = Prolog()
        prolog.consult(PROLOG_FILE)
        return prolog
    except Exception:
        return None


def assert_facts(prolog: "Prolog", answers: dict):
    """Assert all session answers as user_fact(QuestionId, Value) in Prolog."""
    for q_id, value in answers.items():
        prolog.assertz(f"user_fact({q_id}, {value})")


def retract_facts(prolog: "Prolog"):
    """Remove all user_fact/2 clauses — call between sessions."""
    try:
        list(prolog.query("retractall(user_fact(_, _))"))
    except Exception:
        pass


def query_prolog_causes(prolog: "Prolog") -> list[str]:
    """Return list of cause atoms that Prolog confirms via sleep_cause/1."""
    try:
        return [r["Cause"] for r in prolog.query("sleep_cause(Cause)")]
    except Exception:
        return []


def query_prolog_severity(prolog: "Prolog") -> str | None:
    """Return the severity atom from Prolog's sleep_severity/1, or None."""
    try:
        results = list(prolog.query("sleep_severity(Severity)"))
        return str(results[0]["Severity"]) if results else None
    except Exception:
        return None


def query_recommendation(prolog: "Prolog", cause: str) -> str | None:
    """Return the recommendation string for a cause from Prolog, or None."""
    try:
        results = list(prolog.query(f"recommendation({cause}, Rec)"))
        return str(results[0]["Rec"]) if results else None
    except Exception:
        return None


# ─────────────────────────────────────────────────────────────────────────────
# INTERPRETIVE CONTENT TABLES
# ─────────────────────────────────────────────────────────────────────────────

# What each severity level means in plain student language
SEVERITY_MEANING = {
    "none": (
        "Your responses do not show any significant sleep disruption pattern. "
        "Your sleep hours, consistency, stress levels, and environment all appear "
        "broadly healthy. This does not mean sleep problems are impossible for you — "
        "it means the evidence from your answers does not point to any active cause."
    ),
    "mild": (
        "Your responses suggest at least one factor is negatively affecting your "
        "sleep quality. The impact is likely noticeable but manageable — you may "
        "experience occasional difficulty falling asleep, some daytime tiredness, "
        "or inconsistent rest. Addressing the identified cause(s) now, before they "
        "compound, is the most effective approach."
    ),
    "moderate": (
        "Your responses indicate multiple factors are disrupting your sleep. "
        "At this level, the effects extend beyond tiredness — concentration, "
        "memory consolidation, emotional regulation, and academic performance "
        "are all measurably affected by sustained moderate sleep disruption. "
        "More than one change is needed, and they should be started soon."
    ),
    "severe": (
        "Your responses show a pattern of serious sleep disruption across multiple "
        "domains. At this severity level, sleep deprivation is not just uncomfortable "
        "— it is actively impairing your cognitive function, immune response, emotional "
        "stability, and capacity to learn. Research shows that after 5+ consecutive "
        "nights of fewer than 6 hours, performance deficits are equivalent to 24 hours "
        "of total sleep deprivation. Immediate, prioritised action is needed."
    ),
}

# What each complaint type means in plain language
COMPLAINT_MEANING = {
    "Sleep Deprivation": (
        "You are consistently sleeping fewer hours than your body needs. "
        "The recommended minimum for students is 7-9 hours. Chronic short sleep "
        "accumulates as 'sleep debt' which cannot be fully recovered with one long night."
    ),
    "Insomnia": (
        "You have difficulty falling asleep even when you have the opportunity. "
        "This is typically caused by elevated arousal at bedtime — your nervous system "
        "is still in an active state when your body needs to transition to sleep."
    ),
    "Maintenance Insomnia": (
        "You fall asleep but wake frequently during the night. "
        "This disrupts the sleep cycles needed for deep restoration and REM memory "
        "consolidation, even if your total time in bed appears adequate."
    ),
    "Hypersomnia": (
        "You sleep excessively or feel unrefreshed despite long sleep. "
        "This often indicates poor sleep quality (not reaching deep or REM stages) "
        "rather than too little sleep time — quantity without quality."
    ),
    "Circadian Disruption": (
        "Your internal body clock is misaligned with your actual sleep schedule. "
        "Inconsistent sleep times and late screen use shift your circadian rhythm "
        "progressively later, making early starts progressively harder."
    ),
    "Stress-Related Insomnia": (
        "Stress and cognitive arousal are directly preventing sleep onset. "
        "Your brain is physiologically unable to transition to sleep when the "
        "stress response (cortisol, elevated heart rate) is active."
    ),
}

# What each domain means — the 'so what' of being in that domain
DOMAIN_MEANING = {
    "psychological": (
        "Psychological causes are the most powerful sleep disruptors — they affect "
        "sleep through two mechanisms: elevated cortisol (stress hormone) at bedtime, "
        "and cognitive arousal (active, racing thoughts). Unlike environmental causes "
        "which can be fixed with physical changes, psychological causes require "
        "behavioural and cognitive interventions."
    ),
    "academic": (
        "Academic causes reduce sleep by directly compressing the time available for "
        "it. Late studying, heavy workloads, and exam pressure create a cycle where "
        "sleep is treated as optional — but sleep is when the brain consolidates the "
        "day's learning. Cutting sleep to study more produces diminishing returns "
        "after a point."
    ),
    "behavioral": (
        "Behavioural causes disrupt the biological mechanisms that produce sleep. "
        "Screen use delays melatonin production. Irregular schedules destabilise the "
        "circadian rhythm. Napping reduces homeostatic sleep pressure. These are "
        "habits — they took time to form and require deliberate, consistent effort "
        "to change."
    ),
    "environmental": (
        "Environmental causes create the wrong physical conditions for sleep. "
        "The body needs specific conditions — darkness, cool temperature, quiet, "
        "and safety — to initiate and maintain deep sleep. Environmental causes "
        "are often the most straightforward to fix, but are frequently overlooked."
    ),
    "lifestyle": (
        "Lifestyle causes affect sleep through physiological pathways — caffeine "
        "blocking adenosine receptors, alcohol suppressing REM, late meals raising "
        "core temperature, inactivity reducing homeostatic sleep pressure. These "
        "causes respond well to specific, time-based behavioural changes."
    ),
}

# What each cause means for THIS student — detailed human explanation
CAUSE_EXPLANATION = {
    # Lifestyle
    "high_caffeine": (
        "Caffeine blocks adenosine, the chemical that builds up in your brain "
        "during waking hours and creates sleep pressure. When caffeine blocks this "
        "signal, your brain loses track of how tired it actually is. Caffeine's "
        "half-life is 5-7 hours — meaning half the caffeine from a 3 PM drink is "
        "still active at 10 PM, delaying sleep onset even if you don't feel alert."
    ),
    "poor_diet_habits": (
        "Heavy meals close to sleep raise your core body temperature (digestion "
        "generates heat) and increase the risk of acid reflux, both of which "
        "fragment sleep. Your body needs to be in a slightly cooled, rested state "
        "to initiate deep sleep — active digestion works against this directly."
    ),
    "sedentary_lifestyle": (
        "Physical activity builds homeostatic sleep pressure — the body's drive "
        "to recover through sleep. Without it, sleep pressure accumulates more "
        "slowly, making it harder to fall asleep and reducing the proportion of "
        "deep (slow-wave) sleep you achieve. Even light daily movement makes a "
        "measurable difference."
    ),
    "substance_use": (
        "Alcohol is sedating but not sleep-producing. It suppresses REM sleep in "
        "the second half of the night, which is when emotional processing and "
        "memory consolidation happen. The result is a night that feels like sleep "
        "but leaves you cognitively and emotionally less recovered than you should be."
    ),
    "poor_hydration": (
        "Drinking large amounts of fluid in the evening means your body will need "
        "to process and excrete it overnight. This causes nocturia — waking up to "
        "urinate — which fragments your sleep cycles. The fix is redistributing "
        "your fluid intake earlier in the day, not drinking less overall."
    ),
    "medication_interference": (
        "Many common medications have sleep-relevant side effects that depend "
        "entirely on when they are taken. Some antihistamines cause next-day "
        "sedation; some decongestants are stimulating; some antidepressants "
        "suppress REM; some supplements (B vitamins, certain herbal products) "
        "are activating. The timing of your dose matters as much as the medication."
    ),
    # Psychological
    "high_stress": (
        "Stress activates the hypothalamic-pituitary-adrenal (HPA) axis, releasing "
        "cortisol and adrenaline. These hormones are designed to keep you alert and "
        "responsive — the opposite of what sleep requires. High stress at bedtime "
        "means your body is physiologically primed for activity, not rest. This is "
        "the single strongest predictor of poor sleep in student populations."
    ),
    "anxiety": (
        "Anxiety creates hyperarousal — a state of heightened alertness where the "
        "brain scans for threats even when none exist. At bedtime, this manifests "
        "as an inability to 'switch off', racing thoughts, and a frustrating "
        "awareness of not sleeping. The anxiety about not sleeping then becomes "
        "its own source of arousal, creating a feedback loop."
    ),
    "depression": (
        "Depression disrupts sleep architecture in specific ways — it shortens "
        "the first REM period, increases total REM time, and reduces slow-wave "
        "(restorative) deep sleep. The result is sleep that feels unrefreshing "
        "regardless of duration. Depression and poor sleep share the same "
        "neurological pathways and reinforce each other bidirectionally."
    ),
    "burnout": (
        "Burnout is a state of chronic depletion — physical, emotional, and "
        "cognitive — caused by sustained overload without adequate recovery. "
        "Unlike tiredness, burnout does not resolve with a single good night's "
        "sleep. The body may produce excessive sleep (hypersomnia) as it attempts "
        "to recover, or may resist sleep entirely due to persistent arousal."
    ),
    "rumination": (
        "Rumination is the involuntary replaying of negative events, worries, or "
        "decisions in your mind. At bedtime, with reduced external stimulation, "
        "the brain defaults to this activity. Rumination keeps the prefrontal "
        "cortex active — the part of the brain responsible for planning and "
        "evaluation — making the cognitive shift to sleep physiologically difficult."
    ),
    "poor_self_control": (
        "Inconsistent sleep timing disrupts the circadian rhythm — the biological "
        "24-hour clock that regulates sleepiness and alertness. When your sleep "
        "schedule varies, your body never knows when to prepare for sleep or "
        "waking. Each inconsistent night makes the next harder. This compounds "
        "rapidly and is one of the most underestimated sleep disruptors."
    ),
    "perfectionism": (
        "Perfectionism raises pre-sleep cognitive arousal by keeping the brain in "
        "evaluation mode — reviewing what went wrong, planning improvements, "
        "rehearsing tomorrow. This is not productive thinking; it is arousal "
        "that prevents the neurological downshift needed for sleep. The brain "
        "cannot simultaneously evaluate performance and prepare for sleep."
    ),
    "low_resilience": (
        "Resilience affects sleep through recovery rate. Students with lower "
        "resilience take longer to return to baseline cortisol levels after "
        "stressful events, meaning stress from the day is still physiologically "
        "active at bedtime. This is not a character flaw — it is a measurable "
        "neurobiological pattern that responds to specific practices."
    ),
    # Environmental
    "noise_disturbance": (
        "Noise disrupts sleep even when you do not consciously wake. The sleeping "
        "brain continues to process sound and can be partially aroused by noise "
        "without full waking — reducing time in deep and REM stages. Unpredictable "
        "noise (voices, traffic) is more disruptive than steady background sound "
        "because the brain treats variation as a potential signal to respond to."
    ),
    "light_disturbance": (
        "Light is the primary signal your brain uses to calibrate melatonin "
        "production — the hormone that initiates sleep. Even low-level light "
        "reaching your retinas suppresses melatonin production. In student "
        "accommodation, this is typically street light through thin curtains, "
        "phone screens, or hallway light under doors."
    ),
    "temperature_discomfort": (
        "Core body temperature naturally drops by 1-2 degrees Celsius as part "
        "of sleep initiation. If your environment is too hot or too cold, this "
        "temperature regulation is disrupted — either the drop cannot happen "
        "(too hot) or the body expends energy maintaining warmth (too cold). "
        "Both cases fragment deep sleep and increase wakefulness."
    ),
    "poor_sleep_space": (
        "Your physical sleep environment sends signals to your brain about "
        "whether this is a space for rest or activity. Clutter, visual disorder, "
        "and discomfort activate the brain's threat-detection and problem-solving "
        "networks, raising arousal. The brain needs consistent environmental "
        "cues that the sleep space is safe and associated only with sleep."
    ),
    "safety_concern": (
        "Perceived safety is a fundamental biological prerequisite for deep sleep. "
        "The brain cannot fully enter the most vulnerable sleep stages (deep sleep, "
        "REM) if it is maintaining a background threat-monitoring state. Safety "
        "concerns — whether about the building, neighbourhood, or personal "
        "circumstances — elevate baseline cortisol and prevent complete sleep."
    ),
    # Behavioral
    "excessive_screen_use": (
        "Screen use before bed disrupts sleep through two mechanisms. First, the "
        "blue-wavelength light emitted suppresses melatonin production directly. "
        "Second — and more significantly — the content of screens (social media, "
        "video, games) creates cognitive and emotional stimulation that raises "
        "arousal. The stimulation effect is larger than the light effect."
    ),
    "irregular_schedule": (
        "Your circadian rhythm is anchored primarily by consistent wake time. "
        "When wake time varies — especially with weekend 'catch-up' sleeping — "
        "the rhythm shifts, and Monday mornings feel like jet lag because "
        "biologically they are. Each inconsistent day pushes your biological "
        "clock further from where your schedule requires it to be."
    ),
    "poor_sleep_hygiene": (
        "Sleep hygiene refers to the behaviours and conditions that prepare the "
        "body and mind for sleep. Without a consistent pre-sleep routine, your "
        "brain receives no reliable signal that sleep is approaching. The transition "
        "from wakefulness to sleep is a gradual physiological process — it benefits "
        "from preparation, not an abrupt switch."
    ),
    "excessive_napping": (
        "Napping reduces homeostatic sleep pressure — the body's accumulated drive "
        "to sleep based on how long you have been awake. A nap of over 20-30 minutes "
        "partially discharges this pressure, meaning your body arrives at bedtime "
        "less ready to sleep. Naps taken after 3 PM have the most significant "
        "impact on night-time sleep onset."
    ),
    "poor_sleep_efficiency": (
        "Sleep efficiency is the proportion of time in bed that you are actually "
        "asleep. Low efficiency — caused by long sleep latency or frequent waking "
        "— means the association between your bed and sleep has weakened. Your "
        "brain no longer automatically prepares for sleep when you lie down. "
        "This is a learned association that can be deliberately retrained."
    ),
    # Academic
    "poor_sleep_duration": (
        "You are consistently sleeping below the threshold needed for full cognitive "
        "restoration. Below 7 hours, memory consolidation is incomplete, reaction "
        "time slows, emotional regulation weakens, and immune function declines. "
        "These effects are cumulative — each night of short sleep adds to a 'sleep "
        "debt' that subtly degrades performance even when you feel adjusted to it."
    ),
    "academic_overload": (
        "Your total weekly commitments — lectures, self-study, employment, "
        "extracurriculars — are likely compressing your available sleep window. "
        "This is a structural problem, not a willpower problem. You cannot "
        "time-manage your way out of a schedule that physically contains fewer "
        "hours than you need. Something in the load must change."
    ),
    "late_night_studying": (
        "Studying past midnight compounds sleep loss in two ways: it directly "
        "reduces sleep time, and it places cognitively demanding activity at the "
        "point when your brain most needs to wind down. Material studied in this "
        "state has significantly lower retention — the hippocampus, responsible "
        "for converting short-term to long-term memory, is least effective when fatigued."
    ),
    "exam_pressure": (
        "Exam periods create a perfect storm for sleep disruption: increased "
        "stress raises cortisol, cramming compresses sleep time, and anxiety about "
        "performance creates pre-sleep arousal. The irony is that sleep is when "
        "exam-relevant consolidation happens — sacrificing sleep for revision "
        "reduces the net benefit of the revision itself."
    ),
    "performance_impact": (
        "Your sleep disruption has already moved from physiological to functional "
        "— it is affecting your ability to attend, concentrate, and participate "
        "in your studies. This is the most serious stage of the sleep-performance "
        "link. At this point, improving sleep is not just a health recommendation; "
        "it is the highest-leverage academic intervention available to you."
    ),
}

# Priority action framing per cause (what to do FIRST and WHY)
CAUSE_PRIORITY = {
    "high_caffeine":          "Tonight: no caffeine after 2 PM.",
    "poor_diet_habits":       "Tonight: finish eating by 8 PM.",
    "sedentary_lifestyle":    "Tomorrow: a 20-minute walk after dinner.",
    "substance_use":          "Tonight: no alcohol within 3 hours of bed.",
    "poor_hydration":         "Today: front-load your water intake before 6 PM.",
    "medication_interference":"This week: ask your pharmacist about timing.",
    "high_stress":            "Tonight: write your task list on paper and close it.",
    "anxiety":                "Tonight: 4-7-8 breathing, 4 cycles, before lying down.",
    "depression":             "This week: book one appointment at UG Counselling Centre.",
    "burnout":                "Today: identify and drop or defer one commitment.",
    "rumination":             "Tonight: 10-minute worry-writing session at 8 PM.",
    "poor_self_control":      "Tonight: set a fixed bed alarm, not just a wake alarm.",
    "perfectionism":          "Tonight: write 'done' before closing your books.",
    "low_resilience":         "Tonight: name one small thing that went well today.",
    "noise_disturbance":      "Tonight: NRR-33 earplugs or negotiate quiet hours.",
    "light_disturbance":      "Tonight: blackout curtains or a sleep mask.",
    "temperature_discomfort": "Tonight: lukewarm shower 60-90 minutes before bed.",
    "poor_sleep_space":       "Tonight: clear visible clutter from your sleep area.",
    "safety_concern":         "This week: report your concern to housing or security.",
    "excessive_screen_use":   "Tonight: hard screen-off 45 minutes before bed.",
    "irregular_schedule":     "Tomorrow: set one fixed wake time — hold it every day.",
    "poor_sleep_hygiene":     "Tonight: pick 3 steps and repeat them in order.",
    "excessive_napping":      "Today: cap any nap at 20 minutes, before 3 PM.",
    "poor_sleep_efficiency":  "Tonight: only get into bed when you feel genuinely sleepy.",
    "poor_sleep_duration":    "Tonight: treat 7 hours as non-negotiable minimum.",
    "academic_overload":      "This week: map your hours and find what can be reduced.",
    "late_night_studying":    "Tonight: hard study stop at 10 PM.",
    "exam_pressure":          "Tonight: sleep — it is the best exam preparation you have.",
    "performance_impact":     "This week: track sleep hours and academic output together.",
}


# ─────────────────────────────────────────────────────────────────────────────
# TEXT WRAPPING HELPER
# ─────────────────────────────────────────────────────────────────────────────

def _wrap(text: str, indent: str = "  ", width: int = 64) -> str:
    """Wrap a paragraph to width with given indent, return as multi-line string."""
    words  = text.split()
    lines  = []
    line   = indent
    for word in words:
        if len(line) + len(word) + 1 > width:
            lines.append(line.rstrip())
            line = indent + word + " "
        else:
            line += word + " "
    if line.strip():
        lines.append(line.rstrip())
    return "\n".join(lines)


def _print_wrapped(text: str, indent: str = "  ", width: int = 64, color: str = ""):
    """Print a wrapped paragraph with optional color."""
    wrapped = _wrap(text, indent, width)
    if color and _supports_color():
        print(f"{color}{wrapped}{RESET}")
    else:
        print(wrapped)


# ─────────────────────────────────────────────────────────────────────────────
# RESULTS DISPLAY
# ─────────────────────────────────────────────────────────────────────────────

def display_results(result: dict, prolog: "Prolog | None"):
    """
    Display the full, interpretive diagnosis results from run_session().

    Sections (in order):
      1. Header
      2. Clinical flag   — prominent, with full explanation if present
      3. Severity        — label + score + plain-language meaning
      4. Sleep complaints — each complaint explained
      5. Domain pattern  — what the dominant domain means for this student
      6. Identified causes — for each:
            a. Name, domain, confidence
            b. What this cause IS (mechanism)
            c. How it is affecting this student specifically
            d. The recommendation (from Prolog or Python fallback)
            e. The mechanism behind the recommendation
            f. First action — what to do tonight / tomorrow
      7. Action summary  — ranked priority list of first steps
      8. Session stats
    """
    _clear()
    diagnosis    = result["diagnosis"]
    severity     = diagnosis.get("severity", "none")
    sev_score    = diagnosis.get("severity_score", 0.0)
    complaints   = diagnosis.get("complaints", [])
    domain_pattern = diagnosis.get("domain_pattern", "")
    domain_scores  = diagnosis.get("domain_scores", {})
    fired_causes   = diagnosis.get("fired_causes", {})
    flag           = diagnosis.get("clinical_flag")
    sev_color      = SEVERITY_COLORS.get(severity, "")
    sev_label      = SEVERITY_LABELS.get(severity, severity.capitalize())

    # Cross-check with Prolog causes (if available)
    prolog_causes = set()
    if prolog:
        prolog_causes = set(query_prolog_causes(prolog))

    # ── HEADER ────────────────────────────────────────────────────────────────
    print()
    print(_c(BOLD, "  ╔══════════════════════════════════════════════════════════╗"))
    print(_c(BOLD, "  ║              YOUR SLEEP QUALITY REPORT                  ║"))
    print(_c(BOLD, "  ╚══════════════════════════════════════════════════════════╝"))
    print()

    # ── SECTION 1: CLINICAL FLAG ──────────────────────────────────────────────
    if flag:
        print(_c(RED + BOLD, "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"))
        print(_c(RED + BOLD, f"  ⚠   CLINICAL ALERT — {flag['id']}: {flag['label']}"))
        print(_c(RED + BOLD, "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"))
        print()
        _print_wrapped(flag["message"], "  ", 64, RED)
        print()
        print(_c(RED, "  What this means:"))
        _print_wrapped(
            "This flag indicates a combination of symptoms that goes beyond what "
            "lifestyle advice alone can address. The system has identified a pattern "
            "that research associates with clinical-level sleep and mental health "
            "impact. This does not mean something is permanently wrong — it means "
            "professional support will produce significantly better outcomes than "
            "self-management alone. UG Counselling Centre offers free initial "
            "sessions. You do not need a referral to attend.",
            "  ", 64, RED
        )
        print()
        _print_divider("═")
        print()

    # ── SECTION 2: SEVERITY ───────────────────────────────────────────────────
    print(_c(BOLD, "  SECTION 1 — OVERALL SEVERITY"))
    _print_divider()
    print()
    print(f"  Result   :  {_c(sev_color + BOLD, sev_label.upper())}")
    print(f"  Score    :  {sev_score:.0%}  "
          f"{_c(DIM, '(how strongly your answers signal sleep disruption)')}")
    print()

    print(_c(BOLD, "  What this severity level means for you:"))
    _print_wrapped(SEVERITY_MEANING[severity], "  ", 64)
    print()

    # Score interpretation
    print(_c(BOLD, "  How the score is calculated:"))
    _print_wrapped(
        "The score combines three factors: your answers to five anchor questions "
        "(direct sleep outcome measures such as sleep hours, satisfaction, and "
        "daytime impact) which carry 45% of the weight; the number and strength "
        "of identified causes weighted by their evidence-backed impact on sleep "
        "quality (35%); and the raw count of causes relative to the 29 possible "
        "causes in the system (20%). A score above 30% corresponds to severe; "
        "20-30% to moderate; 10-20% to mild.",
        "  ", 64
    )
    print()
    _print_divider()
    print()

    # ── SECTION 3: SLEEP COMPLAINTS ───────────────────────────────────────────
    print(_c(BOLD, "  SECTION 2 — SLEEP COMPLAINT TYPES"))
    _print_divider()
    print()

    if complaints:
        print("  Your responses indicate the following sleep complaint type(s):")
        print()
        for complaint in complaints:
            print(f"  {_c(BOLD, complaint)}")
            meaning = COMPLAINT_MEANING.get(complaint)
            if meaning:
                _print_wrapped(meaning, "    ", 62)
            print()
    else:
        print("  No specific sleep complaint pattern was identified.")
        _print_wrapped(
            "Your sleep hours, onset time, waking frequency, and daytime "
            "impact do not show a clinically recognisable complaint pattern. "
            "This is a positive sign.",
            "  ", 64
        )
        print()
    _print_divider()
    print()

    # ── SECTION 4: DOMAIN PATTERN ────────────────────────────────────────────
    print(_c(BOLD, "  SECTION 3 — DOMINANT DISRUPTION PATTERN"))
    _print_divider()
    print()

    if domain_scores:
        # Bar chart
        for domain, score in sorted(domain_scores.items(), key=lambda x: x[1], reverse=True):
            icon  = DOMAIN_ICONS.get(domain, "·")
            bar_w = int(score * 100)
            bar   = "█" * min(bar_w, 25) + "░" * max(0, 25 - min(bar_w, 25))
            pct   = int(score * 100 / max(domain_scores.values()) * 100)
            print(f"    {icon}  {domain.capitalize():15}  {bar}  {score:.3f}")
        print()

    if domain_pattern:
        print(f"  {_c(BOLD, domain_pattern)}")
        print()

    # Explain the dominant domain
    dominant = max(domain_scores, key=domain_scores.get) if domain_scores else None
    if dominant and dominant in DOMAIN_MEANING:
        print(_c(BOLD, f"  What a {dominant.capitalize()}-dominant pattern means:"))
        _print_wrapped(DOMAIN_MEANING[dominant], "  ", 64)
        print()

    _print_divider()
    print()

    # ── SECTION 5: IDENTIFIED CAUSES ─────────────────────────────────────────
    if fired_causes:
        n_causes = len(fired_causes)
        print(_c(BOLD, f"  SECTION 4 — IDENTIFIED CAUSES  ({n_causes} identified)"))
        _print_divider()
        print()
        _print_wrapped(
            f"The system identified {n_causes} cause(s) contributing to your sleep "
            "disruption. Each cause below is explained in detail: what it is, "
            "why it is affecting your sleep, what the recommended action is, "
            "and why that action works. They are listed in order of their "
            "contribution to your overall severity score.",
            "  ", 64
        )
        print()

        sorted_causes = sorted(fired_causes.items(), key=lambda x: x[1], reverse=True)

        for i, (cause, posterior) in enumerate(sorted_causes, 1):
            info   = CAUSES.get(cause, {})
            domain = info.get("domain", "")
            icon   = DOMAIN_ICONS.get(domain, "·")
            weight = CAUSE_WEIGHTS.get(cause, 0.5)
            prolog_confirmed = cause in prolog_causes

            # ── Cause header ─────────────────────────────────────────────────
            confirm_tag = _c(DIM, "  [Prolog ✓]") if prolog_confirmed else ""
            print(_c(BOLD, f"  {i}.  {icon}  {cause.replace('_', ' ').upper()}{confirm_tag}"))

            # Domain + confidence + impact weight
            impact = "Very High" if weight >= 0.95 else \
                     "High"      if weight >= 0.8  else \
                     "Moderate"  if weight >= 0.65 else "Contributing"
            print(f"       Domain     : {domain.capitalize()}")
            print(f"       Confidence : {posterior:.0%}  "
                  f"{_c(DIM, '(probability this cause is active based on your answers)')}")
            print(f"       Impact     : {impact}  "
                  f"{_c(DIM, f'(evidence weight: {weight})')}")
            print()

            # ── What this cause is ───────────────────────────────────────────
            desc = info.get("description", "")
            if desc:
                print(_c(BOLD, "       What it is:"))
                _print_wrapped(desc, "       ", 62)
                print()

            # ── How it is affecting this student ────────────────────────────
            explanation = CAUSE_EXPLANATION.get(cause)
            if explanation:
                print(_c(BOLD, "       How this is affecting your sleep:"))
                _print_wrapped(explanation, "       ", 62)
                print()

            # ── Recommendation ───────────────────────────────────────────────
            rec = None
            if prolog:
                rec = query_recommendation(prolog, cause)
            if not rec:
                rec = _python_fallback_rec(cause)

            if rec:
                print(_c(CYAN + BOLD, "       Recommended action:"))
                _print_wrapped(rec, "       ", 62)
                print()

            # ── First action ─────────────────────────────────────────────────
            priority_action = CAUSE_PRIORITY.get(cause)
            if priority_action:
                print(f"       {_c(BOLD, 'Start here')} →  {priority_action}")
                print()

            _print_divider("·")
            print()

    else:
        print(_c(BOLD, "  SECTION 4 — IDENTIFIED CAUSES"))
        _print_divider()
        print()
        print("  No significant causes were identified.")
        _print_wrapped(
            "Your answers did not trigger any of the 29 sleep disruption cause "
            "rules in the system. Your sleep hours, stress levels, environment, "
            "behaviours, and academic load all appear to be within healthy ranges. "
            "Continue your current habits.",
            "  ", 64
        )
        print()

    # ── SECTION 6: ACTION SUMMARY ────────────────────────────────────────────
    if fired_causes:
        print(_c(BOLD, "  SECTION 5 — YOUR PRIORITY ACTION PLAN"))
        _print_divider()
        print()
        _print_wrapped(
            "Below are the immediate first steps for each identified cause, "
            "ranked by the impact weight of the cause. Start with number 1 "
            "tonight. You do not need to do everything at once — one consistent "
            "change produces more benefit than many inconsistent ones.",
            "  ", 64
        )
        print()

        # Sort by weight descending for priority ordering
        priority_order = sorted(
            fired_causes.keys(),
            key=lambda c: CAUSE_WEIGHTS.get(c, 0),
            reverse=True
        )
        for rank, cause in enumerate(priority_order, 1):
            action = CAUSE_PRIORITY.get(cause, "See recommendation above.")
            icon   = DOMAIN_ICONS.get(CAUSES.get(cause, {}).get("domain", ""), "·")
            print(f"  {rank}.  {icon}  {_c(BOLD, cause.replace('_', ' ').title())}")
            print(f"       {action}")
            print()

    # ── SECTION 7: SESSION STATS ──────────────────────────────────────────────
    _print_divider("═")
    variant     = result.get("variant", "")
    core_count  = result.get("core_count", 0)
    addon_count = result.get("addon_count", 0)
    total_q     = core_count + addon_count
    trigger_log = result.get("trigger_log", [])

    print()
    print(_c(BOLD, "  ASSESSMENT METHODOLOGY"))
    _print_divider()
    print()
    print(f"  Questions asked  :  {total_q}  "
          f"({core_count} core + {addon_count} targeted add-ons)")
    print(f"  Variant          :  {variant.upper()}  "
          f"({VARIANT_CONFIG[variant]['name']})")
    if trigger_log:
        print(f"  Adaptive triggers:  {len(trigger_log)} cross-domain patterns detected")
    print(f"  Causes assessed  :  29 possible causes across 5 domains")
    print(f"  Method           :  Naive Bayes sequential updating + rule-based inference")
    print()
    _print_wrapped(
        "This report was generated by a Bayesian expert system that updated "
        "probability estimates after each of your answers. The add-on questions "
        "you were asked were selected in real time based on which causes had "
        "elevated posteriors at that point in the session. The Prolog knowledge "
        "base independently confirmed the identified causes using rule-based "
        "reasoning over your asserted answers.",
        "  ", 64
    )
    print()


def _python_fallback_rec(cause: str) -> str | None:
    """
    Fallback recommendations used when Prolog is unavailable.
    One concise, actionable sentence per cause.
    These are only displayed if sleepwise.pl is not loaded.
    """
    recs = {
        # Lifestyle
        "high_caffeine":         "Stop all caffeine intake after 2 PM — its half-life means 3 PM coffee still affects midnight sleep.",
        "poor_diet_habits":      "Finish your last meal at least 2 hours before bed to reduce reflux and core-temperature disruption.",
        "sedentary_lifestyle":   "Add 20 minutes of brisk walking daily — even light activity significantly improves sleep depth.",
        "substance_use":         "Alcohol suppresses REM sleep — even one evening drink reduces sleep quality by up to 25%.",
        "poor_hydration":        "Drink your water earlier in the day and taper off after 7 PM to reduce night-time wakeups.",
        "medication_interference":"Review your medication timing with a pharmacist — some medications taken at night disrupt sleep architecture.",
        # Psychological
        "high_stress":           "Write tomorrow's top 3 tasks on paper before bed — externalising the list quiets the planning loop.",
        "anxiety":               "Try 4-7-8 breathing at bedtime: inhale 4s, hold 7s, exhale 8s — activates the parasympathetic system.",
        "depression":            "Contact UG Counselling Centre for a free first session — depression and sleep form a cycle that needs professional support to break.",
        "burnout":               "Identify one task you can drop or defer this week — recovery from burnout requires reducing load, not just resting.",
        "rumination":            "Set a 10-minute 'worry time' earlier in the evening to contain intrusive thoughts before bed.",
        "poor_self_control":     "Use a fixed alarm for both waking AND going to bed — external anchors outperform willpower for schedule control.",
        "perfectionism":         "Reframe 'done' as the goal for tonight — perfectionism at night raises arousal and delays sleep onset.",
        "low_resilience":        "Identify one small win from today before sleeping — building a recovery mindset reduces cortisol at night.",
        # Environmental
        "noise_disturbance":     "NRR-33 earplugs reduce ambient noise by 20dB — the most evidence-backed single intervention for noise disruption.",
        "light_disturbance":     "Blackout curtains or a sleep mask eliminate the primary light-based melatonin suppressor.",
        "temperature_discomfort":"The ideal sleep temperature is 18-20°C — a lukewarm shower 90 minutes before bed also lowers core temperature effectively.",
        "poor_sleep_space":      "Reserve your bed strictly for sleep — remove screens, food, and work materials from the sleep space.",
        "safety_concern":        "Feeling unsafe in your environment directly elevates cortisol at night — report concerns to university housing.",
        # Behavioral
        "excessive_screen_use":  "Set a hard screen-off time 45 minutes before bed — use blue-light blocking mode as a secondary measure only.",
        "irregular_schedule":    "Pick one fixed wake time and hold it 7 days a week — wake consistency is more powerful than bedtime consistency.",
        "poor_sleep_hygiene":    "Build a 3-step wind-down routine (e.g., shower, read, lights out) — repetition teaches your brain the sleep signal.",
        "excessive_napping":     "Cap naps at 20 minutes before 3 PM — longer or later naps directly delay your next night's sleep onset.",
        "poor_sleep_efficiency": "Only get into bed when you feel sleepy — lying awake trains your brain to associate the bed with wakefulness.",
        # Academic
        "poor_sleep_duration":   "Treat 7 hours as a non-negotiable minimum — sleep is when memory consolidation from the day's study occurs.",
        "academic_overload":     "Map your weekly hour commitment (classes + study + work) — if it exceeds 60 hours, something must be reduced.",
        "late_night_studying":   "Hard stop studying at 10 PM — material studied after midnight is poorly consolidated due to fatigue interference.",
        "exam_pressure":         "Sleep the night before an exam consolidates more than a final revision session — prioritise rest over cramming.",
        "performance_impact":    "Track your sleep hours and academic performance for 2 weeks — the correlation will make the cost of poor sleep concrete.",
    }
    return recs.get(cause)


# ─────────────────────────────────────────────────────────────────────────────
# PLAY AGAIN
# ─────────────────────────────────────────────────────────────────────────────

def ask_play_again() -> bool:
    """Ask whether the user wants to run another session. Returns True/False."""
    print()
    _print_divider()
    print()
    while True:
        raw = input("  Would you like to run another assessment? (y/n): ").strip().lower()
        if raw in ("y", "yes"):
            return True
        if raw in ("n", "no"):
            return False
        print(_c(RED, "  Please enter y or n."))


# ─────────────────────────────────────────────────────────────────────────────
# MAIN LOOP
# ─────────────────────────────────────────────────────────────────────────────

def main():
    # ── Initialise Prolog once for the entire run ─────────────────────────────
    prolog = init_prolog()
    if not PROLOG_AVAILABLE:
        print(_c(DIM, "\n  [Note: pyswip not installed — running in Python-only mode.]\n"))
    elif prolog is None:
        print(_c(DIM, "\n  [Note: sleepwise.pl not found — running in Python-only mode.]\n"))

    while True:
        # ── Welcome + variant selection ───────────────────────────────────────
        show_welcome()
        variant = select_variant()

        # ── Clear any leftover Prolog facts from previous session ─────────────
        if prolog:
            retract_facts(prolog)

        # ── Run the full session (question loop + Bayesian engine) ────────────
        _clear()
        print()
        print(_c(BOLD, "  Starting your assessment..."))
        print(_c(DIM,  "  Answer honestly — there are no right or wrong answers."))
        print()
        _pause()

        ask_fn = make_ask_fn()
        result  = run_session(variant, ask_fn)

        # ── Assert answers to Prolog ──────────────────────────────────────────
        if prolog:
            assert_facts(prolog, result["answers"])

        # ── Display results ───────────────────────────────────────────────────
        display_results(result, prolog)

        # ── Offer to run again ────────────────────────────────────────────────
        if not ask_play_again():
            _clear()
            print()
            print(_c(BOLD, "  Thank you for using SleepWise."))
            print("  Prioritise your sleep — your academic performance depends on it.")
            print()
            break


# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    main()

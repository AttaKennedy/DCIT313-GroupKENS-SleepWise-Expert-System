
"""
test_knowledge_base.py
======================
SleepWise Expert System — Knowledge Base Test Suite
Group KENS | DCIT 313 | University of Ghana

Tests the SWI-Prolog knowledge base (sleepwise.pl) directly via pyswip.
Covers all 29 cause rules, 5 clinical flags, 4 severity levels,
6 sleep complaint types, and all 29 recommendation clauses.

Each test has a unique ID (TC-KB-XXX), a plain-English description,
the exact input facts asserted, and the expected Prolog result.

Run:
    python test_knowledge_base.py

Requirements:
    - SWI-Prolog installed and on PATH
    - pyswip installed  (pip install pyswip)
    - sleepwise.pl in ../knowledge_base/ relative to this file
"""

import sys
import os

# ── Path setup ────────────────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from pyswip import Prolog
except ImportError:
    print("\n  ERROR: pyswip is not installed.")
    print("  Run:  pip install pyswip\n")
    sys.exit(1)

# ── Locate sleepwise.pl ───────────────────────────────────────────────────────
PL_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "knowledge_base", "sleepwise.pl"
)
if not os.path.exists(PL_FILE):
    # fallback: same directory
    PL_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sleepwise.pl")

if not os.path.exists(PL_FILE):
    print(f"\n  ERROR: sleepwise.pl not found.\n  Looked at: {PL_FILE}\n")
    sys.exit(1)

# ── Prolog engine ─────────────────────────────────────────────────────────────
p = Prolog()
p.consult(PL_FILE)

# ── Counters ──────────────────────────────────────────────────────────────────
PASS = FAIL = 0
FAILED_TESTS = []


# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def reset():
    list(p.query("retractall(user_fact(_, _))"))

def facts(d: dict):
    reset()
    for qid, val in d.items():
        p.assertz(f"user_fact({qid}, {val})")

def causes() -> set:
    return {str(r["C"]) for r in p.query("sleep_cause(C)")}

def severity() -> str:
    r = list(p.query("sleep_severity(S)"))
    return str(r[0]["S"]) if r else "none"

def complaints() -> set:
    return {str(r["C"]) for r in p.query("sleep_complaint(C)")}

def flags() -> list:
    return [(str(r["Id"]), str(r["L"])) for r in p.query("sleep_clinical_flag(Id, L)")]

def flag_ids() -> set:
    return {fid for fid, _ in flags()}

def has_rec(cause: str) -> bool:
    return bool(list(p.query(f"recommendation({cause}, _)")))


def run(tc_id: str, description: str, result: bool, detail: str = ""):
    global PASS, FAIL
    if result:
        PASS += 1
        print(f"  PASS  [{tc_id}]  {description}")
    else:
        FAIL += 1
        marker = f"  FAIL  [{tc_id}]  {description}"
        if detail:
            marker += f"\n          → {detail}"
        print(marker)
        FAILED_TESTS.append(tc_id)


def section(title: str):
    print()
    print(f"  {'─' * 66}")
    print(f"  {title}")
    print(f"  {'─' * 66}")


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — CAUSE RULES: POSITIVE CASES
# Every cause must fire when its primary triggering fact is asserted.
# ═══════════════════════════════════════════════════════════════════════════════
section("SECTION 1 — Cause Rules: Positive Cases (cause fires on correct evidence)")

# ── Lifestyle ─────────────────────────────────────────────────────────────────
facts({"caffeine_intake": "high"})
run("TC-KB-001", "high_caffeine fires on caffeine_intake=high",
    "high_caffeine" in causes())

facts({"caffeine_intake": "medium"})
run("TC-KB-002", "high_caffeine fires on caffeine_intake=medium",
    "high_caffeine" in causes())

facts({"heavy_meal_before_bed": "often"})
run("TC-KB-003", "poor_diet_habits fires on heavy_meal_before_bed=often",
    "poor_diet_habits" in causes())

facts({"heavy_meal_before_bed": "always"})
run("TC-KB-004", "poor_diet_habits fires on heavy_meal_before_bed=always",
    "poor_diet_habits" in causes())

facts({"physical_activity_level": "none"})
run("TC-KB-005", "sedentary_lifestyle fires on physical_activity_level=none",
    "sedentary_lifestyle" in causes())

facts({"physical_activity_level": "low"})
run("TC-KB-006", "sedentary_lifestyle fires on physical_activity_level=low",
    "sedentary_lifestyle" in causes())

facts({"alcohol_consumption": "often"})
run("TC-KB-007", "substance_use fires on alcohol_consumption=often",
    "substance_use" in causes())

facts({"alcohol_consumption": "daily"})
run("TC-KB-008", "substance_use fires on alcohol_consumption=daily",
    "substance_use" in causes())

facts({"recreational_drug_use": "often"})
run("TC-KB-009", "substance_use fires on recreational_drug_use=often",
    "substance_use" in causes())

facts({"recreational_drug_use": "frequently"})
run("TC-KB-010", "substance_use fires on recreational_drug_use=frequently",
    "substance_use" in causes())

facts({"fluid_intake_timing": "late"})
run("TC-KB-011", "poor_hydration fires on fluid_intake_timing=late",
    "poor_hydration" in causes())

facts({"fluid_intake_timing": "in_bed"})
run("TC-KB-012", "poor_hydration fires on fluid_intake_timing=in_bed",
    "poor_hydration" in causes())

facts({"medication_supplements": "daily_nonrx"})
run("TC-KB-013", "medication_interference fires on medication_supplements=daily_nonrx",
    "medication_interference" in causes())

facts({"medication_supplements": "daily_rx"})
run("TC-KB-014", "medication_interference fires on medication_supplements=daily_rx",
    "medication_interference" in causes())

# ── Psychological ─────────────────────────────────────────────────────────────
facts({"stress_level": "high"})
run("TC-KB-015", "high_stress fires on stress_level=high",
    "high_stress" in causes())

facts({"anxiety_levels": "often"})
run("TC-KB-016", "anxiety fires on anxiety_levels=often",
    "anxiety" in causes())

facts({"anxiety_levels": "every_night"})
run("TC-KB-017", "anxiety fires on anxiety_levels=every_night",
    "anxiety" in causes())

facts({"panic_attacks": "often"})
run("TC-KB-018", "anxiety fires on panic_attacks=often",
    "anxiety" in causes())

facts({"panic_attacks": "frequently"})
run("TC-KB-019", "anxiety fires on panic_attacks=frequently",
    "anxiety" in causes())

facts({"depression_symptoms": "often"})
run("TC-KB-020", "depression fires on depression_symptoms=often",
    "depression" in causes())

facts({"depression_symptoms": "every_day"})
run("TC-KB-021", "depression fires on depression_symptoms=every_day",
    "depression" in causes())

facts({"burnout_feelings": "often"})
run("TC-KB-022", "burnout fires on burnout_feelings=often",
    "burnout" in causes())

facts({"burnout_feelings": "constantly"})
run("TC-KB-023", "burnout fires on burnout_feelings=constantly",
    "burnout" in causes())

facts({"rumination_habits": "often"})
run("TC-KB-024", "rumination fires on rumination_habits=often",
    "rumination" in causes())

facts({"rumination_habits": "always"})
run("TC-KB-025", "rumination fires on rumination_habits=always",
    "rumination" in causes())

facts({"worry_before_bed": "often"})
run("TC-KB-026", "rumination fires on worry_before_bed=often",
    "rumination" in causes())

facts({"worry_before_bed": "always"})
run("TC-KB-027", "rumination fires on worry_before_bed=always",
    "rumination" in causes())

facts({"consistent_sleep_time": "inconsistent"})
run("TC-KB-028", "poor_self_control fires on consistent_sleep_time=inconsistent",
    "poor_self_control" in causes())

facts({"adhd_symptoms": "moderate"})
run("TC-KB-029", "poor_self_control fires on adhd_symptoms=moderate",
    "poor_self_control" in causes())

facts({"adhd_symptoms": "severe"})
run("TC-KB-030", "poor_self_control fires on adhd_symptoms=severe",
    "poor_self_control" in causes())

facts({"perfectionism_tendencies": "often"})
run("TC-KB-031", "perfectionism fires on perfectionism_tendencies=often",
    "perfectionism" in causes())

facts({"perfectionism_tendencies": "always"})
run("TC-KB-032", "perfectionism fires on perfectionism_tendencies=always",
    "perfectionism" in causes())

facts({"resilience_level": "poorly"})
run("TC-KB-033", "low_resilience fires on resilience_level=poorly",
    "low_resilience" in causes())

facts({"resilience_level": "very_poorly"})
run("TC-KB-034", "low_resilience fires on resilience_level=very_poorly",
    "low_resilience" in causes())

# ── Environmental ─────────────────────────────────────────────────────────────
facts({"noisy_environment": "loud"})
run("TC-KB-035", "noise_disturbance fires on noisy_environment=loud",
    "noise_disturbance" in causes())

facts({"partner_snoring": "often"})
run("TC-KB-036", "noise_disturbance fires on partner_snoring=often",
    "noise_disturbance" in causes())

facts({"partner_snoring": "always"})
run("TC-KB-037", "noise_disturbance fires on partner_snoring=always",
    "noise_disturbance" in causes())

facts({"light_exposure_at_night": "often"})
run("TC-KB-038", "light_disturbance fires on light_exposure_at_night=often",
    "light_disturbance" in causes())

facts({"light_exposure_at_night": "always"})
run("TC-KB-039", "light_disturbance fires on light_exposure_at_night=always",
    "light_disturbance" in causes())

facts({"electronic_devices_in_room": "several"})
run("TC-KB-040", "light_disturbance fires on electronic_devices_in_room=several",
    "light_disturbance" in causes())

facts({"electronic_devices_in_room": "many"})
run("TC-KB-041", "light_disturbance fires on electronic_devices_in_room=many",
    "light_disturbance" in causes())

facts({"uncomfortable_temperature": "too_hot"})
run("TC-KB-042", "temperature_discomfort fires on uncomfortable_temperature=too_hot",
    "temperature_discomfort" in causes())

facts({"uncomfortable_temperature": "too_cold"})
run("TC-KB-043", "temperature_discomfort fires on uncomfortable_temperature=too_cold",
    "temperature_discomfort" in causes())

facts({"room_clutter": "high"})
run("TC-KB-044", "poor_sleep_space fires on room_clutter=high",
    "poor_sleep_space" in causes())

facts({"bed_comfort": "uncomfortable"})
run("TC-KB-045", "poor_sleep_space fires on bed_comfort=uncomfortable",
    "poor_sleep_space" in causes())

facts({"neighborhood_safety": "moderate"})
run("TC-KB-046", "safety_concern fires on neighborhood_safety=moderate",
    "safety_concern" in causes())

facts({"neighborhood_safety": "very_concerned"})
run("TC-KB-047", "safety_concern fires on neighborhood_safety=very_concerned",
    "safety_concern" in causes())

# ── Behavioral ────────────────────────────────────────────────────────────────
facts({"screen_before_bed": "often"})
run("TC-KB-048", "excessive_screen_use fires on screen_before_bed=often",
    "excessive_screen_use" in causes())

facts({"screen_before_bed": "always"})
run("TC-KB-049", "excessive_screen_use fires on screen_before_bed=always",
    "excessive_screen_use" in causes())

facts({"social_media_use_at_night": "moderate"})
run("TC-KB-050", "excessive_screen_use fires on social_media_use_at_night=moderate",
    "excessive_screen_use" in causes())

facts({"social_media_use_at_night": "long"})
run("TC-KB-051", "excessive_screen_use fires on social_media_use_at_night=long",
    "excessive_screen_use" in causes())

facts({"consistent_sleep_time": "inconsistent"})
run("TC-KB-052", "irregular_schedule fires on consistent_sleep_time=inconsistent",
    "irregular_schedule" in causes())

facts({"weekend_sleep_catchup": "much_more"})
run("TC-KB-053", "irregular_schedule fires on weekend_sleep_catchup=much_more",
    "irregular_schedule" in causes())

facts({"weekend_sleep_catchup": "far_more"})
run("TC-KB-054", "irregular_schedule fires on weekend_sleep_catchup=far_more",
    "irregular_schedule" in causes())

facts({"bedtime_routine_consistency": "rarely"})
run("TC-KB-055", "poor_sleep_hygiene fires on bedtime_routine_consistency=rarely",
    "poor_sleep_hygiene" in causes())

facts({"bedtime_routine_consistency": "no"})
run("TC-KB-056", "poor_sleep_hygiene fires on bedtime_routine_consistency=no",
    "poor_sleep_hygiene" in causes())

facts({"daytime_nap_hours": "moderate"})
run("TC-KB-057", "excessive_napping fires on daytime_nap_hours=moderate",
    "excessive_napping" in causes())

facts({"daytime_nap_hours": "long"})
run("TC-KB-058", "excessive_napping fires on daytime_nap_hours=long",
    "excessive_napping" in causes())

facts({"sleep_latency": "slow"})
run("TC-KB-059", "poor_sleep_efficiency fires on sleep_latency=slow",
    "poor_sleep_efficiency" in causes())

facts({"sleep_latency": "very_slow"})
run("TC-KB-060", "poor_sleep_efficiency fires on sleep_latency=very_slow",
    "poor_sleep_efficiency" in causes())

facts({"frequent_wakeups": "several"})
run("TC-KB-061", "poor_sleep_efficiency fires on frequent_wakeups=several",
    "poor_sleep_efficiency" in causes())

facts({"frequent_wakeups": "many"})
run("TC-KB-062", "poor_sleep_efficiency fires on frequent_wakeups=many",
    "poor_sleep_efficiency" in causes())

facts({"sleep_disorders": "suspected"})
run("TC-KB-063", "poor_sleep_efficiency fires on sleep_disorders=suspected",
    "poor_sleep_efficiency" in causes())

facts({"sleep_disorders": "diagnosed_mild"})
run("TC-KB-064", "poor_sleep_efficiency fires on sleep_disorders=diagnosed_mild",
    "poor_sleep_efficiency" in causes())

facts({"sleep_disorders": "diagnosed_severe"})
run("TC-KB-065", "poor_sleep_efficiency fires on sleep_disorders=diagnosed_severe",
    "poor_sleep_efficiency" in causes())

# ── Academic ──────────────────────────────────────────────────────────────────
facts({"sleep_hours": "less_than_4"})
run("TC-KB-066", "poor_sleep_duration fires on sleep_hours=less_than_4",
    "poor_sleep_duration" in causes())

facts({"sleep_hours": "four_to_six"})
run("TC-KB-067", "poor_sleep_duration fires on sleep_hours=four_to_six",
    "poor_sleep_duration" in causes())

facts({"academic_workload": "heavy"})
run("TC-KB-068", "academic_overload fires on academic_workload=heavy",
    "academic_overload" in causes())

facts({"employment_status": "part_time"})
run("TC-KB-069", "academic_overload fires on employment_status=part_time",
    "academic_overload" in causes())

facts({"employment_status": "full_time"})
run("TC-KB-070", "academic_overload fires on employment_status=full_time",
    "academic_overload" in causes())

facts({"study_past_midnight": "often"})
run("TC-KB-071", "late_night_studying fires on study_past_midnight=often",
    "late_night_studying" in causes())

facts({"study_past_midnight": "always"})
run("TC-KB-072", "late_night_studying fires on study_past_midnight=always",
    "late_night_studying" in causes())

facts({"exam_preparation_style": "often"})
run("TC-KB-073", "late_night_studying fires on exam_preparation_style=often",
    "late_night_studying" in causes())

facts({"exam_preparation_style": "always"})
run("TC-KB-074", "late_night_studying fires on exam_preparation_style=always",
    "late_night_studying" in causes())

facts({"exam_period": "yes"})
run("TC-KB-075", "exam_pressure fires on exam_period=yes",
    "exam_pressure" in causes())

facts({"academic_pressure_peers_family": "moderate"})
run("TC-KB-076", "exam_pressure fires on academic_pressure_peers_family=moderate",
    "exam_pressure" in causes())

facts({"academic_pressure_peers_family": "high"})
run("TC-KB-077", "exam_pressure fires on academic_pressure_peers_family=high",
    "exam_pressure" in causes())

facts({"performance_impact": "often"})
run("TC-KB-078", "performance_impact fires on performance_impact=often",
    "performance_impact" in causes())

facts({"performance_impact": "every_day"})
run("TC-KB-079", "performance_impact fires on performance_impact=every_day",
    "performance_impact" in causes())

facts({"lecture_attendance": "never"})
run("TC-KB-080", "performance_impact fires on lecture_attendance=never (poor attendance)",
    "performance_impact" in causes())

facts({"lecture_attendance": "rarely"})
run("TC-KB-081", "performance_impact fires on lecture_attendance=rarely (poor attendance)",
    "performance_impact" in causes())


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — CAUSE RULES: NEGATIVE CASES
# No cause should fire on healthy/below-threshold values.
# ═══════════════════════════════════════════════════════════════════════════════
section("SECTION 2 — Cause Rules: Negative Cases (healthy values produce no cause)")

facts({"caffeine_intake": "none"})
run("TC-KB-082", "high_caffeine silent on caffeine_intake=none",
    "high_caffeine" not in causes())

facts({"caffeine_intake": "low"})
run("TC-KB-083", "high_caffeine silent on caffeine_intake=low",
    "high_caffeine" not in causes())

facts({"physical_activity_level": "moderate"})
run("TC-KB-084", "sedentary_lifestyle silent on physical_activity_level=moderate",
    "sedentary_lifestyle" not in causes())

facts({"physical_activity_level": "high"})
run("TC-KB-085", "sedentary_lifestyle silent on physical_activity_level=high",
    "sedentary_lifestyle" not in causes())

facts({"alcohol_consumption": "never"})
run("TC-KB-086", "substance_use silent on alcohol_consumption=never",
    "substance_use" not in causes())

facts({"alcohol_consumption": "rarely"})
run("TC-KB-087", "substance_use silent on alcohol_consumption=rarely",
    "substance_use" not in causes())

facts({"recreational_drug_use": "never"})
run("TC-KB-088", "substance_use silent on recreational_drug_use=never",
    "substance_use" not in causes())

facts({"recreational_drug_use": "rarely"})
run("TC-KB-089", "substance_use silent on recreational_drug_use=rarely",
    "substance_use" not in causes())

facts({"stress_level": "low"})
run("TC-KB-090", "high_stress silent on stress_level=low",
    "high_stress" not in causes())

facts({"stress_level": "medium"})
run("TC-KB-091", "high_stress silent on stress_level=medium",
    "high_stress" not in causes())

facts({"anxiety_levels": "never"})
run("TC-KB-092", "anxiety silent on anxiety_levels=never",
    "anxiety" not in causes())

facts({"anxiety_levels": "rarely"})
run("TC-KB-093", "anxiety silent on anxiety_levels=rarely",
    "anxiety" not in causes())

facts({"depression_symptoms": "never"})
run("TC-KB-094", "depression silent on depression_symptoms=never",
    "depression" not in causes())

facts({"depression_symptoms": "rarely"})
run("TC-KB-095", "depression silent on depression_symptoms=rarely",
    "depression" not in causes())

facts({"burnout_feelings": "never"})
run("TC-KB-096", "burnout silent on burnout_feelings=never",
    "burnout" not in causes())

facts({"burnout_feelings": "rarely"})
run("TC-KB-097", "burnout silent on burnout_feelings=rarely",
    "burnout" not in causes())

facts({"adhd_symptoms": "no"})
run("TC-KB-098", "poor_self_control silent on adhd_symptoms=no",
    "poor_self_control" not in causes())

facts({"adhd_symptoms": "mild"})
run("TC-KB-099", "poor_self_control silent on adhd_symptoms=mild",
    "poor_self_control" not in causes())

facts({"consistent_sleep_time": "very_consistent"})
run("TC-KB-100", "irregular_schedule and poor_self_control silent on consistent_sleep_time=very_consistent",
    "irregular_schedule" not in causes() and "poor_self_control" not in causes())

facts({"weekend_sleep_catchup": "same"})
run("TC-KB-101", "irregular_schedule silent on weekend_sleep_catchup=same",
    "irregular_schedule" not in causes())

facts({"weekend_sleep_catchup": "slightly_more"})
run("TC-KB-102", "irregular_schedule silent on weekend_sleep_catchup=slightly_more",
    "irregular_schedule" not in causes())

facts({"noisy_environment": "quiet"})
run("TC-KB-103", "noise_disturbance silent on noisy_environment=quiet",
    "noise_disturbance" not in causes())

facts({"noisy_environment": "some_noise"})
run("TC-KB-104", "noise_disturbance silent on noisy_environment=some_noise",
    "noise_disturbance" not in causes())

facts({"light_exposure_at_night": "never"})
run("TC-KB-105", "light_disturbance silent on light_exposure_at_night=never",
    "light_disturbance" not in causes())

facts({"uncomfortable_temperature": "comfortable"})
run("TC-KB-106", "temperature_discomfort silent on uncomfortable_temperature=comfortable",
    "temperature_discomfort" not in causes())

facts({"sleep_latency": "fast"})
run("TC-KB-107", "poor_sleep_efficiency silent on sleep_latency=fast",
    "poor_sleep_efficiency" not in causes())

facts({"sleep_latency": "normal"})
run("TC-KB-108", "poor_sleep_efficiency silent on sleep_latency=normal",
    "poor_sleep_efficiency" not in causes())

facts({"frequent_wakeups": "none"})
run("TC-KB-109", "poor_sleep_efficiency silent on frequent_wakeups=none",
    "poor_sleep_efficiency" not in causes())

facts({"frequent_wakeups": "few"})
run("TC-KB-110", "poor_sleep_efficiency silent on frequent_wakeups=few",
    "poor_sleep_efficiency" not in causes())

facts({"sleep_disorders": "no"})
run("TC-KB-111", "poor_sleep_efficiency silent on sleep_disorders=no",
    "poor_sleep_efficiency" not in causes())

facts({"sleep_hours": "six_to_eight"})
run("TC-KB-112", "poor_sleep_duration silent on sleep_hours=six_to_eight",
    "poor_sleep_duration" not in causes())

facts({"sleep_hours": "more_than_8"})
run("TC-KB-113", "poor_sleep_duration silent on sleep_hours=more_than_8",
    "poor_sleep_duration" not in causes())

facts({"exam_period": "no"})
run("TC-KB-114", "exam_pressure silent on exam_period=no",
    "exam_pressure" not in causes())

facts({"academic_pressure_peers_family": "none"})
run("TC-KB-115", "exam_pressure silent on academic_pressure_peers_family=none",
    "exam_pressure" not in causes())

facts({"academic_pressure_peers_family": "mild"})
run("TC-KB-116", "exam_pressure silent on academic_pressure_peers_family=mild",
    "exam_pressure" not in causes())

facts({"performance_impact": "never"})
run("TC-KB-117", "performance_impact silent on performance_impact=never",
    "performance_impact" not in causes())

facts({"lecture_attendance": "often"})
run("TC-KB-118", "performance_impact silent on lecture_attendance=often (healthy)",
    "performance_impact" not in causes())

facts({"lecture_attendance": "frequently"})
run("TC-KB-119", "performance_impact silent on lecture_attendance=frequently (healthy)",
    "performance_impact" not in causes())


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — SEVERITY LEVELS
# ═══════════════════════════════════════════════════════════════════════════════
section("SECTION 3 — Severity Levels")

reset()
run("TC-KB-120", "Severity=none when no facts asserted",
    severity() == "none")

facts({"caffeine_intake": "high"})
run("TC-KB-121", "Severity=mild with one low-weight cause",
    severity() == "mild",
    f"got={severity()}")

facts({"sleep_hours": "four_to_six"})
run("TC-KB-122", "Severity=moderate with short sleep (anchor cause)",
    severity() in ("mild", "moderate"),
    f"got={severity()}")

facts({"depression_symptoms": "every_day", "sleep_hours": "less_than_4"})
run("TC-KB-123", "Severity=severe with depression+critical sleep deprivation",
    severity() == "severe",
    f"got={severity()}")

facts({"sleep_disorders": "diagnosed_severe"})
run("TC-KB-124", "Severity=severe with diagnosed severe sleep disorder",
    severity() == "severe",
    f"got={severity()}")

facts({
    "stress_level":          "high",
    "sleep_hours":           "less_than_4",
    "depression_symptoms":   "every_day",
    "anxiety_levels":        "every_night",
    "screen_before_bed":     "always",
    "academic_workload":     "heavy",
})
run("TC-KB-125", "Severity=severe with 4+ concurrent causes",
    severity() == "severe",
    f"got={severity()}")


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — CLINICAL FLAGS
# ═══════════════════════════════════════════════════════════════════════════════
section("SECTION 4 — Clinical Flags: Positive Cases")

# CF1 — Depression + critical sleep deprivation
facts({"depression_symptoms": "every_day", "sleep_hours": "less_than_4"})
run("TC-KB-126", "CF1 fires on depression=every_day + sleep_hours=less_than_4",
    "CF1" in flag_ids())

facts({"depression_symptoms": "often", "sleep_hours": "less_than_4"})
run("TC-KB-127", "CF1 fires on depression=often + sleep_hours=less_than_4",
    "CF1" in flag_ids())

# CF1 — negative: one condition missing
facts({"depression_symptoms": "every_day", "sleep_hours": "six_to_eight"})
run("TC-KB-128", "CF1 does NOT fire when sleep_hours=six_to_eight (missing condition)",
    "CF1" not in flag_ids())

facts({"depression_symptoms": "rarely", "sleep_hours": "less_than_4"})
run("TC-KB-129", "CF1 does NOT fire when depression=rarely (below threshold)",
    "CF1" not in flag_ids())

# CF2 — Anxiety every night + panic attacks
facts({"anxiety_levels": "every_night", "panic_attacks": "often"})
run("TC-KB-130", "CF2 fires on anxiety=every_night + panic_attacks=often",
    "CF2" in flag_ids())

facts({"anxiety_levels": "every_night", "panic_attacks": "frequently"})
run("TC-KB-131", "CF2 fires on anxiety=every_night + panic_attacks=frequently",
    "CF2" in flag_ids())

# CF2 — negative
facts({"anxiety_levels": "often", "panic_attacks": "frequently"})
run("TC-KB-132", "CF2 does NOT fire when anxiety=often (not every_night)",
    "CF2" not in flag_ids())

facts({"anxiety_levels": "every_night", "panic_attacks": "rarely"})
run("TC-KB-133", "CF2 does NOT fire when panic_attacks=rarely",
    "CF2" not in flag_ids())

# CF3 — Diagnosed severe sleep disorder
facts({"sleep_disorders": "diagnosed_severe"})
run("TC-KB-134", "CF3 fires on sleep_disorders=diagnosed_severe",
    "CF3" in flag_ids())

# CF3 — negative
facts({"sleep_disorders": "diagnosed_mild"})
run("TC-KB-135", "CF3 does NOT fire on sleep_disorders=diagnosed_mild",
    "CF3" not in flag_ids())

facts({"sleep_disorders": "suspected"})
run("TC-KB-136", "CF3 does NOT fire on sleep_disorders=suspected",
    "CF3" not in flag_ids())

facts({"sleep_disorders": "no"})
run("TC-KB-137", "CF3 does NOT fire on sleep_disorders=no",
    "CF3" not in flag_ids())

# CF4 — Burnout constantly + depression
facts({"burnout_feelings": "constantly", "depression_symptoms": "often"})
run("TC-KB-138", "CF4 fires on burnout=constantly + depression=often",
    "CF4" in flag_ids())

facts({"burnout_feelings": "constantly", "depression_symptoms": "every_day"})
run("TC-KB-139", "CF4 fires on burnout=constantly + depression=every_day",
    "CF4" in flag_ids())

# CF4 — negative
facts({"burnout_feelings": "constantly", "depression_symptoms": "never"})
run("TC-KB-140", "CF4 does NOT fire when depression=never",
    "CF4" not in flag_ids())

facts({"burnout_feelings": "often", "depression_symptoms": "every_day"})
run("TC-KB-141", "CF4 does NOT fire when burnout=often (not constantly)",
    "CF4" not in flag_ids())

# CF5 — Triple overload
facts({
    "depression_symptoms": "often",
    "anxiety_levels":      "often",
    "sleep_hours":         "less_than_4",
})
run("TC-KB-142", "CF5 fires on depression + anxiety + sleep_hours=less_than_4",
    "CF5" in flag_ids())

facts({
    "depression_symptoms": "every_day",
    "anxiety_levels":      "every_night",
    "sleep_hours":         "four_to_six",
})
run("TC-KB-143", "CF5 fires on depression + anxiety + sleep_hours=four_to_six",
    "CF5" in flag_ids())

# CF5 — negative: missing one of three conditions
facts({
    "depression_symptoms": "often",
    "anxiety_levels":      "often",
    "sleep_hours":         "six_to_eight",
})
run("TC-KB-144", "CF5 does NOT fire when sleep_hours=six_to_eight",
    "CF5" not in flag_ids())

facts({
    "depression_symptoms": "rarely",
    "anxiety_levels":      "often",
    "sleep_hours":         "less_than_4",
})
run("TC-KB-145", "CF5 does NOT fire when depression=rarely",
    "CF5" not in flag_ids())


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — SLEEP COMPLAINTS
# ═══════════════════════════════════════════════════════════════════════════════
section("SECTION 5 — Sleep Complaint Classification")

facts({"sleep_hours": "less_than_4"})
run("TC-KB-146", "sleep_deprivation complaint fires on sleep_hours=less_than_4",
    "sleep_deprivation" in complaints())

facts({"sleep_hours": "four_to_six"})
run("TC-KB-147", "sleep_deprivation complaint fires on sleep_hours=four_to_six",
    "sleep_deprivation" in complaints())

facts({"sleep_latency": "very_slow"})
run("TC-KB-148", "insomnia complaint fires on sleep_latency=very_slow",
    "insomnia" in complaints())

facts({"sleep_latency": "slow"})
run("TC-KB-149", "insomnia complaint fires on sleep_latency=slow",
    "insomnia" in complaints())

facts({"frequent_wakeups": "several"})
run("TC-KB-150", "maintenance_insomnia complaint fires on frequent_wakeups=several",
    "maintenance_insomnia" in complaints())

facts({"frequent_wakeups": "many"})
run("TC-KB-151", "maintenance_insomnia complaint fires on frequent_wakeups=many",
    "maintenance_insomnia" in complaints())

facts({
    "daytime_nap_hours":  "long",
    "morning_sleepiness": "extremely_tired",
})
run("TC-KB-152", "hypersomnia complaint fires on long naps + extreme morning sleepiness",
    "hypersomnia" in complaints())

facts({
    "consistent_sleep_time": "inconsistent",
    "screen_before_bed":     "always",
})
run("TC-KB-153", "circadian_disruption complaint fires on inconsistent schedule + screen use",
    "circadian_disruption" in complaints())

facts({
    "stress_level":  "high",
    "sleep_latency": "very_slow",
})
run("TC-KB-154", "stress_related_insomnia complaint fires on high stress + slow onset",
    "stress_related_insomnia" in complaints())

facts({"sleep_hours": "six_to_eight"})
run("TC-KB-155", "No sleep complaint fires on healthy sleep hours",
    "sleep_deprivation" not in complaints())


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 6 — RECOMMENDATIONS
# Every cause must have exactly one recommendation clause.
# ═══════════════════════════════════════════════════════════════════════════════
section("SECTION 6 — Recommendations: all 29 causes have recommendation clauses")

reset()
ALL_CAUSES = [
    "high_caffeine", "poor_diet_habits", "sedentary_lifestyle", "substance_use",
    "poor_hydration", "medication_interference", "high_stress", "anxiety",
    "depression", "burnout", "rumination", "poor_self_control", "perfectionism",
    "low_resilience", "noise_disturbance", "light_disturbance",
    "temperature_discomfort", "poor_sleep_space", "safety_concern",
    "excessive_screen_use", "irregular_schedule", "poor_sleep_hygiene",
    "excessive_napping", "poor_sleep_efficiency", "poor_sleep_duration",
    "academic_overload", "late_night_studying", "exam_pressure",
    "performance_impact",
]

tc_num = 156
for cause in ALL_CAUSES:
    run(f"TC-KB-{tc_num:03d}", f"recommendation exists for {cause}",
        has_rec(cause))
    tc_num += 1


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 7 — RESET AND ISOLATION
# ═══════════════════════════════════════════════════════════════════════════════
section("SECTION 7 — Session Reset and Isolation")

facts({"stress_level": "high", "sleep_hours": "less_than_4", "depression_symptoms": "every_day"})
before = causes()
run("TC-KB-185", "Causes fire before reset",
    len(before) > 0)

list(p.query("reset_session"))
after_facts = list(p.query("user_fact(_, _)"))
run("TC-KB-186", "reset_session removes all user_fact clauses",
    len(after_facts) == 0)

after_causes = causes()
run("TC-KB-187", "No causes fire after reset_session",
    len(after_causes) == 0)

after_severity = severity()
run("TC-KB-188", "Severity=none after reset_session",
    after_severity == "none")

# Session isolation: facts from one session do not bleed into next
facts({"caffeine_intake": "high"})
reset()
facts({"screen_before_bed": "always"})
c = causes()
run("TC-KB-189", "Previous session facts do not bleed into new session",
    "high_caffeine" not in c)


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
    print(f"  Failed test IDs:")
    for tc in FAILED_TESTS:
        print(f"    ✗  {tc}")

print()
sys.exit(0 if FAIL == 0 else 1)
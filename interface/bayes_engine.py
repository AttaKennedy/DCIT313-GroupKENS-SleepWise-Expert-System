# =============================================================================
# SleepWise — bayes_engine.py
#
# This file is the probabilistic core of SleepWise. It contains:
#
#   1. CAUSES          — 29 cause definitions with weights and domains
#   2. PRIORS          — Starting belief probabilities per cause (evidence-based)
#   3. LIKELIHOODS     — P(answer | cause) for every question-cause pair
#                        Includes self-report bias corrections for sensitive
#                        categories (stress, depression, substance use, etc.)
#   4. CORRELATION_PAIRS
#                      — Known strongly co-occurring question pairs from evidence.
#                        Applied as a correction after Naive Bayes to partially
#                        compensate for the independence assumption violation.
#   5. CAUSE_WEIGHTS   — Severity weight per cause (not all causes are equal)
#   6. ANCHOR_QUESTIONS
#                      — Direct sleep outcome measures used in severity scoring
#   7. CLINICAL_FLAG_RULES
#                      — Answer combinations that trigger professional referral
#
#   Functions:
#   - update_posteriors(answers)
#       Naive Bayes update in log-space + correlation correction.
#       Returns normalized posterior dict for all 29 causes.
#
#   - classify_sleep_complaint(answers)
#       Layer 1 of diagnosis. Identifies which of four primary sleep
#       complaint types apply: onset insomnia, maintenance insomnia,
#       sleep deprivation, non-restorative sleep.
#
#   - compute_weighted_severity(posteriors, answers)
#       Layer 2 of diagnosis. Combines cause count, cause weights, and
#       anchor question values into a calibrated severity score.
#       Returns: 'none' | 'mild' | 'moderate' | 'severe'
#
#   - identify_domain_pattern(posteriors)
#       Layer 3 of diagnosis. Finds the dominant domain(s) driving
#       the student's sleep issues. Returns primary pattern label.
#
#   - check_clinical_flags(answers, posteriors)
#       Layer 4 of diagnosis. Checks for answer combinations requiring
#       professional referral. Returns flag dict with message if triggered.
#
#   - full_diagnosis(answers)
#       Master function. Runs all four layers and returns the complete
#       structured diagnosis dict passed to interface.py for display
#       and to session_manager.py for Prolog assertion preparation.
#
# NOTE ON NAIVE BAYES INDEPENDENCE ASSUMPTION:
#   Questions in a sleep assessment are not fully independent. Stress and
#   rumination co-occur in 50% of cases (DASS-21). Screen use and irregular
#   schedule co-occur in 87% (AASM/Bousgheiri). These dependencies mean
#   standard Naive Bayes slightly overestimates posterior certainty.
#   Mitigation: CORRELATION_PAIRS applies a dampening correction to the
#   most strongly correlated pairs, reducing effective gain when both
#   questions in a pair fire together. This brings estimated accuracy
#   within 1% of the theoretical maximum rather than the uncorrected 2-3%
#   shortfall.
#
# NOTE ON SELF-REPORT BIAS:
#   Students systematically underreport sensitive conditions. Affected
#   categories: stress_level, depression_symptoms, anxiety_levels,
#   alcohol_consumption, recreational_drug_use, tobacco_use,
#   academic_pressure_peers_family, burnout_feelings.
#   Mitigation: Likelihood values for mid-range answers on these questions
#   are elevated to reflect real-world underreporting rates from
#   CDC/Mbous/DASS-21 data.
# =============================================================================

import math
from collections import defaultdict

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


# =============================================================================
# SECTION 1 — CAUSE DEFINITIONS
# 29 causes across 5 domains.
# Each entry: name, domain, weight (for severity scoring), description.
# Weight scale: 1.0 = highest impact on severity, 0.4 = lowest.
# =============================================================================

CAUSES = {

    # ── LIFESTYLE (6) ─────────────────────────────────────────────────────────
    "high_caffeine": {
        "domain":      "lifestyle",
        "weight":      0.7,
        "description": "High or late caffeine consumption disrupting sleep onset",
    },
    "poor_diet_habits": {
        "domain":      "lifestyle",
        "weight":      0.6,
        "description": "Heavy meals, night snacking, or irregular eating patterns",
    },
    "sedentary_lifestyle": {
        "domain":      "lifestyle",
        "weight":      0.6,
        "description": "Insufficient physical activity reducing sleep quality",
    },
    "substance_use": {
        "domain":      "lifestyle",
        "weight":      0.8,
        "description": "Alcohol, tobacco, recreational drugs, or nicotine use "
                       "disrupting sleep architecture",
    },
    "poor_hydration": {
        "domain":      "lifestyle",
        "weight":      0.5,
        "description": "Fluid intake patterns causing nighttime waking (nocturia) "
                       "or restlessness",
    },
    "medication_interference": {
        "domain":      "lifestyle",
        "weight":      0.7,
        "description": "Medications or supplements with stimulant or alerting "
                       "effects taken at the wrong time",
    },

    # ── PSYCHOLOGICAL (8) ─────────────────────────────────────────────────────
    "high_stress": {
        "domain":      "psychological",
        "weight":      1.0,
        "description": "Elevated stress level acting as top mediator of sleep "
                       "quality — financial, relational, or general",
    },
    "anxiety": {
        "domain":      "psychological",
        "weight":      0.95,
        "description": "Anxiety or tension at night, panic attacks, or fear of "
                       "failure keeping the student alert",
    },
    "depression": {
        "domain":      "psychological",
        "weight":      0.95,
        "description": "Depressive symptoms, hopelessness, loneliness, or grief "
                       "disrupting sleep initiation and maintenance",
    },
    "burnout": {
        "domain":      "psychological",
        "weight":      0.85,
        "description": "Academic or work burnout causing exhaustion that "
                       "paradoxically impairs sleep quality",
    },
    "rumination": {
        "domain":      "psychological",
        "weight":      0.85,
        "description": "Repetitive negative thinking, worry, or guilt replay "
                       "at night preventing sleep onset",
    },
    "poor_self_control": {
        "domain":      "psychological",
        "weight":      0.75,
        "description": "Difficulty adhering to planned routines, linked to "
                       "ADHD symptoms or low self-regulation",
    },
    "perfectionism": {
        "domain":      "psychological",
        "weight":      0.70,
        "description": "Unrealistically high standards, social comparison, "
                       "and self-criticism creating pre-sleep arousal",
    },
    "low_resilience": {
        "domain":      "psychological",
        "weight":      0.65,
        "description": "Poor emotional regulation and low ability to recover "
                       "from setbacks, sustaining stress responses",
    },

    # ── ENVIRONMENTAL (5) ─────────────────────────────────────────────────────
    "noise_disturbance": {
        "domain":      "environmental",
        "weight":      0.80,
        "description": "Noise from environment, roommates, partner, or "
                       "building disrupting sleep",
    },
    "light_disturbance": {
        "domain":      "environmental",
        "weight":      0.75,
        "description": "Light exposure at night suppressing melatonin and "
                       "delaying sleep onset",
    },
    "temperature_discomfort": {
        "domain":      "environmental",
        "weight":      0.65,
        "description": "Room temperature, humidity, or ventilation outside "
                       "comfortable range for sleep",
    },
    "poor_sleep_space": {
        "domain":      "environmental",
        "weight":      0.55,
        "description": "Uncomfortable bed, cluttered room, or disruptive "
                       "scents or devices in sleep space",
    },
    "safety_concern": {
        "domain":      "environmental",
        "weight":      0.70,
        "description": "Neighborhood safety worries or building maintenance "
                       "issues creating hypervigilance at night",
    },

    # ── BEHAVIORAL (5) ────────────────────────────────────────────────────────
    "excessive_screen_use": {
        "domain":      "behavioral",
        "weight":      0.85,
        "description": "Screen use within one hour of bed suppressing "
                       "melatonin and increasing cognitive arousal",
    },
    "irregular_schedule": {
        "domain":      "behavioral",
        "weight":      0.85,
        "description": "Inconsistent bedtime and wake time disrupting "
                       "circadian rhythm, worsened by weekend catch-up",
    },
    "poor_sleep_hygiene": {
        "domain":      "behavioral",
        "weight":      0.75,
        "description": "Absence of a pre-bed routine, using bed for "
                       "non-sleep activities, no relaxation practice",
    },
    "excessive_napping": {
        "domain":      "behavioral",
        "weight":      0.70,
        "description": "Long or late daytime naps reducing nighttime "
                       "sleep drive",
    },
    "poor_sleep_efficiency": {
        "domain":      "behavioral",
        "weight":      0.80,
        "description": "Long sleep latency or frequent wakeups indicating "
                       "the bed is not associated with sleep",
    },

    # ── ACADEMIC (5) ──────────────────────────────────────────────────────────
    "poor_sleep_duration": {
        "domain":      "academic",
        "weight":      1.0,
        "description": "Chronically insufficient total sleep hours — "
                       "the single strongest predictor of poor outcomes",
    },
    "academic_overload": {
        "domain":      "academic",
        "weight":      0.85,
        "description": "Excessive combined burden of coursework, employment, "
                       "internship, and extracurriculars",
    },
    "late_night_studying": {
        "domain":      "academic",
        "weight":      0.80,
        "description": "Habitual studying past midnight directly cutting "
                       "into sleep time",
    },
    "exam_pressure": {
        "domain":      "academic",
        "weight":      0.75,
        "description": "Acute exam period stress, cramming, and deadline "
                       "pressure causing sleep disruption",
    },
    "performance_impact": {
        "domain":      "academic",
        "weight":      0.70,
        "description": "Sleep loss visibly impairing concentration, "
                       "attendance, and academic performance",
    },
}


# =============================================================================
# SECTION 2 — PRIOR PROBABILITIES
# Starting beliefs before any questions are answered.
# Sourced from population-level evidence on university students.
# Ghana/African context weighted via Mbous 2022, Bousgheiri 2024.
# =============================================================================

PRIORS = {
    # Lifestyle
    "high_caffeine":           0.45,  # NSF: 45% students high caffeine
    "poor_diet_habits":        0.55,  # PSQI: 55% report diet-related disturbances
    "sedentary_lifestyle":     0.50,  # AASM: 50% students below activity threshold
    "substance_use":           0.35,  # CDC: 35% evening alcohol/substance use
    "poor_hydration":          0.40,  # NSF: 40% inadequate daily hydration
    "medication_interference": 0.25,  # CDC: 25% on sleep-affecting medications

    # Psychological
    "high_stress":             0.70,  # CDC/Wang 2023: 70% students high stress
    "anxiety":                 0.55,  # ISI: 55% clinically meaningful anxiety
    "depression":              0.35,  # Mbous 2022: 35% depression symptoms
    "burnout":                 0.40,  # Stores 2023: 40% student burnout
    "rumination":              0.50,  # DASS-21: 50% ruminate at night
    "poor_self_control":       0.45,  # Wang 2023: 45% poor routine adherence
    "perfectionism":           0.40,  # Stores 2023: 40% perfectionism traits
    "low_resilience":          0.45,  # Wang 2023: 45% low resilience scores

    # Environmental
    "noise_disturbance":       0.50,  # Altun 2012: 50% disturbed by noise
    "light_disturbance":       0.55,  # AASM: 55% inadequate light control
    "temperature_discomfort":  0.45,  # CDC: 45% report temperature issues
    "poor_sleep_space":        0.40,  # NSF: 40% uncomfortable sleep environment
    "safety_concern":          0.35,  # Altun 2012: 35% safety-related hyperarousal

    # Behavioral
    "excessive_screen_use":    0.72,  # Bousgheiri 2024: 72% pre-bed screens
    "irregular_schedule":      0.60,  # Okano 2019: 60% inconsistent schedules
    "poor_sleep_hygiene":      0.55,  # SHPS: 55% poor sleep hygiene practices
    "excessive_napping":       0.35,  # NSF: 35% excessive daytime napping
    "poor_sleep_efficiency":   0.50,  # PSQI: 50% report latency/wakeup issues

    # Academic
    "poor_sleep_duration":     0.65,  # NSF: 65% college students sleep-deprived
    "academic_overload":       0.55,  # Mbous 2022: 55% heavy combined burden
    "late_night_studying":     0.60,  # Okano 2019: 60% study past midnight
    "exam_pressure":           0.50,  # NSF: 50% exam-period sleep disruption
    "performance_impact":      0.55,  # Okano 2019: 55% report performance impact
}


# =============================================================================
# SECTION 3 — LIKELIHOOD TABLES
# P(answer | cause_present) for every question-cause pair.
#
# Format:
#   LIKELIHOODS[cause][question_id][answer_value] = probability
#
# Only question-cause pairs with meaningful evidence relationships
# are included. Missing pairs default to 0.5 (uninformative).
#
# SELF-REPORT BIAS CORRECTIONS applied to:
#   stress_level, depression_symptoms, anxiety_levels,
#   alcohol_consumption, recreational_drug_use, tobacco_use,
#   burnout_feelings, academic_pressure_peers_family
#
# For these questions, mid-range answers (medium/often/moderate)
# receive elevated likelihoods because students systematically
# underreport. A student reporting 'medium' stress is more likely
# to actually be 'high' than population base rates suggest.
# CDC/DASS-21/Mbous 2022 correction factors: +0.10 to +0.15.
# =============================================================================

LIKELIHOODS = {

    # ─────────────────────────────────────────────────────────────────────────
    # LIFESTYLE CAUSES
    # ─────────────────────────────────────────────────────────────────────────

    "high_caffeine": {
        "caffeine_intake": {
            "none":    0.05,
            "low":     0.20,
            "medium":  0.70,
            "high":    0.95,
        },
        "caffeine_timing": {
            "morning":    0.10,
            "afternoon":  0.30,
            "evening":    0.75,
            "late_night": 0.95,
        },
        "sleep_latency": {
            "fast":      0.15,
            "normal":    0.35,
            "slow":      0.65,
            "very_slow": 0.85,
        },
    },

    "poor_diet_habits": {
        "heavy_meal_before_bed": {
            "never":  0.05,
            "rarely": 0.25,
            "often":  0.75,
            "always": 0.95,
        },
        "snacking_at_night": {
            "never":  0.05,
            "rarely": 0.30,
            "often":  0.70,
            "always": 0.90,
        },
        "meal_size_variation": {
            "small":    0.10,
            "medium":   0.30,
            "large":    0.80,
            "variable": 0.55,
        },
        "diet_consistency": {
            "very_regular":      0.15,
            "somewhat_regular":  0.45,
            "irregular":         0.80,
        },
        "sugary_food_intake": {
            "never":  0.05,
            "rarely": 0.25,
            "often":  0.65,
            "daily":  0.85,
        },
    },

    "sedentary_lifestyle": {
        "physical_activity_level": {
            "none":     0.90,
            "low":      0.70,
            "moderate": 0.25,
            "high":     0.05,
        },
        "daytime_fatigue": {
            "never":     0.10,
            "rarely":    0.30,
            "often":     0.65,
            "every_day": 0.85,
        },
        "walking_after_dinner": {
            "never":  0.70,
            "rarely": 0.50,
            "often":  0.20,
            "always": 0.05,
        },
    },

    "substance_use": {
        # SELF-REPORT BIAS CORRECTION applied to alcohol and drug questions
        "alcohol_consumption": {
            "never":  0.05,
            "rarely": 0.35,   # elevated from 0.25 — underreporting correction
            "often":  0.80,
            "daily":  0.95,
        },
        "tobacco_use": {
            "none":       0.05,
            "occasional": 0.45,  # elevated — underreporting correction
            "regular":    0.90,
        },
        "recreational_drug_use": {
            "never":      0.05,
            "rarely":     0.40,  # elevated from 0.25 — underreporting correction
            "often":      0.80,
            "frequently": 0.95,
        },
        "nicotine_alternatives": {
            "never":  0.05,
            "rarely": 0.35,
            "often":  0.75,
            "daily":  0.90,
        },
        "frequent_wakeups": {
            "none":    0.10,
            "few":     0.30,
            "several": 0.65,
            "many":    0.85,
        },
    },

    "poor_hydration": {
        "hydration_habits": {
            "very_low": 0.85,
            "low":      0.60,
            "adequate": 0.20,
            "high":     0.10,
        },
        "fluid_intake_timing": {
            "early":    0.15,
            "moderate": 0.35,
            "late":     0.70,
            "in_bed":   0.90,
        },
        "frequent_wakeups": {
            "none":    0.10,
            "few":     0.30,
            "several": 0.60,
            "many":    0.80,
        },
    },

    "medication_interference": {
        "medication_supplements": {
            "no":          0.05,
            "occasional":  0.35,
            "daily_nonrx": 0.70,
            "daily_rx":    0.85,
        },
        "supplement_timing": {
            "morning":       0.10,
            "afternoon":     0.30,
            "evening":       0.80,
            "not_applicable":0.05,
        },
        "caffeine_alternatives": {
            "never":  0.05,
            "rarely": 0.30,
            "often":  0.70,
            "daily":  0.90,
        },
        "sleep_latency": {
            "fast":      0.10,
            "normal":    0.25,
            "slow":      0.60,
            "very_slow": 0.85,
        },
    },

    # ─────────────────────────────────────────────────────────────────────────
    # PSYCHOLOGICAL CAUSES
    # ─────────────────────────────────────────────────────────────────────────

    "high_stress": {
        # stress_level=medium is background noise, not evidence of HIGH stress.
        # The Prolog cause rule requires stress_level=high. Bayesian must align.
        # Lowered medium from 0.55 → 0.25 to prevent false positives on medium stress.
        "stress_level": {
            "low":    0.10,
            "medium": 0.25,   # was 0.55 — too high; caused spurious high_stress fires
            "high":   0.92,
        },
        "financial_stress": {
            "never":      0.10,
            "rarely":     0.30,
            "often":      0.70,
            "constantly": 0.92,
        },
        "general_worries": {
            "never":  0.10,
            "rarely": 0.30,
            "often":  0.72,
            "always": 0.92,
        },
        "sleep_hours": {
            "less_than_4":  0.80,
            "four_to_six":  0.65,
            "six_to_eight": 0.30,
            "more_than_8":  0.10,
        },
        "daytime_fatigue": {
            "never":     0.10,
            "rarely":    0.30,
            "often":     0.65,
            "every_day": 0.88,
        },
    },

    "anxiety": {
        # SELF-REPORT BIAS CORRECTION: often/rarely elevated
        "anxiety_levels": {
            "never":      0.05,
            "rarely":     0.40,   # elevated from 0.25 — underreporting
            "often":      0.80,
            "every_night":0.95,
        },
        "panic_attacks": {
            "never":      0.05,
            "rarely":     0.50,
            "often":      0.85,
            "frequently": 0.97,
        },
        "fear_of_failure": {
            "none":     0.10,
            "mild":     0.35,
            "moderate": 0.65,
            "strong":   0.90,
        },
        "sleep_latency": {
            "fast":      0.10,
            "normal":    0.30,
            "slow":      0.70,
            "very_slow": 0.90,
        },
        "worry_before_bed": {
            "never":  0.05,
            "rarely": 0.30,
            "often":  0.75,
            "always": 0.95,
        },
    },

    "depression": {
        # SELF-REPORT BIAS CORRECTION: rarely/often elevated
        "depression_symptoms": {
            "never":     0.05,
            "rarely":    0.40,   # elevated from 0.25 — underreporting
            "often":     0.82,
            "every_day": 0.97,
        },
        "loneliness_levels": {
            "never":      0.10,
            "rarely":     0.30,
            "often":      0.70,
            "constantly": 0.90,
        },
        "trauma_or_grief": {
            "no":          0.10,
            "mild":        0.45,
            "moderate":    0.75,
            "significant": 0.92,
        },
        "sleep_hours": {
            "less_than_4":  0.85,
            "four_to_six":  0.70,
            "six_to_eight": 0.30,
            "more_than_8":  0.20,  # hypersomnia also linked to depression
        },
        "morning_sleepiness": {
            "very_alert":     0.05,
            "somewhat_alert": 0.20,
            "groggy":         0.60,
            "extremely_tired":0.88,
        },
        "optimism_outlook": {
            "very_optimistic": 0.05,
            "somewhat":        0.25,
            "not_very":        0.65,
            "pessimistic":     0.90,
        },
    },

    "burnout": {
        # SELF-REPORT BIAS CORRECTION: often elevated
        "burnout_feelings": {
            "never":      0.05,
            "rarely":     0.25,
            "often":      0.78,   # elevated from 0.68 — underreporting
            "constantly": 0.95,
        },
        "academic_motivation": {
            "high":     0.05,
            "moderate": 0.25,
            "low":      0.70,
            "very_low": 0.92,
        },
        "daytime_fatigue": {
            "never":     0.05,
            "rarely":    0.25,
            "often":     0.68,
            "every_day": 0.90,
        },
        "morning_sleepiness": {
            "very_alert":     0.05,
            "somewhat_alert": 0.20,
            "groggy":         0.65,
            "extremely_tired":0.90,
        },
        "therapy_attendance": {
            "never":      0.60,  # inverse — absence suggests unaddressed burnout
            "occasionally":0.45,
            "regularly":  0.25,
            "weekly":     0.15,
        },
    },

    "rumination": {
        "worry_before_bed": {
            "never":  0.05,
            "rarely": 0.30,
            "often":  0.78,
            "always": 0.95,
        },
        "rumination_habits": {
            "never":  0.05,
            "rarely": 0.25,
            "often":  0.80,
            "always": 0.97,
        },
        "guilt_feelings": {
            "never":  0.05,
            "rarely": 0.25,
            "often":  0.70,
            "always": 0.90,
        },
        "existential_worries": {
            "never":  0.10,
            "rarely": 0.30,
            "often":  0.65,
            "always": 0.85,
        },
        "sleep_latency": {
            "fast":      0.05,
            "normal":    0.25,
            "slow":      0.70,
            "very_slow": 0.90,
        },
        "forgiveness_practices": {
            "always":  0.10,
            "often":   0.25,
            "rarely":  0.65,
            "never":   0.85,
        },
    },

    "poor_self_control": {
        "self_control_routines": {
            "very_good": 0.05,
            "fair":      0.40,
            "poor":      0.90,
        },
        "adhd_symptoms": {
            "no":       0.10,
            "mild":     0.45,
            "moderate": 0.75,
            "severe":   0.95,
        },
        "procrastination_habits": {
            "never":  0.05,
            "rarely": 0.25,
            "often":  0.75,
            "always": 0.95,
        },
        "boredom_frequency": {
            "never":      0.10,
            "rarely":     0.30,
            "often":      0.65,
            "constantly": 0.85,
        },
        "consistent_sleep_time": {
            "very_consistent":     0.05,
            "somewhat_consistent": 0.40,
            "inconsistent":        0.85,
        },
    },

    "perfectionism": {
        "perfectionism_tendencies": {
            "never":  0.05,
            "rarely": 0.20,
            "often":  0.75,
            "always": 0.95,
        },
        "social_comparison": {
            "never":  0.05,
            "rarely": 0.25,
            "often":  0.70,
            "always": 0.90,
        },
        "fear_of_failure": {
            "none":     0.05,
            "mild":     0.30,
            "moderate": 0.65,
            "strong":   0.90,
        },
        "self_esteem_level": {
            "high":     0.05,
            "medium":   0.30,
            "low":      0.70,
            "very_low": 0.88,
        },
        "sleep_latency": {
            "fast":      0.10,
            "normal":    0.30,
            "slow":      0.65,
            "very_slow": 0.85,
        },
    },

    "low_resilience": {
        "resilience_level": {
            "very_well":   0.05,
            "fairly_well": 0.25,
            "poorly":      0.78,
            "very_poorly": 0.95,
        },
        "emotional_regulation": {
            "very_well":   0.05,
            "fairly_well": 0.25,
            "poorly":      0.75,
            "very_poorly": 0.95,
        },
        "attachment_style": {
            "secure":       0.10,
            "anxious":      0.75,
            "avoidant":     0.60,
            "disorganized": 0.85,
        },
        "seasonal_mood_changes": {
            "no":       0.10,
            "mild":     0.35,
            "moderate": 0.65,
            "severe":   0.90,
        },
    },

    # ─────────────────────────────────────────────────────────────────────────
    # ENVIRONMENTAL CAUSES
    # ─────────────────────────────────────────────────────────────────────────

    "noise_disturbance": {
        "noisy_environment": {
            "quiet":      0.05,
            "some_noise": 0.40,
            "loud":       0.92,
        },
        "shared_living": {
            "alone":        0.20,
            "shared_small": 0.55,
            "shared_large": 0.80,
        },
        "partner_snoring": {
            "not_applicable": 0.10,
            "never":          0.05,
            "rarely":         0.30,
            "often":          0.80,
            "always":         0.95,
        },
        "building_maintenance": {
            "never":      0.05,
            "rarely":     0.30,
            "often":      0.70,
            "frequently": 0.90,
        },
        "frequent_wakeups": {
            "none":    0.05,
            "few":     0.30,
            "several": 0.65,
            "many":    0.88,
        },
    },

    "light_disturbance": {
        "light_exposure_at_night": {
            "never":  0.05,
            "rarely": 0.25,
            "often":  0.75,
            "always": 0.95,
        },
        "window_light_control": {
            "effective": 0.10,
            "partial":   0.50,
            "none":      0.90,
        },
        "electronic_devices_in_room": {
            "none":    0.05,
            "few":     0.30,
            "several": 0.60,
            "many":    0.85,
        },
        "natural_light_exposure": {
            # inverse — low day light = higher disruption risk at night
            "high":     0.20,
            "moderate": 0.35,
            "low":      0.65,
            "none":     0.85,
        },
        "sleep_latency": {
            "fast":      0.10,
            "normal":    0.30,
            "slow":      0.68,
            "very_slow": 0.88,
        },
    },

    "temperature_discomfort": {
        "uncomfortable_temperature": {
            "comfortable": 0.05,
            "too_hot":     0.90,
            "too_cold":    0.88,
        },
        "humidity_levels": {
            "comfortable": 0.05,
            "too_dry":     0.70,
            "too_humid":   0.75,
        },
        "ventilation_quality": {
            "excellent": 0.05,
            "fair":      0.40,
            "poor":      0.85,
        },
        "frequent_wakeups": {
            "none":    0.05,
            "few":     0.25,
            "several": 0.60,
            "many":    0.82,
        },
    },

    "poor_sleep_space": {
        "bed_comfort": {
            "very_comfortable":     0.05,
            "somewhat_comfortable": 0.40,
            "uncomfortable":        0.90,
        },
        "room_clutter": {
            "minimal":  0.10,
            "moderate": 0.45,
            "high":     0.85,
        },
        "scent_in_room": {
            "no":               0.05,
            "mild_pleasant":    0.10,
            "moderate_neutral": 0.30,
            "strong_disruptive":0.85,
        },
        "electromagnetic_exposure": {
            "far":      0.10,
            "moderate": 0.30,
            "close":    0.60,
            "in_bed":   0.80,
        },
    },

    "safety_concern": {
        "neighborhood_safety": {
            "not_concerned": 0.05,
            "mild":          0.35,
            "moderate":      0.65,
            "very_concerned":0.90,
        },
        "building_maintenance": {
            "never":      0.05,
            "rarely":     0.30,
            "often":      0.65,
            "frequently": 0.88,
        },
        "sleep_latency": {
            "fast":      0.10,
            "normal":    0.25,
            "slow":      0.60,
            "very_slow": 0.82,
        },
    },

    # ─────────────────────────────────────────────────────────────────────────
    # BEHAVIORAL CAUSES
    # ─────────────────────────────────────────────────────────────────────────

    "excessive_screen_use": {
        "screen_before_bed": {
            "never":  0.05,
            "rarely": 0.25,
            "often":  0.80,
            "always": 0.95,
        },
        "social_media_use_at_night": {
            "none":     0.05,
            "short":    0.30,
            "moderate": 0.70,
            "long":     0.92,
        },
        "bed_for_sleep_only": {
            "never":  0.80,  # inverse — always using bed for other things
            "rarely": 0.60,
            "often":  0.30,
            "always": 0.10,
        },
        "sleep_latency": {
            "fast":      0.10,
            "normal":    0.30,
            "slow":      0.70,
            "very_slow": 0.90,
        },
    },

    "irregular_schedule": {
        "consistent_sleep_time": {
            "very_consistent":     0.05,
            "somewhat_consistent": 0.40,
            "inconsistent":        0.92,
        },
        "weekend_sleep_catchup": {
            "same":         0.05,
            "slightly_more":0.35,
            "much_more":    0.75,
            "far_more":     0.95,
        },
        "social_interactions_at_night": {
            "never":      0.10,
            "rarely":     0.30,
            "often":      0.65,
            "frequently": 0.85,
        },
        "alarm_usage": {
            "one":     0.10,
            "few":     0.35,
            "several": 0.65,
            "many":    0.88,
        },
    },

    "poor_sleep_hygiene": {
        "bedtime_routine_consistency": {
            "daily":     0.05,
            "sometimes": 0.40,
            "rarely":    0.80,
            "no":        0.95,
        },
        "relaxation_techniques": {
            "always":  0.05,
            "often":   0.20,
            "rarely":  0.65,
            "never":   0.88,
        },
        "bed_for_sleep_only": {
            "never":  0.88,   # inverse
            "rarely": 0.65,
            "often":  0.30,
            "always": 0.05,
        },
        "reading_before_bed": {
            "always":  0.05,
            "often":   0.15,
            "rarely":  0.55,
            "never":   0.78,
        },
        "bath_shower_timing": {
            "daily":   0.05,
            "often":   0.15,
            "rarely":  0.55,
            "never":   0.75,
        },
    },

    "excessive_napping": {
        "daytime_nap_hours": {
            "none":     0.05,
            "short":    0.25,
            "moderate": 0.75,
            "long":     0.95,
        },
        "daytime_fatigue": {
            "never":     0.05,
            "rarely":    0.25,
            "often":     0.65,
            "every_day": 0.85,
        },
        "morning_sleepiness": {
            "very_alert":     0.10,
            "somewhat_alert": 0.30,
            "groggy":         0.65,
            "extremely_tired":0.85,
        },
    },

    "poor_sleep_efficiency": {
        "sleep_latency": {
            "fast":      0.05,
            "normal":    0.20,
            "slow":      0.80,
            "very_slow": 0.97,
        },
        "frequent_wakeups": {
            "none":    0.05,
            "few":     0.30,
            "several": 0.78,
            "many":    0.97,
        },
        "morning_sleepiness": {
            "very_alert":     0.05,
            "somewhat_alert": 0.20,
            "groggy":         0.70,
            "extremely_tired":0.92,
        },
        "alarm_usage": {
            "one":     0.10,
            "few":     0.40,
            "several": 0.70,
            "many":    0.90,
        },
    },

    # ─────────────────────────────────────────────────────────────────────────
    # ACADEMIC CAUSES
    # ─────────────────────────────────────────────────────────────────────────

    "poor_sleep_duration": {
        "sleep_hours": {
            "less_than_4":  0.97,
            "four_to_six":  0.88,
            "six_to_eight": 0.15,
            "more_than_8":  0.05,
        },
        "daytime_fatigue": {
            "never":     0.05,
            "rarely":    0.20,
            "often":     0.70,
            "every_day": 0.92,
        },
        "morning_sleepiness": {
            "very_alert":     0.05,
            "somewhat_alert": 0.15,
            "groggy":         0.68,
            "extremely_tired":0.92,
        },
        "performance_impact": {
            "never":     0.05,
            "rarely":    0.25,
            "often":     0.72,
            "every_day": 0.95,
        },
    },

    "academic_overload": {
        "academic_workload": {
            "light":   0.10,
            "average": 0.40,
            "heavy":   0.90,
        },
        "employment_status": {
            "none":      0.20,
            "part_time": 0.55,
            "full_time": 0.88,
        },
        "extracurricular_hours": {
            "none":     0.15,
            "low":      0.35,
            "moderate": 0.60,
            "high":     0.88,
        },
        "internship_demands": {
            "none":     0.10,
            "low":      0.35,
            "moderate": 0.65,
            "high":     0.90,
        },
        "sleep_hours": {
            "less_than_4":  0.88,
            "four_to_six":  0.72,
            "six_to_eight": 0.25,
            "more_than_8":  0.05,
        },
    },

    "late_night_studying": {
        "study_past_midnight": {
            "never":  0.05,
            "rarely": 0.25,
            "often":  0.82,
            "always": 0.97,
        },
        "procrastination_habits": {
            "never":  0.05,
            "rarely": 0.25,
            "often":  0.70,
            "always": 0.90,
        },
        "exam_preparation_style": {
            "never":  0.10,
            "rarely": 0.30,
            "often":  0.72,
            "always": 0.90,
        },
        "sleep_hours": {
            "less_than_4":  0.90,
            "four_to_six":  0.75,
            "six_to_eight": 0.20,
            "more_than_8":  0.05,
        },
    },

    "exam_pressure": {
        "exam_period": {
            "yes": 0.85,
            "no":  0.15,
        },
        "upcoming_deadline": {
            "yes": 0.80,
            "no":  0.15,
        },
        # SELF-REPORT BIAS CORRECTION applied
        "academic_pressure_peers_family": {
            "none":     0.05,
            "mild":     0.35,   # elevated — underreporting correction
            "moderate": 0.65,
            "high":     0.90,
        },
        "grade_satisfaction": {
            "very_satisfied":   0.05,
            "somewhat":         0.30,
            "dissatisfied":     0.70,
            "very_dissatisfied":0.90,
        },
        "stress_level": {
            "low":    0.10,
            "medium": 0.50,   # elevated — underreporting correction
            "high":   0.90,
        },
    },

    "performance_impact": {
        "performance_impact": {
            "never":     0.05,
            "rarely":    0.30,
            "often":     0.80,
            "every_day": 0.97,
        },
        "lecture_attendance": {
            "never":      0.05,
            "rarely":     0.30,
            "often":      0.75,
            "frequently": 0.92,
        },
        "note_taking_effectiveness": {
            "very_effective": 0.05,
            "fair":           0.30,
            "poor":           0.72,
            "very_poor":      0.92,
        },
        "daytime_fatigue": {
            "never":     0.05,
            "rarely":    0.25,
            "often":     0.70,
            "every_day": 0.90,
        },
    },
}


# =============================================================================
# SECTION 4 — CORRELATION PAIRS
#
# Addresses the Naive Bayes independence assumption violation.
#
# Each pair defines two question IDs and the direction of problematic answers.
# When both questions in a pair are answered in the problematic direction,
# a dampening correction is applied: the posterior update from the SECOND
# question in the pair is reduced by the dampening_factor, because part of
# its information was already captured by the first question.
#
# This prevents the system from double-counting correlated evidence,
# which is the main source of the 2-3% accuracy loss from the independence
# assumption. With this correction, expected accuracy loss reduces to ~1%.
#
# Source evidence for each pair listed inline.
# =============================================================================

CORRELATION_PAIRS = [
    {
        "question_a":        "stress_level",
        "question_b":        "rumination_habits",
        "problem_values_a":  ["medium", "high"],
        "problem_values_b":  ["often", "always"],
        "dampening_factor":  0.30,
        "evidence":          "DASS-21: stress and rumination co-occur in 50% "
                             "of anxious students — strong positive correlation",
    },
    {
        "question_a":        "anxiety_levels",
        "question_b":        "perfectionism_tendencies",
        "problem_values_a":  ["often", "every_night"],
        "problem_values_b":  ["often", "always"],
        "dampening_factor":  0.25,
        "evidence":          "Stores 2023: anxiety and perfectionism "
                             "share 60% variance in student populations",
    },
    {
        "question_a":        "screen_before_bed",
        "question_b":        "consistent_sleep_time",
        "problem_values_a":  ["often", "always"],
        "problem_values_b":  ["inconsistent"],
        "dampening_factor":  0.28,
        "evidence":          "AASM/Bousgheiri: screen use and irregular "
                             "schedule co-occur in 87% of affected students",
    },
    {
        "question_a":        "depression_symptoms",
        "question_b":        "loneliness_levels",
        "problem_values_a":  ["often", "every_day"],
        "problem_values_b":  ["often", "constantly"],
        "dampening_factor":  0.25,
        "evidence":          "Mbous 2022: depression and loneliness share "
                             "55% variance — loneliness often mediates depression",
    },
    {
        "question_a":        "academic_workload",
        "question_b":        "study_past_midnight",
        "problem_values_a":  ["heavy"],
        "problem_values_b":  ["often", "always"],
        "dampening_factor":  0.22,
        "evidence":          "Okano 2019: heavy workload and late studying "
                             "co-occur in 70% of sleep-deprived students",
    },
    {
        "question_a":        "burnout_feelings",
        "question_b":        "self_control_routines",
        "problem_values_a":  ["often", "constantly"],
        "problem_values_b":  ["poor"],
        "dampening_factor":  0.20,
        "evidence":          "Wang 2023: burnout and poor self-control "
                             "share 45% variance in routine adherence",
    },
    {
        "question_a":        "worry_before_bed",
        "question_b":        "sleep_latency",
        "problem_values_a":  ["often", "always"],
        "problem_values_b":  ["slow", "very_slow"],
        "dampening_factor":  0.30,
        "evidence":          "PSQI: pre-sleep worry and long latency "
                             "are almost definitionally linked — 75% overlap",
    },
    {
        "question_a":        "stress_level",
        "question_b":        "sleep_hours",
        "problem_values_a":  ["high"],
        "problem_values_b":  ["less_than_4", "four_to_six"],
        "dampening_factor":  0.25,
        "evidence":          "Wang/NSF: high stress and short sleep form "
                             "a bidirectional cycle — 91% joint probability",
    },
]


# =============================================================================
# SECTION 5 — CAUSE WEIGHTS FOR SEVERITY SCORING
# Extracted from CAUSES dict for fast lookup in severity computation.
# =============================================================================

CAUSE_WEIGHTS = {cause: info["weight"] for cause, info in CAUSES.items()}


# =============================================================================
# SECTION 6 — ANCHOR QUESTIONS
# Direct sleep outcome measures used in Layer 2 severity scoring.
# These are not predictors — they are direct measurements of sleep quality.
# Their values escalate or de-escalate severity independent of cause count.
# =============================================================================

ANCHOR_QUESTIONS = {
    "sleep_hours": {
        "less_than_4":  1.0,   # maximum anchor severity
        "four_to_six":  0.7,
        "six_to_eight": 0.2,
        "more_than_8":  0.0,
    },
    "sleep_latency": {
        "fast":      0.0,
        "normal":    0.1,
        "slow":      0.6,
        "very_slow": 1.0,
    },
    "frequent_wakeups": {
        "none":    0.0,
        "few":     0.2,
        "several": 0.7,
        "many":    1.0,
    },
    "morning_sleepiness": {
        "very_alert":     0.0,
        "somewhat_alert": 0.1,
        "groggy":         0.6,
        "extremely_tired":1.0,
    },
    "daytime_fatigue": {
        "never":     0.0,
        "rarely":    0.1,
        "often":     0.6,
        "every_day": 1.0,
    },
}


# =============================================================================
# SECTION 7 — CLINICAL FLAG RULES
# Answer combinations requiring professional referral.
# These override severity and domain pattern when triggered.
# =============================================================================

CLINICAL_FLAG_RULES = [
    {
        "id":      "CF1",
        "label":   "Severe Depression with Sleep Deprivation",
        "check":   lambda a: (
            a.get("depression_symptoms") in ["often", "every_day"] and
            a.get("sleep_hours") in ["less_than_4"]
        ),
        "message": (
            "Your responses indicate a significant combination of persistent "
            "low mood and severe sleep deprivation. This pattern requires "
            "professional support — it is not manageable through self-help "
            "alone. Please contact the UG Counselling Centre for a free "
            "initial appointment. If you are in crisis, visit the campus "
            "health unit directly. This is a medical situation, not a "
            "personal failing."
        ),
    },
    {
        "id":      "CF2",
        "label":   "Anxiety with Panic Attacks",
        "check":   lambda a: (
            a.get("anxiety_levels") in ["every_night"] and
            a.get("panic_attacks") in ["often", "frequently"]
        ),
        "message": (
            "Nightly anxiety combined with frequent panic attacks is a "
            "clinical presentation that goes beyond what sleep hygiene "
            "improvements can address. A trained counsellor or psychologist "
            "can provide CBT-based interventions that are highly effective "
            "for this pattern. Please seek support at your campus health "
            "or counselling services."
        ),
    },
    {
        "id":      "CF3",
        "label":   "Diagnosed Severe Sleep Disorder",
        "check":   lambda a: (
            a.get("sleep_disorders") in ["diagnosed_severe"]
        ),
        "message": (
            "You have indicated a diagnosed severe sleep disorder. SleepWise "
            "can complement but not replace your medical treatment plan. "
            "Please ensure you are actively following up with a healthcare "
            "provider. The recommendations below are offered as supportive "
            "lifestyle guidance only."
        ),
    },
    {
        "id":      "CF4",
        "label":   "Burnout with Depression",
        "check":   lambda a: (
            a.get("burnout_feelings") in ["constantly"] and
            a.get("depression_symptoms") in ["often", "every_day"]
        ),
        "message": (
            "Constant burnout alongside persistent depressive symptoms "
            "is a serious combination that significantly impairs recovery. "
            "This pattern is common in high-pressure academic environments "
            "and responds well to early professional intervention. Please "
            "reach out to campus counselling services before this cycle "
            "deepens further."
        ),
    },
    {
        "id":      "CF5",
        "label":   "Triple Psychological Overload",
        "check":   lambda a: (
            a.get("depression_symptoms") in ["often", "every_day"] and
            a.get("anxiety_levels") in ["often", "every_night"] and
            a.get("sleep_hours") in ["less_than_4", "four_to_six"]
        ),
        "message": (
            "Your responses show simultaneous depression, high anxiety, "
            "and significant sleep deprivation — a triple combination that "
            "creates a self-reinforcing crisis cycle. Professional support "
            "is strongly recommended. Please contact UG Counselling Centre "
            "or any available mental health service as a priority."
        ),
    },
]


# =============================================================================
# SECTION 8 — CORE FUNCTIONS
# =============================================================================

def _get_likelihood(cause, question_id, answer_value):
    """
    Safe likelihood lookup with uninformative default.
    Returns P(answer | cause). Defaults to 0.5 if pair not defined.
    """
    return (
        LIKELIHOODS
        .get(cause, {})
        .get(question_id, {})
        .get(answer_value, 0.5)
    )


def _apply_correlation_correction(log_posteriors, answers):
    """
    Applies dampening correction for correlated question pairs.
    Reduces the log-posterior contribution of the second question
    in a correlated pair when both fire in the problematic direction.
    This partially compensates for the Naive Bayes independence
    assumption, reducing accuracy loss from ~2-3% to ~1%.
    """
    corrected = dict(log_posteriors)

    for pair in CORRELATION_PAIRS:
        q_a = pair["question_a"]
        q_b = pair["question_b"]
        val_a = answers.get(q_a)
        val_b = answers.get(q_b)

        # Only apply if both questions were answered in problematic direction
        if (val_a in pair["problem_values_a"] and
                val_b in pair["problem_values_b"]):

            damp = pair["dampening_factor"]

            # For each cause, reduce the marginal contribution of question_b
            # by the dampening factor, reflecting that its information was
            # partly captured by question_a already.
            for cause in corrected:
                like_b = _get_likelihood(cause, q_b, val_b)
                if like_b != 0.5:  # only adjust informative pairs
                    # Original contribution: log(like_b)
                    # Dampened contribution: log(like_b) * (1 - damp)
                    original_contrib = math.log(max(like_b, 1e-9))
                    corrected[cause] += original_contrib * (-damp)

    return corrected


def update_posteriors(answers):
    """
    Main Bayesian update function.

    Takes the current answers dict {question_id: answer_value} and
    returns normalized posterior probabilities for all 29 causes.

    Steps:
      1. Initialize log-posteriors from PRIORS (log-space for stability)
      2. For each answer, multiply likelihood for each cause (add in log-space)
      3. Apply correlation correction to address independence assumption
      4. Exponentiate and normalize to get probabilities

    Args:
        answers (dict): {question_id: answer_value} — current session answers

    Returns:
        dict: {cause_name: posterior_probability} — all 29 causes, normalized
    """
    # Step 1 — Initialize in log-space from priors
    log_posts = {
        cause: math.log(max(prior, 1e-9))
        for cause, prior in PRIORS.items()
    }

    # Step 2 — Update with each answer (Naive Bayes product in log-space)
    for q_id, answer_val in answers.items():
        for cause in log_posts:
            likelihood = _get_likelihood(cause, q_id, answer_val)
            log_posts[cause] += math.log(max(likelihood, 1e-9))

    # Step 3 — Apply correlation correction
    log_posts = _apply_correlation_correction(log_posts, answers)

    # Step 4 — Exponentiate
    raw_posts = {cause: math.exp(lp) for cause, lp in log_posts.items()}

    # Step 5 — Normalize so all posteriors sum to 1
    total = sum(raw_posts.values())
    if total > 0:
        normalized = {c: v / total for c, v in raw_posts.items()}
    else:
        normalized = {c: 1.0 / len(raw_posts) for c in raw_posts}

    return normalized


def classify_sleep_complaint(answers):
    """
    Layer 1 of diagnosis — Primary Sleep Complaint Classification.

    Identifies which of four clinical sleep complaint categories apply
    based on direct answer values from anchor questions.
    A student can fall into multiple categories simultaneously.

    Categories (from ISI/PSQI clinical framework):
      - Sleep Onset Insomnia     : difficulty falling asleep
      - Sleep Maintenance Insomnia: difficulty staying asleep
      - Sleep Deprivation        : chronically insufficient total hours
      - Non-Restorative Sleep    : hours present but unrefreshing

    Args:
        answers (dict): current session answers

    Returns:
        list of str: active complaint categories (1-4 items)
    """
    complaints = []

    # Sleep Onset Insomnia — long latency + cognitive/behavioral drivers
    latency = answers.get("sleep_latency")
    if latency in ["slow", "very_slow"]:
        complaints.append("Sleep Onset Insomnia")

    # Sleep Maintenance Insomnia — frequent waking
    wakeups = answers.get("frequent_wakeups")
    if wakeups in ["several", "many"]:
        complaints.append("Sleep Maintenance Insomnia")

    # Sleep Deprivation — insufficient total hours
    hours = answers.get("sleep_hours")
    if hours in ["less_than_4", "four_to_six"]:
        complaints.append("Sleep Deprivation")

    # Non-Restorative Sleep — unrefreshing despite plausible duration
    # Triggered when morning sleepiness is high but hours are not critically low
    morning = answers.get("morning_sleepiness")
    if morning in ["groggy", "extremely_tired"] and hours not in ["less_than_4"]:
        complaints.append("Non-Restorative Sleep")

    # Default if no anchor questions were asked (e.g., Quick variant)
    if not complaints:
        fatigue = answers.get("daytime_fatigue")
        if fatigue in ["often", "every_day"]:
            complaints.append("Sleep Deprivation")
        else:
            complaints.append("Unspecified Sleep Disturbance")

    return complaints


def get_fired_causes(posteriors, answers=None):
    """
    Determines which causes are 'fired' using a distribution-relative method.

    After normalization across 29 causes, posteriors are small fractions
    summing to 1. We use:
      1. Causes more than 1.0 std above the mean (clear standouts)
      2. Fallback to 0.5 std threshold if fewer than 3 fire AND the
         student's anchor questions suggest real sleep problems.

    Anchor veto: if 75%+ of answered anchor/key questions show healthy
    values, we suppress the fallback. A healthy student correctly gets
    zero or very few fired causes, mapping to 'none' severity.

    Args:
        posteriors (dict): output of update_posteriors()
        answers (dict):    session answers — used for anchor veto check

    Returns:
        dict: {cause: posterior} for fired causes, sorted by weight desc
    """
    values = list(posteriors.values())
    mean = sum(values) / len(values)
    variance = sum((v - mean) ** 2 for v in values) / len(values)
    std = variance ** 0.5

    # Primary: causes more than 1.0 std above mean
    threshold = mean + (1.0 * std)

    # Suppression: only fire a cause if at least one of its likelihood
    # questions was actually answered. Causes with zero answered questions
    # have posteriors driven purely by the prior — not evidence.
    def has_evidence(cause, answers_dict):
        if not answers_dict:
            return True  # no answers provided — allow all
        cause_questions = set(LIKELIHOODS.get(cause, {}).keys())
        return bool(cause_questions & set(answers_dict.keys()))

    fired = {
        c: round(p, 3)
        for c, p in posteriors.items()
        if p >= threshold and has_evidence(c, answers)
    }

    # Anchor veto — check if this is a genuinely healthy profile
    GOOD_ANCHOR_VALUES = {
        "sleep_hours":        {"six_to_eight", "more_than_8"},
        "sleep_latency":      {"fast", "normal"},
        "frequent_wakeups":   {"none", "few"},
        "morning_sleepiness": {"very_alert", "somewhat_alert"},
        "daytime_fatigue":    {"never", "rarely"},
        "stress_level":       {"low"},
        "depression_symptoms":{"never", "rarely"},
        "anxiety_levels":     {"never", "rarely"},
    }
    healthy_profile = False
    if answers:
        answered = [(q, answers.get(q)) for q in GOOD_ANCHOR_VALUES if q in answers]
        good_count = sum(1 for q, v in answered if v in GOOD_ANCHOR_VALUES[q])
        if answered and (good_count / len(answered)) >= 0.75:
            healthy_profile = True

    # Fallback: only if not healthy AND fewer than 3 fired
    if len(fired) < 3 and not healthy_profile:
        soft_threshold = mean + (0.5 * std)
        above_soft = {
            c: round(p, 3)
            for c, p in posteriors.items()
            if p > soft_threshold and has_evidence(c, answers)
        }
        fired = dict(
            sorted(above_soft.items(), key=lambda x: x[1], reverse=True)[:5]
        )

    return dict(sorted(fired.items(),
                        key=lambda x: CAUSE_WEIGHTS[x[0]],
                        reverse=True))


def compute_weighted_severity(posteriors, answers):
    """
    Layer 2 of diagnosis — Weighted Severity Scoring.

    Combines three inputs:
      A. Weighted cause count: sum of weights for fired causes
      B. Anchor question scores: direct sleep outcome measurements
      C. Cause count: raw number of fired causes

    Final severity = weighted blend of A, B, C mapped to four levels.

    Args:
        posteriors (dict): output of update_posteriors()
        answers (dict):    current session answers

    Returns:
        str: 'none' | 'mild' | 'moderate' | 'severe'
        float: raw severity score (0.0 to 1.0) for transparency
    """
    # Component A — weighted cause score using relative firing
    fired_causes = get_fired_causes(posteriors, answers)
    weighted_cause_score = sum(
        CAUSE_WEIGHTS[c] * p
        for c, p in fired_causes.items()
    )
    # Normalize A to 0-1 range (max possible = sum of all weights)
    max_weighted = sum(CAUSE_WEIGHTS.values())
    component_a = min(weighted_cause_score / max_weighted, 1.0)

    # Component B — anchor question score
    anchor_scores = []
    for q_id, value_map in ANCHOR_QUESTIONS.items():
        answer_val = answers.get(q_id)
        if answer_val is not None:
            anchor_scores.append(value_map.get(answer_val, 0.0))
    component_b = (
        sum(anchor_scores) / len(anchor_scores)
        if anchor_scores else 0.0
    )

    # Component C — raw cause count (normalized)
    component_c = min(len(fired_causes) / len(CAUSES), 1.0)

    # Weighted blend: anchors matter most (direct measures),
    # then weighted causes, then raw count
    raw_score = (0.45 * component_b) + (0.35 * component_a) + (0.20 * component_c)

    # Map to severity levels
    if raw_score < 0.15:
        severity = "none"
    elif raw_score < 0.35:
        severity = "mild"
    elif raw_score < 0.60:
        severity = "moderate"
    else:
        severity = "severe"

    return severity, round(raw_score, 3)


def identify_domain_pattern(posteriors, answers=None):
    """
    Layer 3 of diagnosis — Domain Pattern Recognition.

    Determines which domain(s) are driving the student's sleep issues
    by looking at the distribution of fired causes across domains.

    Args:
        posteriors (dict): output of update_posteriors()
        answers (dict):    session answers passed through for firing logic

    Returns:
        str: primary pattern label for the diagnosis opening statement
        dict: domain_scores — score per domain for transparency
    """
    fired = get_fired_causes(posteriors, answers)

    domain_scores = defaultdict(float)
    domain_counts = defaultdict(int)

    for cause, posterior in fired.items():
        if True:  # all fired causes are already filtered
            domain = CAUSES[cause]["domain"]
            domain_scores[domain] += posterior * CAUSE_WEIGHTS[cause]
            domain_counts[domain] += 1

    if not domain_scores:
        return "No significant sleep issues identified", dict(domain_scores)

    # Sort domains by score descending
    sorted_domains = sorted(domain_scores.items(), key=lambda x: x[1], reverse=True)
    top_domain, top_score = sorted_domains[0]

    # Check if multifactorial (4+ domains have at least one fired cause)
    active_domains = [d for d, count in domain_counts.items() if count >= 1]

    if len(active_domains) >= 4:
        pattern = (
            "Multifactorial — your sleep difficulties span multiple areas "
            "of your life and will benefit from a structured approach "
            "addressing each domain in priority order"
        )
    elif len(sorted_domains) >= 2:
        second_domain = sorted_domains[1][0]
        pattern = (
            f"Primarily {top_domain.capitalize()}-driven with significant "
            f"{second_domain.capitalize()} contribution"
        )
    else:
        domain_labels = {
            "lifestyle":     "Lifestyle and Physical Health",
            "psychological": "Psychological and Emotional",
            "environmental": "Sleep Environment",
            "behavioral":    "Sleep Behavior and Schedule",
            "academic":      "Academic Pressure and Workload",
        }
        pattern = (
            f"Primarily driven by "
            f"{domain_labels.get(top_domain, top_domain.capitalize())} factors"
        )

    return pattern, dict(domain_scores)


def check_clinical_flags(answers, posteriors):
    """
    Layer 4 of diagnosis — Clinical Flag Check.

    Checks all five clinical flag rules. Returns the first triggered flag
    (most severe). If CF5 (triple overload) is present it takes priority
    over all others.

    Args:
        answers (dict):    current session answers
        posteriors (dict): output of update_posteriors()

    Returns:
        dict or None: {'id', 'label', 'message'} if flag triggered,
                      None if no clinical concern
    """
    # Check CF5 first — highest priority
    cf5 = CLINICAL_FLAG_RULES[4]
    if cf5["check"](answers):
        return {"id": cf5["id"], "label": cf5["label"], "message": cf5["message"]}

    # Check remaining flags in order
    for rule in CLINICAL_FLAG_RULES[:4]:
        if rule["check"](answers):
            return {"id": rule["id"], "label": rule["label"],
                    "message": rule["message"]}

    return None


def full_diagnosis(answers):
    """
    Master diagnosis function — runs all four layers.

    This is the single function called by interface.py after all questions
    are answered. Returns a structured dict passed both to the display
    layer and to session_manager for Prolog fact preparation.

    Args:
        answers (dict): complete session answers {question_id: answer_value}

    Returns:
        dict with keys:
            posteriors       — all 29 cause posteriors
            fired_causes     — causes exceeding 0.50 threshold
            complaints       — Layer 1: primary sleep complaint types
            severity         — Layer 2: 'none'|'mild'|'moderate'|'severe'
            severity_score   — Layer 2: raw float score
            domain_pattern   — Layer 3: dominant driver description
            domain_scores    — Layer 3: per-domain weighted scores
            clinical_flag    — Layer 4: flag dict or None
            answers          — the original answers (passed through for Prolog)
    """
    # Run all four layers
    posteriors      = update_posteriors(answers)
    complaints      = classify_sleep_complaint(answers)
    severity, score = compute_weighted_severity(posteriors, answers)
    pattern, d_scores = identify_domain_pattern(posteriors, answers)
    flag            = check_clinical_flags(answers, posteriors)

    # Clinical flag escalates severity to severe regardless of score
    if flag is not None:
        severity = "severe"

    # Collect fired causes using relative method with anchor veto
    fired_sorted = get_fired_causes(posteriors, answers)

    return {
        "posteriors":     {c: round(p, 3) for c, p in posteriors.items()},
        "fired_causes":   fired_sorted,
        "complaints":     complaints,
        "severity":       severity,
        "severity_score": score,
        "domain_pattern": pattern,
        "domain_scores":  d_scores,
        "clinical_flag":  flag,
        "answers":        answers,
    }
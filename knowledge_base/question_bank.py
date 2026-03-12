# =============================================================================
# SleepWise — question_bank.py
# Single source of truth for all 120 questions.
#
# Structure of each entry:
#   id        : Prolog-safe atom (lowercase, underscores). Bridge to Prolog.
#   number    : Original question number (1-120) for reference.
#   domain    : lifestyle | psychological | environmental | behavioral | academic
#   text      : Full question text shown to the user.
#   options   : List of {label, value} dicts.
#               label → what the user sees.
#               value → Prolog-safe atom asserted as user_fact(id, value).
#   core_from : q20 | q30 | q40 | q50 | addon
#               The earliest variant in which this question is a CORE.
#               addon = always conditional, never a core.
#   gain      : Estimated entropy gain (bits). Used for core ranking.
#   evidence  : Source citation for documentation.
# =============================================================================

QUESTION_BANK = [

    # =========================================================================
    # DOMAIN 1: LIFESTYLE
    # 20 questions — Q1-Q11 (original) + Q62-Q70, Q9 (expanded)
    # Cores: Q1, Q3, Q2 (q20) | Q4, Q11 (q30) | Q6, Q8 (q40) | Q5, Q7, Q10 (q50)
    # =========================================================================

    {
        "id":        "caffeine_intake",
        "number":    1,
        "domain":    "lifestyle",
        "text":      "How would you describe your daily caffeine consumption "
                     "(coffee, tea, energy drinks)?",
        "options": [
            {"label": "None",             "value": "none"},
            {"label": "Low (1-2 cups)",   "value": "low"},
            {"label": "Medium (3-4 cups)","value": "medium"},
            {"label": "High (5+ cups)",   "value": "high"},
        ],
        "core_from": "q20",
        "gain":      0.56,
        "evidence":  "NSF: Caffeine disrupts sleep onset; top predictor in "
                     "PSQI disturbances (web:0, web:10)",
    },

    {
        "id":        "heavy_meal_before_bed",
        "number":    2,
        "domain":    "lifestyle",
        "text":      "How often do you eat heavy or spicy meals within "
                     "3 hours of bedtime?",
        "options": [
            {"label": "Never",                  "value": "never"},
            {"label": "Rarely (1-2×/week)",     "value": "rarely"},
            {"label": "Often (3-5×/week)",      "value": "often"},
            {"label": "Always (daily)",         "value": "always"},
        ],
        "core_from": "q20",
        "gain":      0.48,
        "evidence":  "PSQI: Heavy meals raise disturbances score; "
                     "explains 15% variance (web:2, web:7)",
    },

    {
        "id":        "physical_activity_level",
        "number":    3,
        "domain":    "lifestyle",
        "text":      "How many days per week do you engage in moderate "
                     "exercise (e.g., walking, gym) for 30+ minutes?",
        "options": [
            {"label": "0 days",   "value": "none"},
            {"label": "1-2 days", "value": "low"},
            {"label": "3-4 days", "value": "moderate"},
            {"label": "5+ days",  "value": "high"},
        ],
        "core_from": "q20",
        "gain":      0.52,
        "evidence":  "AASM: Exercise timing/frequency strongly impacts "
                     "sleep quality (web:6, web:10)",
    },

    {
        "id":        "alcohol_consumption",
        "number":    4,
        "domain":    "lifestyle",
        "text":      "How often do you drink alcohol in the evening "
                     "(within 4 hours of bed)?",
        "options": [
            {"label": "Never",              "value": "never"},
            {"label": "Rarely (1-2×/week)", "value": "rarely"},
            {"label": "Often (3-5×/week)",  "value": "often"},
            {"label": "Daily",              "value": "daily"},
        ],
        "core_from": "q30",
        "gain":      0.51,
        "evidence":  "CDC: Evening alcohol suppresses REM sleep, "
                     "increasing wakeups (web:1, web:3)",
    },

    {
        "id":        "tobacco_use",
        "number":    5,
        "domain":    "lifestyle",
        "text":      "How would you describe your smoking or exposure "
                     "to secondhand smoke?",
        "options": [
            {"label": "None",                        "value": "none"},
            {"label": "Occasional smoker/exposure",  "value": "occasional"},
            {"label": "Regular smoker/exposure (daily)", "value": "regular"},
        ],
        "core_from": "q50",
        "gain":      0.38,
        "evidence":  "NSF: Nicotine is a stimulant; smokers have 25% "
                     "higher insomnia rates (web:0, web:10)",
    },

    {
        "id":        "hydration_habits",
        "number":    6,
        "domain":    "lifestyle",
        "text":      "How many glasses of water (or non-caffeinated fluids) "
                     "do you drink daily?",
        "options": [
            {"label": "Less than 4",  "value": "very_low"},
            {"label": "4-6 glasses",  "value": "low"},
            {"label": "7-8 glasses",  "value": "adequate"},
            {"label": "More than 8",  "value": "high"},
        ],
        "core_from": "q40",
        "gain":      0.41,
        "evidence":  "NSF: Dehydration causes restlessness; optimal hydration "
                     "improves sleep quality (web:0, web:10)",
    },

    {
        "id":        "diet_consistency",
        "number":    7,
        "domain":    "lifestyle",
        "text":      "How regular are your meal times each day?",
        "options": [
            {"label": "Very regular (same times daily)",       "value": "very_regular"},
            {"label": "Somewhat regular (varies by 1-2 hrs)", "value": "somewhat_regular"},
            {"label": "Irregular (no set times)",             "value": "irregular"},
        ],
        "core_from": "q50",
        "gain":      0.36,
        "evidence":  "Studies: Irregular eating disrupts circadian rhythms "
                     "and melatonin (web:7, web:12)",
    },

    {
        "id":        "snacking_at_night",
        "number":    8,
        "domain":    "lifestyle",
        "text":      "How often do you eat snacks or light meals after "
                     "dinner but before bed?",
        "options": [
            {"label": "Never",                  "value": "never"},
            {"label": "Rarely (1-2 nights/wk)", "value": "rarely"},
            {"label": "Often (3-5 nights/wk)",  "value": "often"},
            {"label": "Always (every night)",   "value": "always"},
        ],
        "core_from": "q40",
        "gain":      0.39,
        "evidence":  "PSQI: Nighttime snacking disrupts gastric processes "
                     "and sleep onset (web:2, web:7)",
    },

    {
        "id":        "food_insecurity",
        "number":    9,
        "domain":    "lifestyle",
        "text":      "How often do you skip meals or worry about "
                     "affording food?",
        "options": [
            {"label": "Never",                    "value": "never"},
            {"label": "Rarely (1-2×/month)",      "value": "rarely"},
            {"label": "Often (weekly)",           "value": "often"},
            {"label": "Frequently",               "value": "frequently"},
        ],
        "core_from": "addon",
        "gain":      0.30,
        "evidence":  "CDC: Food insecurity links to elevated cortisol and "
                     "disrupted sleep in 30% of students (web:1, web:3)",
    },

    {
        "id":        "medication_supplements",
        "number":    10,
        "domain":    "lifestyle",
        "text":      "Do you take any medications or supplements that might "
                     "affect sleep (e.g., stimulants, sleep aids)?",
        "options": [
            {"label": "No",                          "value": "no"},
            {"label": "Yes – occasional",            "value": "occasional"},
            {"label": "Yes – daily, non-prescription","value": "daily_nonrx"},
            {"label": "Yes – prescription",          "value": "daily_rx"},
        ],
        "core_from": "q50",
        "gain":      0.40,
        "evidence":  "CDC: Stimulant medications (ADHD, antidepressants) "
                     "alter sleep architecture (web:1, web:3)",
    },

    {
        "id":        "caffeine_timing",
        "number":    11,
        "domain":    "lifestyle",
        "text":      "When do you typically consume your last caffeinated "
                     "drink of the day?",
        "options": [
            {"label": "Morning only",              "value": "morning"},
            {"label": "Afternoon (before 3 PM)",   "value": "afternoon"},
            {"label": "Evening (after 3 PM)",      "value": "evening"},
            {"label": "Late night (after 8 PM)",   "value": "late_night"},
        ],
        "core_from": "q30",
        "gain":      0.53,
        "evidence":  "NSF: Late caffeine delays sleep onset by 1-2 hrs "
                     "in 60% of consumers (web:0, web:10)",
    },

    {
        "id":        "sugary_food_intake",
        "number":    62,
        "domain":    "lifestyle",
        "text":      "How often do you consume sugary foods or drinks "
                     "in the evening?",
        "options": [
            {"label": "Never",              "value": "never"},
            {"label": "Rarely (1-2×/wk)",   "value": "rarely"},
            {"label": "Often (3-5×/wk)",    "value": "often"},
            {"label": "Daily",              "value": "daily"},
        ],
        "core_from": "addon",
        "gain":      0.28,
        "evidence":  "NSF: Sugar spikes disrupt sleep onset in 30% "
                     "of students (web:0, web:1)",
    },

    {
        "id":        "exercise_timing",
        "number":    63,
        "domain":    "lifestyle",
        "text":      "When do you usually exercise relative to bedtime?",
        "options": [
            {"label": "Morning",                        "value": "morning"},
            {"label": "Afternoon",                      "value": "afternoon"},
            {"label": "Evening (2-4 hours before bed)", "value": "evening"},
            {"label": "Late night (within 2 hours)",    "value": "late_night"},
        ],
        "core_from": "addon",
        "gain":      0.35,
        "evidence":  "AASM: Late exercise elevates core temp, delaying "
                     "sleep in 20-40% (web:6, web:10)",
    },

    {
        "id":        "dietary_allergies",
        "number":    64,
        "domain":    "lifestyle",
        "text":      "Do you have food allergies or intolerances that "
                     "cause discomfort at night?",
        "options": [
            {"label": "No",                    "value": "no"},
            {"label": "Mild (rare symptoms)",  "value": "mild"},
            {"label": "Moderate (weekly)",     "value": "moderate"},
            {"label": "Severe (daily)",        "value": "severe"},
        ],
        "core_from": "addon",
        "gain":      0.26,
        "evidence":  "CDC: Allergies link to sleep disturbances in 25% "
                     "of sufferers (web:1, web:3)",
    },

    {
        "id":        "meal_size_variation",
        "number":    65,
        "domain":    "lifestyle",
        "text":      "How would you describe the size of your "
                     "evening meals?",
        "options": [
            {"label": "Small/light", "value": "small"},
            {"label": "Medium",      "value": "medium"},
            {"label": "Large/heavy", "value": "large"},
            {"label": "Variable",    "value": "variable"},
        ],
        "core_from": "addon",
        "gain":      0.29,
        "evidence":  "PSQI: Large meals increase acid reflux and "
                     "disturbances (web:2, web:7)",
    },

    {
        "id":        "nicotine_alternatives",
        "number":    66,
        "domain":    "lifestyle",
        "text":      "How often do you use e-cigarettes or vaping products?",
        "options": [
            {"label": "Never",              "value": "never"},
            {"label": "Rarely (1-2×/wk)",   "value": "rarely"},
            {"label": "Often (3-5×/wk)",    "value": "often"},
            {"label": "Daily",              "value": "daily"},
        ],
        "core_from": "addon",
        "gain":      0.27,
        "evidence":  "NSF: Nicotine from vaping disrupts REM in 15-30% "
                     "of young adults (web:0, web:10)",
    },

    {
        "id":        "fluid_intake_timing",
        "number":    67,
        "domain":    "lifestyle",
        "text":      "When do you have your last drink (any fluid) "
                     "before bed?",
        "options": [
            {"label": "More than 2 hours before bed", "value": "early"},
            {"label": "1-2 hours before bed",         "value": "moderate"},
            {"label": "Within 1 hour of bed",         "value": "late"},
            {"label": "In bed",                       "value": "in_bed"},
        ],
        "core_from": "addon",
        "gain":      0.31,
        "evidence":  "AASM: Late fluids cause nocturia (waking to urinate) "
                     "in 40% of sleepers (web:6, web:17)",
    },

    {
        "id":        "supplement_timing",
        "number":    68,
        "domain":    "lifestyle",
        "text":      "When do you take vitamins or supplements that "
                     "might energize you?",
        "options": [
            {"label": "Morning",        "value": "morning"},
            {"label": "Afternoon",      "value": "afternoon"},
            {"label": "Evening",        "value": "evening"},
            {"label": "Not applicable", "value": "not_applicable"},
        ],
        "core_from": "addon",
        "gain":      0.24,
        "evidence":  "CDC: B-vitamins and stimulant-like supplements "
                     "disrupt sleep when taken late (web:1, web:15)",
    },

    {
        "id":        "fasting_habits",
        "number":    69,
        "domain":    "lifestyle",
        "text":      "How often do you practice intermittent fasting "
                     "or skip dinner?",
        "options": [
            {"label": "Never",                  "value": "never"},
            {"label": "Rarely (1-2 days/wk)",   "value": "rarely"},
            {"label": "Often (3-5 days/wk)",    "value": "often"},
            {"label": "Daily",                  "value": "daily"},
        ],
        "core_from": "addon",
        "gain":      0.25,
        "evidence":  "Studies: Irregular eating windows affect circadian "
                     "rhythms and cortisol (web:7, web:12)",
    },

    {
        "id":        "recreational_drug_use",
        "number":    70,
        "domain":    "lifestyle",
        "text":      "How often do you use recreational drugs "
                     "(e.g., marijuana)?",
        "options": [
            {"label": "Never",              "value": "never"},
            {"label": "Rarely (monthly)",   "value": "rarely"},
            {"label": "Often (weekly)",     "value": "often"},
            {"label": "Frequently",         "value": "frequently"},
        ],
        "core_from": "addon",
        "gain":      0.33,
        "evidence":  "NSF: Cannabis can aid or impair sleep depending on "
                     "frequency and type of use (web:0, web:10)",
    },


    # =========================================================================
    # DOMAIN 2: PSYCHOLOGICAL
    # 32 questions — Q12-Q23 (original) + Q71-Q80 (expanded) + Q111-Q120
    # Cores: Q12, Q14, Q15 (q20) | Q13, Q17 (q30) | Q18, Q22 (q40)
    #        Q16, Q19, Q20 (q50) | rest addon
    # =========================================================================

    {
        "id":        "stress_level",
        "number":    12,
        "domain":    "psychological",
        "text":      "How would you rate your overall stress level "
                     "in the past week?",
        "options": [
            {"label": "Low",    "value": "low"},
            {"label": "Medium", "value": "medium"},
            {"label": "High",   "value": "high"},
        ],
        "core_from": "q20",
        "gain":      0.88,
        "evidence":  "Wang 2023: Stress top mediator of sleep quality — "
                     "35% variance; Okano 2019: top 25% academic impact "
                     "(web:5, web:6)",
    },

    {
        "id":        "depression_symptoms",
        "number":    14,
        "domain":    "psychological",
        "text":      "In the past week, how often have you felt "
                     "depressed or hopeless?",
        "options": [
            {"label": "Never",               "value": "never"},
            {"label": "Rarely (1-2 days)",   "value": "rarely"},
            {"label": "Often (3-5 days)",    "value": "often"},
            {"label": "Every day",           "value": "every_day"},
        ],
        "core_from": "q20",
        "gain":      0.72,
        "evidence":  "DASS-21/PHQ-9: Depression explains 50% variance "
                     "in insomnia; Mbous 2022 top predictor (web:2, web:5)",
    },

    {
        "id":        "anxiety_levels",
        "number":    15,
        "domain":    "psychological",
        "text":      "How often do you experience anxiety or tension "
                     "that keeps you up at night?",
        "options": [
            {"label": "Never",                   "value": "never"},
            {"label": "Rarely (1-2 nights/wk)",  "value": "rarely"},
            {"label": "Often (3-5 nights/wk)",   "value": "often"},
            {"label": "Every night",             "value": "every_night"},
        ],
        "core_from": "q20",
        "gain":      0.70,
        "evidence":  "ISI: Anxiety severity top-3 predictor of sleep "
                     "onset delay and quality (web:5, web:8)",
    },

    {
        "id":        "worry_before_bed",
        "number":    13,
        "domain":    "psychological",
        "text":      "How often do you find yourself worrying or "
                     "overthinking right before bed?",
        "options": [
            {"label": "Never",                   "value": "never"},
            {"label": "Rarely (1-2 nights/wk)",  "value": "rarely"},
            {"label": "Often (3-5 nights/wk)",   "value": "often"},
            {"label": "Always (every night)",    "value": "always"},
        ],
        "core_from": "q30",
        "gain":      0.65,
        "evidence":  "PSQI: Pre-sleep cognitive arousal explains 20-30% "
                     "of insomnia variance (web:2, web:7)",
    },

    {
        "id":        "burnout_feelings",
        "number":    17,
        "domain":    "psychological",
        "text":      "How often do you feel burned out from "
                     "studies or work?",
        "options": [
            {"label": "Never",                "value": "never"},
            {"label": "Rarely (once/month)",  "value": "rarely"},
            {"label": "Often (weekly)",       "value": "often"},
            {"label": "Constantly",           "value": "constantly"},
        ],
        "core_from": "q30",
        "gain":      0.60,
        "evidence":  "Stores 2023: Burnout mediates sleep quality decline "
                     "in university students (web:9, web:16)",
    },

    {
        "id":        "self_control_routines",
        "number":    18,
        "domain":    "psychological",
        "text":      "How good are you at sticking to planned bedtime "
                     "or study schedules?",
        "options": [
            {"label": "Very good (always follow)",  "value": "very_good"},
            {"label": "Fair (mostly follow)",       "value": "fair"},
            {"label": "Poor (often deviate)",       "value": "poor"},
        ],
        "core_from": "q40",
        "gain":      0.55,
        "evidence":  "Wang 2023: Self-control mediates bedtime/sleep "
                     "quality relationship — 35% effect (web:6, web:18)",
    },

    {
        "id":        "sleep_disorders",
        "number":    22,
        "domain":    "psychological",
        "text":      "Have you been diagnosed with or do you suspect "
                     "a sleep disorder (e.g., insomnia, sleep apnea)?",
        "options": [
            {"label": "No",                        "value": "no"},
            {"label": "Suspected but undiagnosed", "value": "suspected"},
            {"label": "Diagnosed — mild",          "value": "diagnosed_mild"},
            {"label": "Diagnosed — severe",        "value": "diagnosed_severe"},
        ],
        "core_from": "q40",
        "gain":      0.58,
        "evidence":  "ISI/PSQI: Clinical disorders directly explain "
                     "50-70% of outcome variance (web:5, web:8)",
    },

    {
        "id":        "adhd_symptoms",
        "number":    16,
        "domain":    "psychological",
        "text":      "Do you have difficulty focusing or hyperactivity "
                     "that affects your daily routine?",
        "options": [
            {"label": "No",                                    "value": "no"},
            {"label": "Mild (occasional issues)",              "value": "mild"},
            {"label": "Moderate (frequent but manageable)",   "value": "moderate"},
            {"label": "Severe (daily disruption)",            "value": "severe"},
        ],
        "core_from": "q50",
        "gain":      0.48,
        "evidence":  "Mbous 2022: ADHD predicts 50% insomnia risk "
                     "in student populations (web:5, web:8)",
    },

    {
        "id":        "general_worries",
        "number":    19,
        "domain":    "psychological",
        "text":      "How often do non-academic worries (e.g., future "
                     "career, relationships) affect your thoughts at night?",
        "options": [
            {"label": "Never",                   "value": "never"},
            {"label": "Rarely (1-2 nights/wk)",  "value": "rarely"},
            {"label": "Often (3-5 nights/wk)",   "value": "often"},
            {"label": "Always",                  "value": "always"},
        ],
        "core_from": "q50",
        "gain":      0.45,
        "evidence":  "CDC: Generalized worry is independent predictor "
                     "of poor sleep onset (web:1, web:3)",
    },

    {
        "id":        "financial_stress",
        "number":    20,
        "domain":    "psychological",
        "text":      "How often does financial worry (e.g., tuition, "
                     "living costs) affect you?",
        "options": [
            {"label": "Never",              "value": "never"},
            {"label": "Rarely (monthly)",   "value": "rarely"},
            {"label": "Often (weekly)",     "value": "often"},
            {"label": "Constantly",         "value": "constantly"},
        ],
        "core_from": "q50",
        "gain":      0.44,
        "evidence":  "Mbous 2022: Financial stress adds 20% to insomnia "
                     "prediction in lower-SES students (web:5, web:8)",
    },

    {
        "id":        "discrimination_experiences",
        "number":    21,
        "domain":    "psychological",
        "text":      "Have you faced discrimination (e.g., based on race "
                     "or gender) at university in the past month?",
        "options": [
            {"label": "No",                          "value": "no"},
            {"label": "Yes — mild/occasional",       "value": "mild"},
            {"label": "Yes — frequent/impactful",    "value": "frequent"},
        ],
        "core_from": "addon",
        "gain":      0.32,
        "evidence":  "CDC: Minority stress from discrimination increases "
                     "insomnia risk by 30% (web:1, web:3)",
    },

    {
        "id":        "trauma_or_grief",
        "number":    23,
        "domain":    "psychological",
        "text":      "Have recent events (e.g., loss, trauma) been "
                     "affecting your mental state?",
        "options": [
            {"label": "No",                        "value": "no"},
            {"label": "Yes — mild impact",         "value": "mild"},
            {"label": "Yes — moderate impact",     "value": "moderate"},
            {"label": "Yes — significant impact",  "value": "significant"},
        ],
        "core_from": "addon",
        "gain":      0.38,
        "evidence":  "Mbous 2022: Trauma/grief elevates stress hormones "
                     "causing insomnia in 40% (web:5, web:8)",
    },

    {
        "id":        "loneliness_levels",
        "number":    71,
        "domain":    "psychological",
        "text":      "How often do you feel lonely or isolated?",
        "options": [
            {"label": "Never",              "value": "never"},
            {"label": "Rarely (monthly)",   "value": "rarely"},
            {"label": "Often (weekly)",     "value": "often"},
            {"label": "Constantly",         "value": "constantly"},
        ],
        "core_from": "addon",
        "gain":      0.36,
        "evidence":  "Mbous 2022: Loneliness links to depression and "
                     "insomnia in 40% of students (web:5, web:8)",
    },

    {
        "id":        "perfectionism_tendencies",
        "number":    72,
        "domain":    "psychological",
        "text":      "How often do you set unrealistically high "
                     "standards for yourself?",
        "options": [
            {"label": "Never",   "value": "never"},
            {"label": "Rarely",  "value": "rarely"},
            {"label": "Often",   "value": "often"},
            {"label": "Always",  "value": "always"},
        ],
        "core_from": "addon",
        "gain":      0.34,
        "evidence":  "Stores 2023: Perfectionism strongly correlates "
                     "with anxiety and sleep disturbances",
    },

    {
        "id":        "rumination_habits",
        "number":    73,
        "domain":    "psychological",
        "text":      "How often do you replay negative events in "
                     "your mind at night?",
        "options": [
            {"label": "Never",                   "value": "never"},
            {"label": "Rarely (1-2 nights/wk)",  "value": "rarely"},
            {"label": "Often (3-5 nights/wk)",   "value": "often"},
            {"label": "Always",                  "value": "always"},
        ],
        "core_from": "addon",
        "gain":      0.40,
        "evidence":  "DASS-21: Rumination amplifies stress response "
                     "in 50% of anxious individuals (web:2, web:5)",
    },

    {
        "id":        "resilience_level",
        "number":    74,
        "domain":    "psychological",
        "text":      "How well do you bounce back from setbacks?",
        "options": [
            {"label": "Very well",   "value": "very_well"},
            {"label": "Fairly well", "value": "fairly_well"},
            {"label": "Poorly",      "value": "poorly"},
            {"label": "Very poorly", "value": "very_poorly"},
        ],
        "core_from": "addon",
        "gain":      0.33,
        "evidence":  "Wang 2023: Low resilience predicts poor sleep "
                     "quality in 30% of students",
    },

    {
        "id":        "mindfulness_practice",
        "number":    75,
        "domain":    "psychological",
        "text":      "How often do you practice mindfulness "
                     "or meditation?",
        "options": [
            {"label": "Never",              "value": "never"},
            {"label": "Rarely (monthly)",   "value": "rarely"},
            {"label": "Often (weekly)",     "value": "often"},
            {"label": "Daily",              "value": "daily"},
        ],
        "core_from": "addon",
        "gain":      0.30,
        "evidence":  "AASM: Mindfulness reduces anxiety and sleep "
                     "latency significantly (web:0, web:6)",
    },

    {
        "id":        "guilt_feelings",
        "number":    76,
        "domain":    "psychological",
        "text":      "How often do you feel guilty about not sleeping "
                     "well or underperforming?",
        "options": [
            {"label": "Never",   "value": "never"},
            {"label": "Rarely",  "value": "rarely"},
            {"label": "Often",   "value": "often"},
            {"label": "Always",  "value": "always"},
        ],
        "core_from": "addon",
        "gain":      0.28,
        "evidence":  "PSQI: Guilt cycles worsen sleep dysfunction "
                     "and increase latency (web:2, web:7)",
    },

    {
        "id":        "optimism_outlook",
        "number":    77,
        "domain":    "psychological",
        "text":      "How optimistic are you about your future?",
        "options": [
            {"label": "Very optimistic",  "value": "very_optimistic"},
            {"label": "Somewhat",         "value": "somewhat"},
            {"label": "Not very",         "value": "not_very"},
            {"label": "Pessimistic",      "value": "pessimistic"},
        ],
        "core_from": "addon",
        "gain":      0.26,
        "evidence":  "CDC: Low optimism links to mental distress "
                     "and disrupted sleep (web:1, web:3)",
    },

    {
        "id":        "emotional_regulation",
        "number":    78,
        "domain":    "psychological",
        "text":      "How well can you manage strong emotions "
                     "before bed?",
        "options": [
            {"label": "Very well",   "value": "very_well"},
            {"label": "Fairly well", "value": "fairly_well"},
            {"label": "Poorly",      "value": "poorly"},
            {"label": "Very poorly", "value": "very_poorly"},
        ],
        "core_from": "addon",
        "gain":      0.31,
        "evidence":  "Altun 2012: Poor emotional regulation causes "
                     "sleep disturbances in students",
    },

    {
        "id":        "attachment_style",
        "number":    79,
        "domain":    "psychological",
        "text":      "How would you describe your close relationships "
                     "(e.g., secure, anxious)?",
        "options": [
            {"label": "Secure",       "value": "secure"},
            {"label": "Anxious",      "value": "anxious"},
            {"label": "Avoidant",     "value": "avoidant"},
            {"label": "Disorganized", "value": "disorganized"},
        ],
        "core_from": "addon",
        "gain":      0.22,
        "evidence":  "Studies: Anxious attachment increases worry "
                     "and sleep issues (web:5, web:8)",
    },

    {
        "id":        "seasonal_mood_changes",
        "number":    80,
        "domain":    "psychological",
        "text":      "Do seasons affect your mood or sleep "
                     "(e.g., winter blues)?",
        "options": [
            {"label": "No",                       "value": "no"},
            {"label": "Mildly (occasional)",      "value": "mild"},
            {"label": "Moderately (seasonal)",    "value": "moderate"},
            {"label": "Severely",                 "value": "severe"},
        ],
        "core_from": "addon",
        "gain":      0.24,
        "evidence":  "NSF: Seasonal Affective Disorder affects 10-20% "
                     "of young adults (web:0, web:10)",
    },

    {
        "id":        "panic_attacks",
        "number":    111,
        "domain":    "psychological",
        "text":      "How often do you experience panic attacks?",
        "options": [
            {"label": "Never",              "value": "never"},
            {"label": "Rarely (monthly)",   "value": "rarely"},
            {"label": "Often (weekly)",     "value": "often"},
            {"label": "Frequently",         "value": "frequently"},
        ],
        "core_from": "addon",
        "gain":      0.37,
        "evidence":  "DASS-21: Panic attacks directly link to "
                     "anxiety-driven sleep disruption (web:2, web:5)",
    },

    {
        "id":        "therapy_attendance",
        "number":    112,
        "domain":    "psychological",
        "text":      "How often do you attend therapy or counseling?",
        "options": [
            {"label": "Never",               "value": "never"},
            {"label": "Occasionally",        "value": "occasionally"},
            {"label": "Regularly (monthly)", "value": "regularly"},
            {"label": "Weekly",              "value": "weekly"},
        ],
        "core_from": "addon",
        "gain":      0.29,
        "evidence":  "AASM: Therapy/CBT-I improves mental health and "
                     "sleep in 60% of insomnia patients (web:0, web:6)",
    },

    {
        "id":        "mood_swings",
        "number":    113,
        "domain":    "psychological",
        "text":      "How often do you have mood swings that "
                     "affect your sleep?",
        "options": [
            {"label": "Never",   "value": "never"},
            {"label": "Rarely",  "value": "rarely"},
            {"label": "Often",   "value": "often"},
            {"label": "Daily",   "value": "daily"},
        ],
        "core_from": "addon",
        "gain":      0.31,
        "evidence":  "Studies: Bipolar-like mood symptoms disrupt "
                     "sleep in 20% of young adults (web:7, web:9)",
    },

    {
        "id":        "gratitude_practice",
        "number":    114,
        "domain":    "psychological",
        "text":      "How often do you practice gratitude "
                     "(e.g., journaling positives)?",
        "options": [
            {"label": "Never",   "value": "never"},
            {"label": "Rarely",  "value": "rarely"},
            {"label": "Often",   "value": "often"},
            {"label": "Daily",   "value": "daily"},
        ],
        "core_from": "addon",
        "gain":      0.22,
        "evidence":  "NSF: Gratitude practice boosts optimism and "
                     "improves sleep quality (web:0, web:10)",
    },

    {
        "id":        "fear_of_failure",
        "number":    115,
        "domain":    "psychological",
        "text":      "How strong is your fear of academic failure?",
        "options": [
            {"label": "None",     "value": "none"},
            {"label": "Mild",     "value": "mild"},
            {"label": "Moderate", "value": "moderate"},
            {"label": "Strong",   "value": "strong"},
        ],
        "core_from": "addon",
        "gain":      0.35,
        "evidence":  "Mbous 2022: Fear of failure correlates with "
                     "stress and insomnia severity",
    },

    {
        "id":        "social_comparison",
        "number":    116,
        "domain":    "psychological",
        "text":      "How often do you compare yourself to peers "
                     "academically?",
        "options": [
            {"label": "Never",   "value": "never"},
            {"label": "Rarely",  "value": "rarely"},
            {"label": "Often",   "value": "often"},
            {"label": "Always",  "value": "always"},
        ],
        "core_from": "addon",
        "gain":      0.27,
        "evidence":  "CDC: Social comparison increases anxiety "
                     "in 40% of students (web:1, web:3)",
    },

    {
        "id":        "self_esteem_level",
        "number":    117,
        "domain":    "psychological",
        "text":      "How would you rate your self-esteem?",
        "options": [
            {"label": "High",     "value": "high"},
            {"label": "Medium",   "value": "medium"},
            {"label": "Low",      "value": "low"},
            {"label": "Very low", "value": "very_low"},
        ],
        "core_from": "addon",
        "gain":      0.28,
        "evidence":  "PSQI: Low self-esteem ties to sleep dysfunction "
                     "and rumination (web:2, web:7)",
    },

    {
        "id":        "boredom_frequency",
        "number":    118,
        "domain":    "psychological",
        "text":      "How often do you feel bored or unengaged "
                     "with your studies?",
        "options": [
            {"label": "Never",      "value": "never"},
            {"label": "Rarely",     "value": "rarely"},
            {"label": "Often",      "value": "often"},
            {"label": "Constantly", "value": "constantly"},
        ],
        "core_from": "addon",
        "gain":      0.21,
        "evidence":  "Studies: Boredom leads to procrastination and "
                     "irregular sleep patterns (web:7, web:12)",
    },

    {
        "id":        "forgiveness_practices",
        "number":    119,
        "domain":    "psychological",
        "text":      "How often do you forgive yourself "
                     "for mistakes?",
        "options": [
            {"label": "Always",  "value": "always"},
            {"label": "Often",   "value": "often"},
            {"label": "Rarely",  "value": "rarely"},
            {"label": "Never",   "value": "never"},
        ],
        "core_from": "addon",
        "gain":      0.20,
        "evidence":  "NSF: Self-forgiveness reduces guilt-driven "
                     "sleep latency (web:0, web:10)",
    },

    {
        "id":        "existential_worries",
        "number":    120,
        "domain":    "psychological",
        "text":      "How often do you worry about life's purpose "
                     "or direction?",
        "options": [
            {"label": "Never",      "value": "never"},
            {"label": "Rarely",     "value": "rarely"},
            {"label": "Often",      "value": "often"},
            {"label": "Always",     "value": "always"},
        ],
        "core_from": "addon",
        "gain":      0.22,
        "evidence":  "Altun 2012: Existential anxiety affects 25% "
                     "of young adults and delays sleep onset",
    },


    # =========================================================================
    # DOMAIN 3: ENVIRONMENTAL
    # 20 questions — Q24-Q33 (original) + Q81-Q90 (expanded)
    # Cores: Q24, Q25, Q26 (q20) | Q28, Q30 (q30) | Q29, Q27 (q40)
    #        Q31, Q33 (q50) | rest addon
    # =========================================================================

    {
        "id":        "noisy_environment",
        "number":    24,
        "domain":    "environmental",
        "text":      "How would you describe the noise level in your "
                     "sleeping environment at night?",
        "options": [
            {"label": "Quiet",                             "value": "quiet"},
            {"label": "Some noise (occasional)",           "value": "some_noise"},
            {"label": "Loud (frequent or constant noise)", "value": "loud"},
        ],
        "core_from": "q20",
        "gain":      0.60,
        "evidence":  "Altun 2012: Noise is top-3 environmental predictor; "
                     "disrupts sleep in 50%+ students (web:3, web:16)",
    },

    {
        "id":        "light_exposure_at_night",
        "number":    25,
        "domain":    "environmental",
        "text":      "How often are you exposed to bright lights "
                     "(e.g., streetlights, roommates) during bedtime hours?",
        "options": [
            {"label": "Never",                   "value": "never"},
            {"label": "Rarely (1-2 nights/wk)",  "value": "rarely"},
            {"label": "Often (3-5 nights/wk)",   "value": "often"},
            {"label": "Always (every night)",    "value": "always"},
        ],
        "core_from": "q20",
        "gain":      0.58,
        "evidence":  "AASM: Light suppresses melatonin, delaying sleep "
                     "in 40-60% of exposed individuals (web:0, web:6)",
    },

    {
        "id":        "uncomfortable_temperature",
        "number":    26,
        "domain":    "environmental",
        "text":      "How would you describe the temperature in your "
                     "room at night?",
        "options": [
            {"label": "Comfortable",  "value": "comfortable"},
            {"label": "Too hot",      "value": "too_hot"},
            {"label": "Too cold",     "value": "too_cold"},
        ],
        "core_from": "q20",
        "gain":      0.55,
        "evidence":  "CDC: Room temperature outside 65-68F is among "
                     "top environmental disruptors (web:1, web:3)",
    },

    {
        "id":        "neighborhood_safety",
        "number":    27,
        "domain":    "environmental",
        "text":      "How concerned are you about safety or violence "
                     "in your living area?",
        "options": [
            {"label": "Not concerned",       "value": "not_concerned"},
            {"label": "Mildly concerned",    "value": "mild"},
            {"label": "Moderately concerned","value": "moderate"},
            {"label": "Very concerned",      "value": "very_concerned"},
        ],
        "core_from": "q40",
        "gain":      0.44,
        "evidence":  "Altun 2012: Safety concerns elevate vigilance "
                     "and arousal, impairing sleep onset (web:3, web:16)",
    },

    {
        "id":        "room_air_quality",
        "number":    28,
        "domain":    "environmental",
        "text":      "How would you rate the air quality in your "
                     "bedroom (e.g., dust, pollution)?",
        "options": [
            {"label": "Excellent (fresh/clean)",        "value": "excellent"},
            {"label": "Fair (occasional issues)",       "value": "fair"},
            {"label": "Poor (stuffy/polluted often)",   "value": "poor"},
        ],
        "core_from": "q30",
        "gain":      0.48,
        "evidence":  "Wang 2023: Air quality mediates sleep environment "
                     "effects — 35% model fit (web:6, web:18)",
    },

    {
        "id":        "bed_comfort",
        "number":    29,
        "domain":    "environmental",
        "text":      "How comfortable is your mattress or bedding?",
        "options": [
            {"label": "Very comfortable",                  "value": "very_comfortable"},
            {"label": "Somewhat comfortable",             "value": "somewhat_comfortable"},
            {"label": "Uncomfortable (causes aches)",     "value": "uncomfortable"},
        ],
        "core_from": "q40",
        "gain":      0.42,
        "evidence":  "NSF: Uncomfortable sleep surfaces increase wakeups "
                     "and reduce deep sleep (web:0, web:10)",
    },

    {
        "id":        "shared_living",
        "number":    30,
        "domain":    "environmental",
        "text":      "Do you share your room or living space "
                     "with others (e.g., roommates)?",
        "options": [
            {"label": "No (live alone)",      "value": "alone"},
            {"label": "Yes (1-2 people)",     "value": "shared_small"},
            {"label": "Yes (3+ people)",      "value": "shared_large"},
        ],
        "core_from": "q30",
        "gain":      0.50,
        "evidence":  "PSQI: Shared living increases disturbance risk "
                     "by 25-35% (web:2, web:19)",
    },

    {
        "id":        "chronic_health_conditions",
        "number":    31,
        "domain":    "environmental",
        "text":      "Do you have any ongoing health issues "
                     "(e.g., allergies, asthma) that affect sleep?",
        "options": [
            {"label": "None",                    "value": "none"},
            {"label": "Mild (rare impact)",      "value": "mild"},
            {"label": "Moderate (weekly impact)","value": "moderate"},
            {"label": "Severe (daily)",          "value": "severe"},
        ],
        "core_from": "q50",
        "gain":      0.43,
        "evidence":  "Bousgheiri 2024: Chronic diseases rank high "
                     "as sleep disruptors",
    },

    {
        "id":        "pet_pest_disturbances",
        "number":    32,
        "domain":    "environmental",
        "text":      "How often do pets, insects, or pests "
                     "disrupt your sleep?",
        "options": [
            {"label": "Never",                     "value": "never"},
            {"label": "Rarely (1-2 nights/month)", "value": "rarely"},
            {"label": "Often (weekly)",            "value": "often"},
            {"label": "Frequently",                "value": "frequently"},
        ],
        "core_from": "addon",
        "gain":      0.28,
        "evidence":  "PSQI: Pet/pest disturbances add to sleep "
                     "fragmentation in 25% (web:2, web:19)",
    },

    {
        "id":        "humidity_levels",
        "number":    33,
        "domain":    "environmental",
        "text":      "How would you describe the humidity in your "
                     "room at night?",
        "options": [
            {"label": "Comfortable",                         "value": "comfortable"},
            {"label": "Too dry (causes throat irritation)",  "value": "too_dry"},
            {"label": "Too humid (feels sticky/moldy)",      "value": "too_humid"},
        ],
        "core_from": "q50",
        "gain":      0.38,
        "evidence":  "CDC: Humidity extremes contribute to breathing "
                     "disruptions and poor sleep (web:1, web:15)",
    },

    {
        "id":        "window_light_control",
        "number":    81,
        "domain":    "environmental",
        "text":      "Do you have curtains or blinds to effectively "
                     "block light in your room?",
        "options": [
            {"label": "Yes (effective)",          "value": "effective"},
            {"label": "Partial (some light leaks)","value": "partial"},
            {"label": "No (bright room)",         "value": "none"},
        ],
        "core_from": "addon",
        "gain":      0.32,
        "evidence":  "AASM: Inadequate light control reduces melatonin "
                     "in 40% of exposed individuals (web:0, web:6)",
    },

    {
        "id":        "ventilation_quality",
        "number":    82,
        "domain":    "environmental",
        "text":      "How well-ventilated is your room "
                     "(e.g., fresh air flow)?",
        "options": [
            {"label": "Excellent",       "value": "excellent"},
            {"label": "Fair",            "value": "fair"},
            {"label": "Poor (stale air)","value": "poor"},
        ],
        "core_from": "addon",
        "gain":      0.30,
        "evidence":  "CDC: Poor ventilation causes CO2 buildup and "
                     "fatigue in 20% of residents (web:1, web:15)",
    },

    {
        "id":        "electronic_devices_in_room",
        "number":    83,
        "domain":    "environmental",
        "text":      "How many electronic devices (e.g., chargers, fans) "
                     "make noise or emit light in your room?",
        "options": [
            {"label": "None",  "value": "none"},
            {"label": "1-2",   "value": "few"},
            {"label": "3-4",   "value": "several"},
            {"label": "5+",    "value": "many"},
        ],
        "core_from": "addon",
        "gain":      0.27,
        "evidence":  "NSF: Device noise and light disrupt sleep "
                     "in 30% of young adults (web:0, web:10)",
    },

    {
        "id":        "room_clutter",
        "number":    84,
        "domain":    "environmental",
        "text":      "How cluttered is your sleeping space?",
        "options": [
            {"label": "Minimal",                       "value": "minimal"},
            {"label": "Moderate",                      "value": "moderate"},
            {"label": "High (affects movement/mind)",  "value": "high"},
        ],
        "core_from": "addon",
        "gain":      0.24,
        "evidence":  "Studies: Visual clutter increases stress and "
                     "sleep latency (web:7, web:12)",
    },

    {
        "id":        "scent_in_room",
        "number":    85,
        "domain":    "environmental",
        "text":      "Are there strong scents (e.g., perfume, food) "
                     "in your room at night?",
        "options": [
            {"label": "No",                  "value": "no"},
            {"label": "Mild (pleasant)",     "value": "mild_pleasant"},
            {"label": "Moderate (neutral)",  "value": "moderate_neutral"},
            {"label": "Strong (disruptive)", "value": "strong_disruptive"},
        ],
        "core_from": "addon",
        "gain":      0.20,
        "evidence":  "Altun 2012: Odors can cause disturbances and "
                     "fragmented sleep in sensitive individuals",
    },

    {
        "id":        "partner_snoring",
        "number":    86,
        "domain":    "environmental",
        "text":      "If you share a bed, how often does your "
                     "partner's snoring disturb you?",
        "options": [
            {"label": "Not applicable", "value": "not_applicable"},
            {"label": "Never",          "value": "never"},
            {"label": "Rarely",         "value": "rarely"},
            {"label": "Often",          "value": "often"},
            {"label": "Always",         "value": "always"},
        ],
        "core_from": "addon",
        "gain":      0.26,
        "evidence":  "PSQI: Bed-partner snoring causes fragmented sleep "
                     "in 25% of shared sleepers (web:2, web:19)",
    },

    {
        "id":        "building_maintenance",
        "number":    87,
        "domain":    "environmental",
        "text":      "How often do building issues (e.g., leaky roof, "
                     "power outages) affect your sleep?",
        "options": [
            {"label": "Never",              "value": "never"},
            {"label": "Rarely (monthly)",   "value": "rarely"},
            {"label": "Often (weekly)",     "value": "often"},
            {"label": "Frequently",         "value": "frequently"},
        ],
        "core_from": "addon",
        "gain":      0.25,
        "evidence":  "CDC: Infrastructure issues disproportionately "
                     "impact low-SES student sleep (web:1, web:3)",
    },

    {
        "id":        "natural_light_exposure",
        "number":    88,
        "domain":    "environmental",
        "text":      "How much natural light do you get "
                     "during the day?",
        "options": [
            {"label": "A lot (outdoors often)",      "value": "high"},
            {"label": "Moderate",                    "value": "moderate"},
            {"label": "Little (indoors most of day)","value": "low"},
            {"label": "None",                        "value": "none"},
        ],
        "core_from": "addon",
        "gain":      0.29,
        "evidence":  "AASM: Daytime light regulates circadian rhythm; "
                     "deficiency worsens nighttime sleep (web:6, web:17)",
    },

    {
        "id":        "room_color_scheme",
        "number":    89,
        "domain":    "environmental",
        "text":      "How would you describe your room's colors?",
        "options": [
            {"label": "Calming (cool tones)",      "value": "calming"},
            {"label": "Neutral",                   "value": "neutral"},
            {"label": "Stimulating (bright/warm)", "value": "stimulating"},
            {"label": "Not sure",                  "value": "unsure"},
        ],
        "core_from": "addon",
        "gain":      0.14,
        "evidence":  "Studies: Blue/cool tones associated with improved "
                     "sleep quality (web:9, web:16)",
    },

    {
        "id":        "electromagnetic_exposure",
        "number":    90,
        "domain":    "environmental",
        "text":      "How close are Wi-Fi routers or phones "
                     "to your bed?",
        "options": [
            {"label": "Far away",                   "value": "far"},
            {"label": "Moderate distance",          "value": "moderate"},
            {"label": "Close (within arm's reach)", "value": "close"},
            {"label": "In bed",                     "value": "in_bed"},
        ],
        "core_from": "addon",
        "gain":      0.16,
        "evidence":  "NSF: Potential EMF disruption reported in 15%; "
                     "proximity increases stimulation risk (web:0, web:10)",
    },


    # =========================================================================
    # DOMAIN 4: BEHAVIORAL
    # 21 questions — Q34-Q44 (original) + Q91-Q100 (expanded)
    # Cores: Q34, Q35, Q36 (q20) | Q38, Q37 (q30) | Q43, Q42 (q40)
    #        Q41, Q44, Q40 (q50) | rest addon
    # =========================================================================

    {
        "id":        "screen_before_bed",
        "number":    34,
        "domain":    "behavioral",
        "text":      "How often do you use screens (phone, laptop, TV) "
                     "within 1 hour of bedtime?",
        "options": [
            {"label": "Never",                   "value": "never"},
            {"label": "Rarely (1-2 nights/wk)",  "value": "rarely"},
            {"label": "Often (3-5 nights/wk)",   "value": "often"},
            {"label": "Always (every night)",    "value": "always"},
        ],
        "core_from": "q20",
        "gain":      0.80,
        "evidence":  "Bousgheiri 2024: Smartphone/screen addiction ranks "
                     "high; blue light suppresses melatonin (web:0, web:5)",
    },

    {
        "id":        "consistent_sleep_time",
        "number":    35,
        "domain":    "behavioral",
        "text":      "How consistent is your bedtime and wake-up time "
                     "each day (including weekends)?",
        "options": [
            {"label": "Very consistent (same times daily)",        "value": "very_consistent"},
            {"label": "Somewhat consistent (varies by 1-2 hrs)",  "value": "somewhat_consistent"},
            {"label": "Inconsistent (varies a lot)",              "value": "inconsistent"},
        ],
        "core_from": "q20",
        "gain":      0.75,
        "evidence":  "Okano 2019: Sleep regularity top-25% academic "
                     "impact predictor; NSF core metric (web:7, web:11)",
    },

    {
        "id":        "daytime_nap_hours",
        "number":    36,
        "domain":    "behavioral",
        "text":      "On average, how many hours do you nap "
                     "during the day?",
        "options": [
            {"label": "0 — no napping",    "value": "none"},
            {"label": "0.5-1 hour",        "value": "short"},
            {"label": "1-2 hours",         "value": "moderate"},
            {"label": "More than 2 hours", "value": "long"},
        ],
        "core_from": "q20",
        "gain":      0.62,
        "evidence":  "NSF: Napping more than 1 hr or after 3 PM disrupts "
                     "nighttime sleep onset significantly (web:0, web:10)",
    },

    {
        "id":        "bedtime_routine_consistency",
        "number":    37,
        "domain":    "behavioral",
        "text":      "Do you have a consistent pre-bed routine "
                     "(e.g., reading, no screens)?",
        "options": [
            {"label": "Yes (daily)",              "value": "daily"},
            {"label": "Sometimes (3-5 nights/wk)","value": "sometimes"},
            {"label": "Rarely (1-2 nights/wk)",   "value": "rarely"},
            {"label": "No",                       "value": "no"},
        ],
        "core_from": "q30",
        "gain":      0.55,
        "evidence":  "PSQI: Consistent pre-sleep routines reduce latency "
                     "and improve efficiency (web:2, web:7)",
    },

    {
        "id":        "social_media_use_at_night",
        "number":    38,
        "domain":    "behavioral",
        "text":      "How long do you spend on social media in bed "
                     "before sleep?",
        "options": [
            {"label": "None",                  "value": "none"},
            {"label": "Less than 30 minutes",  "value": "short"},
            {"label": "30-60 minutes",         "value": "moderate"},
            {"label": "More than 60 minutes",  "value": "long"},
        ],
        "core_from": "q30",
        "gain":      0.58,
        "evidence":  "Bousgheiri 2024: Social media night use among top "
                     "behavioral disruptors for students (web:0, web:5)",
    },

    {
        "id":        "social_interactions_at_night",
        "number":    39,
        "domain":    "behavioral",
        "text":      "How often do late-night social activities "
                     "(e.g., parties, calls) disrupt your sleep?",
        "options": [
            {"label": "Never",                        "value": "never"},
            {"label": "Rarely (1-2 times/month)",     "value": "rarely"},
            {"label": "Often (weekly)",               "value": "often"},
            {"label": "Frequently (multiple/week)",   "value": "frequently"},
        ],
        "core_from": "addon",
        "gain":      0.38,
        "evidence":  "NSF: Social disruptions delay sleep onset and "
                     "reduce total sleep time (web:0, web:10)",
    },

    {
        "id":        "relaxation_techniques",
        "number":    40,
        "domain":    "behavioral",
        "text":      "How often do you use relaxation techniques "
                     "(e.g., meditation, deep breathing) before bed?",
        "options": [
            {"label": "Never",                   "value": "never"},
            {"label": "Rarely (1-2 nights/wk)",  "value": "rarely"},
            {"label": "Often (3-5 nights/wk)",   "value": "often"},
            {"label": "Always",                  "value": "always"},
        ],
        "core_from": "q50",
        "gain":      0.42,
        "evidence":  "AASM: Relaxation techniques reduce sleep latency "
                     "by 15-25 min in evidence-based trials (web:6, web:17)",
    },

    {
        "id":        "daytime_fatigue",
        "number":    41,
        "domain":    "behavioral",
        "text":      "How often do you feel fatigued or sleepy "
                     "during the day?",
        "options": [
            {"label": "Never",                    "value": "never"},
            {"label": "Rarely (1-2 days/wk)",     "value": "rarely"},
            {"label": "Often (3-5 days/wk)",      "value": "often"},
            {"label": "Every day",                "value": "every_day"},
        ],
        "core_from": "q50",
        "gain":      0.50,
        "evidence":  "Desjardins/ESS: Daytime fatigue reflects sleep debt "
                     "and is a key outcome measure (web:9, web:16)",
    },

    {
        "id":        "frequent_wakeups",
        "number":    42,
        "domain":    "behavioral",
        "text":      "How many times do you wake up per night "
                     "on average?",
        "options": [
            {"label": "0 times",    "value": "none"},
            {"label": "1-2 times",  "value": "few"},
            {"label": "3-4 times",  "value": "several"},
            {"label": "5+ times",   "value": "many"},
        ],
        "core_from": "q40",
        "gain":      0.55,
        "evidence":  "PSQI: Sleep fragmentation explains 20% of sleep "
                     "quality variance (web:2, web:12)",
    },

    {
        "id":        "sleep_latency",
        "number":    43,
        "domain":    "behavioral",
        "text":      "How long does it typically take you to fall asleep "
                     "after going to bed?",
        "options": [
            {"label": "Less than 15 minutes", "value": "fast"},
            {"label": "15-30 minutes",        "value": "normal"},
            {"label": "30-60 minutes",        "value": "slow"},
            {"label": "More than 60 minutes", "value": "very_slow"},
        ],
        "core_from": "q40",
        "gain":      0.60,
        "evidence":  "PSQI: Sleep latency is one of 7 core components; "
                     "more than 30 min signals clinically poor sleep "
                     "(web:2, web:12)",
    },

    {
        "id":        "morning_sleepiness",
        "number":    44,
        "domain":    "behavioral",
        "text":      "How alert do you feel upon waking "
                     "in the morning?",
        "options": [
            {"label": "Very alert",      "value": "very_alert"},
            {"label": "Somewhat alert",  "value": "somewhat_alert"},
            {"label": "Groggy",          "value": "groggy"},
            {"label": "Extremely tired", "value": "extremely_tired"},
        ],
        "core_from": "q50",
        "gain":      0.48,
        "evidence":  "NSF/ESS: Morning alertness inversely predicts "
                     "sleep quality scores (web:0, web:17)",
    },

    {
        "id":        "reading_before_bed",
        "number":    91,
        "domain":    "behavioral",
        "text":      "How often do you read (books, not screens) "
                     "before sleep?",
        "options": [
            {"label": "Never",                   "value": "never"},
            {"label": "Rarely (1-2 nights/wk)",  "value": "rarely"},
            {"label": "Often (3-5 nights/wk)",   "value": "often"},
            {"label": "Always",                  "value": "always"},
        ],
        "core_from": "addon",
        "gain":      0.26,
        "evidence":  "AASM: Physical reading calms the mind and "
                     "reduces sleep latency (web:6, web:17)",
    },

    {
        "id":        "journaling_habits",
        "number":    92,
        "domain":    "behavioral",
        "text":      "How often do you journal your thoughts "
                     "before bed?",
        "options": [
            {"label": "Never",   "value": "never"},
            {"label": "Rarely",  "value": "rarely"},
            {"label": "Often",   "value": "often"},
            {"label": "Daily",   "value": "daily"},
        ],
        "core_from": "addon",
        "gain":      0.24,
        "evidence":  "Studies: Journaling reduces cognitive rumination "
                     "in 30% of anxious sleepers (web:5, web:8)",
    },

    {
        "id":        "stretching_routine",
        "number":    93,
        "domain":    "behavioral",
        "text":      "How often do you do light stretching or yoga "
                     "before bed?",
        "options": [
            {"label": "Never",                   "value": "never"},
            {"label": "Rarely (1-2 nights/wk)",  "value": "rarely"},
            {"label": "Often (3-5 nights/wk)",   "value": "often"},
            {"label": "Always",                  "value": "always"},
        ],
        "core_from": "addon",
        "gain":      0.25,
        "evidence":  "NSF: Pre-bed stretching improves relaxation "
                     "and sleep quality scores (web:0, web:10)",
    },

    {
        "id":        "bath_shower_timing",
        "number":    94,
        "domain":    "behavioral",
        "text":      "How often do you take a warm bath or shower "
                     "before bed?",
        "options": [
            {"label": "Never",   "value": "never"},
            {"label": "Rarely",  "value": "rarely"},
            {"label": "Often",   "value": "often"},
            {"label": "Daily",   "value": "daily"},
        ],
        "core_from": "addon",
        "gain":      0.28,
        "evidence":  "AASM: Warm bath 1-2 hrs before bed lowers core "
                     "temperature aiding sleep onset",
    },

    {
        "id":        "music_listening_before_bed",
        "number":    95,
        "domain":    "behavioral",
        "text":      "How often do you listen to calming music or "
                     "sounds before bed?",
        "options": [
            {"label": "Never",                   "value": "never"},
            {"label": "Rarely (1-2 nights/wk)",  "value": "rarely"},
            {"label": "Often (3-5 nights/wk)",   "value": "often"},
            {"label": "Always",                  "value": "always"},
        ],
        "core_from": "addon",
        "gain":      0.23,
        "evidence":  "PSQI: Relaxing music aids disturbance reduction "
                     "and sleep onset (web:2, web:7)",
    },

    {
        "id":        "bed_for_sleep_only",
        "number":    96,
        "domain":    "behavioral",
        "text":      "How often do you use your bed for activities "
                     "other than sleep (e.g., studying, eating)?",
        "options": [
            {"label": "Never",   "value": "never"},
            {"label": "Rarely",  "value": "rarely"},
            {"label": "Often",   "value": "often"},
            {"label": "Always",  "value": "always"},
        ],
        "core_from": "addon",
        "gain":      0.32,
        "evidence":  "SHPS: Stimulus control — using bed only for sleep "
                     "improves efficiency significantly",
    },

    {
        "id":        "alarm_usage",
        "number":    97,
        "domain":    "behavioral",
        "text":      "How many alarms do you set to wake up?",
        "options": [
            {"label": "1",     "value": "one"},
            {"label": "2-3",   "value": "few"},
            {"label": "4-5",   "value": "several"},
            {"label": "6+",    "value": "many"},
        ],
        "core_from": "addon",
        "gain":      0.27,
        "evidence":  "CDC: Multiple alarms indicate fragmented sleep "
                     "and unrestorative rest patterns (web:1, web:3)",
    },

    {
        "id":        "weekend_sleep_catchup",
        "number":    98,
        "domain":    "behavioral",
        "text":      "How much longer do you sleep on weekends "
                     "compared to weekdays?",
        "options": [
            {"label": "Same amount",        "value": "same"},
            {"label": "1-2 hours longer",   "value": "slightly_more"},
            {"label": "3-4 hours longer",   "value": "much_more"},
            {"label": "5+ hours longer",    "value": "far_more"},
        ],
        "core_from": "addon",
        "gain":      0.35,
        "evidence":  "NSF: Social jet lag from weekend catch-up disrupts "
                     "circadian rhythm (web:0, web:17)",
    },

    {
        "id":        "caffeine_alternatives",
        "number":    99,
        "domain":    "behavioral",
        "text":      "How often do you use energy supplements "
                     "(e.g., ginseng, energy pills)?",
        "options": [
            {"label": "Never",   "value": "never"},
            {"label": "Rarely",  "value": "rarely"},
            {"label": "Often",   "value": "often"},
            {"label": "Daily",   "value": "daily"},
        ],
        "core_from": "addon",
        "gain":      0.22,
        "evidence":  "Studies: Stimulant supplements have similar "
                     "disruptive effects to caffeine (web:7, web:12)",
    },

    {
        "id":        "walking_after_dinner",
        "number":    100,
        "domain":    "behavioral",
        "text":      "How often do you go for a light walk "
                     "after dinner?",
        "options": [
            {"label": "Never",                   "value": "never"},
            {"label": "Rarely (1-2 nights/wk)",  "value": "rarely"},
            {"label": "Often (3-5 nights/wk)",   "value": "often"},
            {"label": "Always",                  "value": "always"},
        ],
        "core_from": "addon",
        "gain":      0.21,
        "evidence":  "AASM: Post-dinner walking aids digestion and "
                     "promotes sleep readiness (web:6, web:10)",
    },


    # =========================================================================
    # DOMAIN 5: ACADEMIC
    # 27 questions — Q45-Q61 (original) + Q101-Q110 (expanded)
    # Cores: Q57, Q46, Q49 (q20) | Q48, Q45 (q30) | Q61, Q50 (q40)
    #        Q56, Q47, Q58 (q50) | rest addon
    # =========================================================================

    {
        "id":        "sleep_hours",
        "number":    57,
        "domain":    "academic",
        "text":      "On average, how many hours of sleep do you "
                     "get per night?",
        "options": [
            {"label": "Less than 4 hours", "value": "less_than_4"},
            {"label": "4-6 hours",         "value": "four_to_six"},
            {"label": "6-8 hours",         "value": "six_to_eight"},
            {"label": "More than 8 hours", "value": "more_than_8"},
        ],
        "core_from": "q20",
        "gain":      0.92,
        "evidence":  "PSQI: Duration is number 1 predictor — explains "
                     "30-40% variance; CDC/NSF minimum 7 hrs "
                     "(web:4, web:9)",
    },

    {
        "id":        "study_past_midnight",
        "number":    46,
        "domain":    "academic",
        "text":      "How often do you study or work past midnight?",
        "options": [
            {"label": "Never",                   "value": "never"},
            {"label": "Rarely (1-2 nights/wk)",  "value": "rarely"},
            {"label": "Often (3-5 nights/wk)",   "value": "often"},
            {"label": "Always (every night)",    "value": "always"},
        ],
        "core_from": "q20",
        "gain":      0.78,
        "evidence":  "Okano 2019: Late studying in top 25% of academic "
                     "performance predictors (web:7, web:11)",
    },

    {
        "id":        "academic_workload",
        "number":    49,
        "domain":    "academic",
        "text":      "How heavy is your current course load?",
        "options": [
            {"label": "Light (under 12 credits)", "value": "light"},
            {"label": "Average (12-15 credits)",  "value": "average"},
            {"label": "Heavy (16+ credits)",      "value": "heavy"},
        ],
        "core_from": "q20",
        "gain":      0.72,
        "evidence":  "Mbous 2022: Workload predicts 50% of insomnia "
                     "variance alongside employment (web:5, web:8)",
    },

    {
        "id":        "upcoming_deadline",
        "number":    48,
        "domain":    "academic",
        "text":      "Do you have any major deadlines or assignments "
                     "due in the next week?",
        "options": [
            {"label": "Yes", "value": "yes"},
            {"label": "No",  "value": "no"},
        ],
        "core_from": "q30",
        "gain":      0.60,
        "evidence":  "Okano 2019: Acute deadline stress in top "
                     "preparation/sleep predictors (web:7, web:11)",
    },

    {
        "id":        "exam_period",
        "number":    45,
        "domain":    "academic",
        "text":      "Are you currently in an exam period or "
                     "preparing for one?",
        "options": [
            {"label": "Yes", "value": "yes"},
            {"label": "No",  "value": "no"},
        ],
        "core_from": "q30",
        "gain":      0.62,
        "evidence":  "NSF: Exam periods associated with 1-2 hr sleep "
                     "reduction and elevated cortisol (web:0, web:17)",
    },

    {
        "id":        "performance_impact",
        "number":    61,
        "domain":    "academic",
        "text":      "How often does poor sleep affect your academic "
                     "performance (e.g., concentration in class)?",
        "options": [
            {"label": "Never",                    "value": "never"},
            {"label": "Rarely (1-2 days/wk)",     "value": "rarely"},
            {"label": "Often (3-5 days/wk)",      "value": "often"},
            {"label": "Every day",                "value": "every_day"},
        ],
        "core_from": "q40",
        "gain":      0.65,
        "evidence":  "Okano 2019: Sleep-performance link — direct "
                     "academic impact metric (web:7, web:10)",
    },

    {
        "id":        "employment_status",
        "number":    50,
        "domain":    "academic",
        "text":      "Do you work a job alongside your studies, and "
                     "if so, how many hours per week?",
        "options": [
            {"label": "No job",                   "value": "none"},
            {"label": "Part-time (under 20 hrs)", "value": "part_time"},
            {"label": "Full-time (20+ hrs)",      "value": "full_time"},
        ],
        "core_from": "q40",
        "gain":      0.58,
        "evidence":  "Mbous 2022: Employment is top-3 predictor of "
                     "student insomnia (web:5, web:8)",
    },

    {
        "id":        "procrastination_habits",
        "number":    56,
        "domain":    "academic",
        "text":      "How often do you procrastinate on academic tasks, "
                     "leading to last-minute work?",
        "options": [
            {"label": "Never",             "value": "never"},
            {"label": "Rarely",            "value": "rarely"},
            {"label": "Often (frequent)",  "value": "often"},
            {"label": "Always",            "value": "always"},
        ],
        "core_from": "q50",
        "gain":      0.55,
        "evidence":  "NSF/Okano: Procrastination shifts studying late, "
                     "directly reducing sleep hours (web:0, web:7)",
    },

    {
        "id":        "early_morning_class",
        "number":    47,
        "domain":    "academic",
        "text":      "Do you have classes or commitments that "
                     "start before 8 AM?",
        "options": [
            {"label": "Yes", "value": "yes"},
            {"label": "No",  "value": "no"},
        ],
        "core_from": "q50",
        "gain":      0.52,
        "evidence":  "NSF: Early classes reduce sleep time and cause "
                     "chronic sleep debt in students (web:0, web:10)",
    },

    {
        "id":        "academic_pressure_peers_family",
        "number":    58,
        "domain":    "academic",
        "text":      "How much pressure do you feel from others "
                     "(peers, family) to perform academically?",
        "options": [
            {"label": "None",     "value": "none"},
            {"label": "Mild",     "value": "mild"},
            {"label": "Moderate", "value": "moderate"},
            {"label": "High",     "value": "high"},
        ],
        "core_from": "q50",
        "gain":      0.50,
        "evidence":  "Wang 2023: External academic pressure amplifies "
                     "stress and self-control effects on sleep "
                     "(web:6, web:18)",
    },

    {
        "id":        "major_type",
        "number":    51,
        "domain":    "academic",
        "text":      "What type of major are you studying?",
        "options": [
            {"label": "Humanities/Social Sciences", "value": "humanities"},
            {"label": "STEM/Engineering",           "value": "stem"},
            {"label": "Medical/Nursing",            "value": "medical"},
            {"label": "Other",                      "value": "other"},
        ],
        "core_from": "addon",
        "gain":      0.38,
        "evidence":  "Kushida/Okano: High-demand majors (medicine, STEM) "
                     "associated with greater sleep debt (web:7, web:11)",
    },

    {
        "id":        "study_environment",
        "number":    52,
        "domain":    "academic",
        "text":      "How often do you study in a distracting "
                     "environment (e.g., cafe, noisy library)?",
        "options": [
            {"label": "Never",              "value": "never"},
            {"label": "Rarely (1-2×/wk)",   "value": "rarely"},
            {"label": "Often (3-5×/wk)",    "value": "often"},
            {"label": "Always",             "value": "always"},
        ],
        "core_from": "addon",
        "gain":      0.34,
        "evidence":  "Studies: Distracting study environments extend "
                     "study hours, delaying sleep (web:5, web:8)",
    },

    {
        "id":        "extracurricular_hours",
        "number":    53,
        "domain":    "academic",
        "text":      "How many hours per week do you spend on clubs, "
                     "sports, or volunteering?",
        "options": [
            {"label": "0 hours",        "value": "none"},
            {"label": "1-5 hours",      "value": "low"},
            {"label": "6-10 hours",     "value": "moderate"},
            {"label": "More than 10",   "value": "high"},
        ],
        "core_from": "addon",
        "gain":      0.36,
        "evidence":  "NSF: Extracurricular overload adds to time-debt "
                     "and reduces sleep window (web:0, web:10)",
    },

    {
        "id":        "transition_challenges",
        "number":    54,
        "domain":    "academic",
        "text":      "If you are a new student, how difficult has "
                     "adjusting to university life been?",
        "options": [
            {"label": "Not applicable (not new)", "value": "not_applicable"},
            {"label": "Easy adjustment",          "value": "easy"},
            {"label": "Moderate challenges",      "value": "moderate"},
            {"label": "Very difficult",           "value": "very_difficult"},
        ],
        "core_from": "addon",
        "gain":      0.32,
        "evidence":  "CDC: Transition stress is a major first-year "
                     "sleep disruptor (web:1, web:3)",
    },

    {
        "id":        "group_projects_late",
        "number":    55,
        "domain":    "academic",
        "text":      "How often do group assignments or meetings "
                     "extend into late hours?",
        "options": [
            {"label": "Never",                       "value": "never"},
            {"label": "Rarely (1-2×/semester)",      "value": "rarely"},
            {"label": "Often (monthly)",             "value": "often"},
            {"label": "Frequently (weekly)",         "value": "frequently"},
        ],
        "core_from": "addon",
        "gain":      0.30,
        "evidence":  "Okano/Kushida: Late group sessions add cumulative "
                     "sleep debt (web:7, web:11)",
    },

    {
        "id":        "online_classes",
        "number":    59,
        "domain":    "academic",
        "text":      "How many of your classes are online or hybrid, "
                     "potentially affecting your schedule?",
        "options": [
            {"label": "None",              "value": "none"},
            {"label": "Some (1-2 classes)","value": "some"},
            {"label": "Most (3+ classes)", "value": "most"},
            {"label": "All",               "value": "all"},
        ],
        "core_from": "addon",
        "gain":      0.28,
        "evidence":  "Studies: Online class flexibility enables irregular "
                     "sleep schedules (web:7, web:12)",
    },

    {
        "id":        "commute_time",
        "number":    60,
        "domain":    "academic",
        "text":      "How long is your daily commute to campus "
                     "or classes?",
        "options": [
            {"label": "No commute (on-campus/online)", "value": "none"},
            {"label": "Short (under 30 min)",          "value": "short"},
            {"label": "Medium (30-60 min)",            "value": "medium"},
            {"label": "Long (over 60 min)",            "value": "long"},
        ],
        "core_from": "addon",
        "gain":      0.29,
        "evidence":  "CDC: Long commutes reduce sleep window and "
                     "increase fatigue (web:1, web:3)",
    },

    {
        "id":        "lecture_attendance",
        "number":    101,
        "domain":    "academic",
        "text":      "How often do you miss lectures due to tiredness?",
        "options": [
            {"label": "Never",              "value": "never"},
            {"label": "Rarely (monthly)",   "value": "rarely"},
            {"label": "Often (weekly)",     "value": "often"},
            {"label": "Frequently",         "value": "frequently"},
        ],
        "core_from": "addon",
        "gain":      0.35,
        "evidence":  "Okano 2019: Attendance drops link directly to "
                     "sleep deficit and performance loss (web:7, web:10)",
    },

    {
        "id":        "note_taking_effectiveness",
        "number":    102,
        "domain":    "academic",
        "text":      "How effective is your note-taking during classes "
                     "when you are sleepy?",
        "options": [
            {"label": "Very effective", "value": "very_effective"},
            {"label": "Fair",           "value": "fair"},
            {"label": "Poor",           "value": "poor"},
            {"label": "Very poor",      "value": "very_poor"},
        ],
        "core_from": "addon",
        "gain":      0.27,
        "evidence":  "Studies: Sleep loss reduces memory encoding "
                     "and retention by 40% (web:5, web:8)",
    },

    {
        "id":        "exam_preparation_style",
        "number":    103,
        "domain":    "academic",
        "text":      "How often do you cram for exams?",
        "options": [
            {"label": "Never",   "value": "never"},
            {"label": "Rarely",  "value": "rarely"},
            {"label": "Often",   "value": "often"},
            {"label": "Always",  "value": "always"},
        ],
        "core_from": "addon",
        "gain":      0.38,
        "evidence":  "NSF: Cramming worsens both sleep quality and "
                     "memory consolidation (web:0, web:17)",
    },

    {
        "id":        "help_seeking_behavior",
        "number":    104,
        "domain":    "academic",
        "text":      "How often do you seek academic help "
                     "(e.g., tutoring, office hours)?",
        "options": [
            {"label": "Never",                  "value": "never"},
            {"label": "Rarely (semesterly)",    "value": "rarely"},
            {"label": "Often (monthly)",        "value": "often"},
            {"label": "Frequently",             "value": "frequently"},
        ],
        "core_from": "addon",
        "gain":      0.22,
        "evidence":  "CDC: Academic support reduces stress and "
                     "sleep disruption (web:1, web:3)",
    },

    {
        "id":        "grade_satisfaction",
        "number":    105,
        "domain":    "academic",
        "text":      "How satisfied are you with your current grades?",
        "options": [
            {"label": "Very satisfied",    "value": "very_satisfied"},
            {"label": "Somewhat",          "value": "somewhat"},
            {"label": "Dissatisfied",      "value": "dissatisfied"},
            {"label": "Very dissatisfied", "value": "very_dissatisfied"},
        ],
        "core_from": "addon",
        "gain":      0.33,
        "evidence":  "PSQI: Grade dissatisfaction correlates with "
                     "anxiety-driven poor sleep (web:2, web:7)",
    },

    {
        "id":        "study_breaks",
        "number":    106,
        "domain":    "academic",
        "text":      "How often do you take breaks during "
                     "study sessions?",
        "options": [
            {"label": "Every 30 minutes", "value": "frequent"},
            {"label": "Every hour",       "value": "regular"},
            {"label": "Rarely",           "value": "rarely"},
            {"label": "Never",            "value": "never"},
        ],
        "core_from": "addon",
        "gain":      0.26,
        "evidence":  "AASM: Scheduled breaks prevent cognitive burnout "
                     "and improve sleep readiness (web:6, web:9)",
    },

    {
        "id":        "academic_motivation",
        "number":    107,
        "domain":    "academic",
        "text":      "How motivated are you for your studies?",
        "options": [
            {"label": "Highly motivated",  "value": "high"},
            {"label": "Moderately",        "value": "moderate"},
            {"label": "Low",               "value": "low"},
            {"label": "Very low",          "value": "very_low"},
        ],
        "core_from": "addon",
        "gain":      0.31,
        "evidence":  "Mbous 2022: Low motivation ties to depression "
                     "and disrupted sleep patterns",
    },

    {
        "id":        "internship_demands",
        "number":    108,
        "domain":    "academic",
        "text":      "If you have an internship, how many hours "
                     "per week does it take?",
        "options": [
            {"label": "No internship",    "value": "none"},
            {"label": "Under 10 hours",   "value": "low"},
            {"label": "10-20 hours",      "value": "moderate"},
            {"label": "Over 20 hours",    "value": "high"},
        ],
        "core_from": "addon",
        "gain":      0.29,
        "evidence":  "Studies: Internship hours add directly to total "
                     "time burden and sleep deficit (web:7, web:12)",
    },

    {
        "id":        "thesis_research_load",
        "number":    109,
        "domain":    "academic",
        "text":      "If you are in graduate school, how heavy is "
                     "your thesis or research work?",
        "options": [
            {"label": "Not applicable", "value": "not_applicable"},
            {"label": "Light",          "value": "light"},
            {"label": "Medium",         "value": "medium"},
            {"label": "Heavy",          "value": "heavy"},
        ],
        "core_from": "addon",
        "gain":      0.28,
        "evidence":  "NSF: High research load disrupts regular schedules "
                     "in 50% of graduate students (web:0, web:10)",
    },

    {
        "id":        "class_participation_when_tired",
        "number":    110,
        "domain":    "academic",
        "text":      "How often do you participate in class "
                     "when tired?",
        "options": [
            {"label": "Always",  "value": "always"},
            {"label": "Often",   "value": "often"},
            {"label": "Rarely",  "value": "rarely"},
            {"label": "Never",   "value": "never"},
        ],
        "core_from": "addon",
        "gain":      0.20,
        "evidence":  "CDC: Fatigue significantly reduces academic "
                     "engagement and participation (web:1, web:3)",
    },

]

# =============================================================================
# END OF QUESTION BANK — all 120 questions loaded.
# =============================================================================
# =============================================================================
# SleepWise — trigger_rules.py
#
# This file defines how elevated cause posteriors translate into specific
# add-on question selections during an adaptive session.
#
# It contains two components:
#
#   1. TRIGGER_RULES
#      Maps each of the 29 causes to an ordered list of add-on question IDs.
#      When a cause's posterior is elevated after the core questions, the
#      session manager consults this list to find which add-on questions
#      would most reduce remaining uncertainty about that cause.
#
#      Each add-on entry is a tuple:
#        (question_id, min_variant, priority_rank)
#
#      question_id   : matches exactly the 'id' field in question_bank.py
#                      and the first argument of user_fact/2 in Prolog.
#      min_variant   : earliest variant where this add-on is eligible.
#                      'q20' = eligible from Quick onwards
#                      'q30' = eligible from Balanced onwards
#                      'q40' = eligible from Detailed onwards
#                      'q50' = eligible from Full Dive onwards
#      priority_rank : 1 = highest priority, selected first within budget.
#                      Lower numbers = more diagnostic value for this cause.
#
#   2. CROSS_DOMAIN_TRIGGERS
#      Joint condition triggers that fire based on specific COMBINATIONS
#      of answer values rather than single cause posteriors. These capture
#      the most important interaction effects — the dependencies that Naive
#      Bayes cannot model on its own.
#
#      Each entry has:
#        id         : identifier for logging and debugging
#        condition  : lambda(answers, posteriors) -> bool
#        addons     : list of question IDs to add in priority order
#        min_variant: earliest variant where this trigger is eligible
#        clinical   : if True, fires in ALL variants, ignores slot budget,
#                     and cannot be suppressed — used for CF-level patterns
#
# COORDINATION WITH OTHER FILES:
#   - question_bank.py  : all question_id values here match bank entries
#   - bayes_engine.py   : posteriors from update_posteriors() trigger rules
#   - session_manager.py: select_addons() reads this file to fill the budget
#   - sleepwise.pl      : user_fact/2 atoms match question_id values here
#
# DEDUPLICATION:
#   The same question ID may appear in multiple causes' trigger lists.
#   session_manager.select_addons() deduplicates — a question is asked at
#   most once per session regardless of how many causes reference it.
#   When deduplicating, the instance with the highest combined score
#   (posterior × 1/priority) is kept.
#
# MIN_VARIANT LOGIC:
#   Questions that are cores in some variants (e.g. core_from='q30') are
#   still listed as add-on targets. session_manager skips any question
#   already in asked_ids, so if it was asked as a core it won't repeat.
#   The min_variant here reflects when the question adds value as an add-on
#   specifically — typically one variant below its core_from level.
# =============================================================================

sys.path.insert(0, os.path.dirname(__file__))
from bayes_engine import PRIORS


# =============================================================================
# SECTION 1 — TRIGGER RULES
# Format per entry: (question_id, min_variant, priority_rank)
# Ordered within each cause by diagnostic value for that specific cause.
# =============================================================================

TRIGGER_RULES = {

    # ─────────────────────────────────────────────────────────────────────────
    # LIFESTYLE CAUSES
    # ─────────────────────────────────────────────────────────────────────────

    "high_caffeine": [
        # caffeine_timing is the single most diagnostic follow-up:
        # knowing WHEN caffeine is consumed explains latency directly
        ("caffeine_timing",        "q20", 1),
        # sugary food at night has same stimulant-like effect, extends picture
        ("sugary_food_intake",     "q20", 2),
        # late fluid intake compounds caffeine — nocturia + stimulation
        ("fluid_intake_timing",    "q20", 3),
        # stimulant supplements may substitute or compound caffeine
        ("caffeine_alternatives",  "q30", 4),
        # supplement timing — B-vitamins taken late act as stimulants
        ("supplement_timing",      "q40", 5),
    ],

    "poor_diet_habits": [
        # meal size is the most direct follow-up to heavy meal flag
        ("meal_size_variation",    "q20", 1),
        # snacking compounds meal-related disruption
        ("snacking_at_night",      "q20", 2),
        # irregularity of meal times affects circadian rhythm
        ("diet_consistency",       "q20", 3),
        # fasting/skipping dinner disrupts evening metabolism
        ("fasting_habits",         "q30", 4),
        # allergies can cause nighttime discomfort independent of meal size
        ("dietary_allergies",      "q40", 5),
        # sugary foods at night spike blood sugar — same disruption pathway
        ("sugary_food_intake",     "q40", 6),
    ],

    "sedentary_lifestyle": [
        # exercise timing matters as much as frequency — late exercise hurts
        ("exercise_timing",        "q20", 1),
        # light post-dinner walk is both diagnostic and actionable
        ("walking_after_dinner",   "q20", 2),
        # stretching before bed is a protective behavior — absence flags issue
        ("stretching_routine",     "q30", 3),
        # daytime fatigue confirms sedentary cycle: no activity → poor sleep
        # → fatigue → less activity
        ("daytime_fatigue",        "q30", 4),
        # bath/shower timing — sedentary students often skip this wind-down
        ("bath_shower_timing",     "q40", 5),
    ],

    "substance_use": [
        # alcohol is the highest-evidence substance disruptor — ask first
        ("alcohol_consumption",    "q20", 1),
        # recreational drugs — second most impactful, underreported
        ("recreational_drug_use",  "q20", 2),
        # vaping/nicotine alternatives increasingly common in students
        ("nicotine_alternatives",  "q20", 3),
        # tobacco — traditional form, still significant
        ("tobacco_use",            "q30", 4),
        # fasting can interact with substance use — empty stomach amplifies
        ("fasting_habits",         "q40", 5),
        # food insecurity sometimes linked to substance use patterns
        ("food_insecurity",        "q50", 6),
    ],

    "poor_hydration": [
        # timing of last fluid determines nocturia risk directly
        ("fluid_intake_timing",    "q20", 1),
        # total hydration level — dehydration causes restlessness
        ("hydration_habits",       "q20", 2),
        # frequent wakeups confirm nocturia pattern
        ("frequent_wakeups",       "q20", 3),
        # dietary allergies can increase fluid retention issues
        ("dietary_allergies",      "q40", 4),
    ],

    "medication_interference": [
        # timing is the key diagnostic — same medication at different times
        # has completely different sleep impact
        ("supplement_timing",      "q20", 1),
        # stimulant alternatives may be used alongside prescriptions
        ("caffeine_alternatives",  "q20", 2),
        # confirm medication use detail if not already asked as core
        ("medication_supplements", "q20", 3),
        # vitamin B taken at night is a common overlooked disruptor
        ("sugary_food_intake",     "q40", 4),
    ],

    # ─────────────────────────────────────────────────────────────────────────
    # PSYCHOLOGICAL CAUSES
    # ─────────────────────────────────────────────────────────────────────────

    "high_stress": [
        # rumination is the behavioral mechanism through which stress
        # becomes insomnia — most diagnostic follow-up
        ("rumination_habits",      "q20", 1),
        # financial stress is a distinct but common stress subtype in students
        ("financial_stress",       "q20", 2),
        # general non-academic worries broaden the stress picture
        ("general_worries",        "q20", 3),
        # resilience determines whether stress translates to poor sleep
        ("resilience_level",       "q30", 4),
        # mindfulness practice — absence confirms no coping mechanism
        ("mindfulness_practice",   "q30", 5),
        # emotional regulation skill level mediates stress-sleep link
        ("emotional_regulation",   "q40", 6),
        # discrimination stress adds independent pathway — UG context relevant
        ("discrimination_experiences", "q50", 7),
    ],

    "anxiety": [
        # panic attacks — escalates clinical concern immediately
        ("panic_attacks",          "q20", 1),
        # fear of failure is the most common anxiety subtype in students
        ("fear_of_failure",        "q20", 2),
        # perfectionism drives anxiety in academic contexts
        ("perfectionism_tendencies","q20", 3),
        # worry before bed is the sleep-specific anxiety manifestation
        ("worry_before_bed",       "q20", 4),
        # emotional regulation ability determines anxiety impact on sleep
        ("emotional_regulation",   "q30", 5),
        # social comparison amplifies anxiety in university setting
        ("social_comparison",      "q40", 6),
        # attachment style predicts anxiety pattern type
        ("attachment_style",       "q50", 7),
    ],

    "depression": [
        # loneliness is the strongest environmental mediator of depression
        ("loneliness_levels",      "q20", 1),
        # trauma or grief — acute causal event for depression onset
        ("trauma_or_grief",        "q20", 2),
        # optimism level — inverse indicator of depression severity
        ("optimism_outlook",       "q20", 3),
        # therapy attendance — protective behavior, absence is a risk flag
        ("therapy_attendance",     "q30", 4),
        # seasonal mood changes — screens for Seasonal Affective Disorder
        ("seasonal_mood_changes",  "q30", 5),
        # mood swings can indicate bipolar spectrum alongside depression
        ("mood_swings",            "q40", 6),
        # discrimination experiences are a documented depression pathway
        ("discrimination_experiences", "q50", 7),
    ],

    "burnout": [
        # motivation level is the most direct behavioral marker of burnout
        ("academic_motivation",    "q20", 1),
        # therapy attendance — most students with burnout are not in therapy
        ("therapy_attendance",     "q20", 2),
        # mood swings accompany burnout and worsen sleep
        ("mood_swings",            "q30", 3),
        # gratitude practice — its absence confirms no positive reframing
        ("gratitude_practice",     "q30", 4),
        # forgiveness of self — burnout students self-blame significantly
        ("forgiveness_practices",  "q40", 5),
        # boredom and burnout co-occur — disengagement pattern
        ("boredom_frequency",      "q40", 6),
        # existential worry about future — common in burned-out students
        ("existential_worries",    "q50", 7),
    ],

    "rumination": [
        # worry before bed is the sleep-onset specific form of rumination
        ("worry_before_bed",       "q20", 1),
        # guilt replay is a distinct rumination subtype
        ("guilt_feelings",         "q20", 2),
        # existential worries are often the content of rumination episodes
        ("existential_worries",    "q20", 3),
        # journaling — its absence means no externalisation of thoughts
        ("journaling_habits",      "q30", 4),
        # forgiveness of self breaks the guilt-rumination cycle
        ("forgiveness_practices",  "q30", 5),
        # mindfulness — primary evidence-based intervention for rumination
        ("mindfulness_practice",   "q40", 6),
        # self-esteem level predicts rumination severity
        ("self_esteem_level",      "q40", 7),
    ],

    "poor_self_control": [
        # ADHD symptoms are the primary clinical cause of poor self-control
        ("adhd_symptoms",          "q20", 1),
        # procrastination is the behavioral expression of poor self-control
        ("procrastination_habits", "q20", 2),
        # boredom leads to distraction and off-schedule behavior
        ("boredom_frequency",      "q30", 3),
        # self-esteem predicts ability to maintain routines under pressure
        ("self_esteem_level",      "q30", 4),
        # relaxation techniques — absence confirms no structured wind-down
        ("relaxation_techniques",  "q40", 5),
        # help-seeking behavior — poor self-control students avoid it
        ("help_seeking_behavior",  "q50", 6),
    ],

    "perfectionism": [
        # social comparison is the trigger mechanism for perfectionism
        ("social_comparison",      "q20", 1),
        # fear of failure is perfectionism's primary emotional output
        ("fear_of_failure",        "q20", 2),
        # self-esteem — low self-esteem fuels perfectionism cycle
        ("self_esteem_level",      "q20", 3),
        # gratitude practice — its absence confirms negative self-focus
        ("gratitude_practice",     "q30", 4),
        # forgiveness practices break the perfectionism-guilt cycle
        ("forgiveness_practices",  "q30", 5),
        # grade satisfaction — dissatisfaction drives perfectionist behavior
        ("grade_satisfaction",     "q40", 6),
    ],

    "low_resilience": [
        # emotional regulation is the core skill of resilience
        ("emotional_regulation",   "q20", 1),
        # resilience level — direct self-assessment confirmation
        ("resilience_level",       "q20", 2),
        # attachment style predicts resilience pattern
        ("attachment_style",       "q30", 3),
        # seasonal mood changes — low resilience amplifies seasonal effects
        ("seasonal_mood_changes",  "q30", 4),
        # optimism outlook is both a resilience component and outcome
        ("optimism_outlook",       "q40", 5),
        # mindfulness practice builds resilience — absence is a risk factor
        ("mindfulness_practice",   "q40", 6),
    ],

    # ─────────────────────────────────────────────────────────────────────────
    # ENVIRONMENTAL CAUSES
    # ─────────────────────────────────────────────────────────────────────────

    "noise_disturbance": [
        # shared living is the most common source of noise for students
        ("shared_living",          "q20", 1),
        # partner snoring — highly specific and actionable if present
        ("partner_snoring",        "q20", 2),
        # building maintenance issues — structural noise sources
        ("building_maintenance",   "q20", 3),
        # room clutter can amplify perceived noise through anxiety
        ("room_clutter",           "q30", 4),
        # pet or pest disturbances — common but often unreported
        ("pet_pest_disturbances",  "q30", 5),
        # neighborhood safety concerns cause hypervigilance to noise
        ("neighborhood_safety",    "q40", 6),
    ],

    "light_disturbance": [
        # window light control is the most actionable fix
        ("window_light_control",   "q20", 1),
        # electronic devices emit light and are often overlooked
        ("electronic_devices_in_room", "q20", 2),
        # natural light during the day regulates the circadian clock —
        # daytime deficiency worsens nighttime light sensitivity
        ("natural_light_exposure", "q30", 3),
        # room color affects perceived light intensity
        ("room_color_scheme",      "q40", 4),
        # electromagnetic exposure from devices close to bed
        ("electromagnetic_exposure","q40", 5),
    ],

    "temperature_discomfort": [
        # humidity compounds temperature discomfort
        ("humidity_levels",        "q20", 1),
        # ventilation quality directly affects temperature regulation
        ("ventilation_quality",    "q20", 2),
        # bed comfort interacts with temperature — wrong bedding worsens it
        ("bed_comfort",            "q30", 3),
        # electromagnetic devices near bed generate heat
        ("electromagnetic_exposure","q40", 4),
        # room color affects perceived warmth
        ("room_color_scheme",      "q50", 5),
    ],

    "poor_sleep_space": [
        # bed comfort is the most fundamental sleep space factor
        ("bed_comfort",            "q20", 1),
        # clutter creates psychological noise and stress
        ("room_clutter",           "q20", 2),
        # strong scents are a frequently overlooked disruptor
        ("scent_in_room",          "q20", 3),
        # electromagnetic exposure from devices in bed
        ("electromagnetic_exposure","q30", 4),
        # room color affects psychological comfort of the space
        ("room_color_scheme",      "q40", 5),
        # ventilation quality ties into sleep space comfort
        ("ventilation_quality",    "q40", 6),
    ],

    "safety_concern": [
        # neighborhood safety is the direct measure
        ("neighborhood_safety",    "q20", 1),
        # building maintenance failures trigger safety anxiety
        ("building_maintenance",   "q20", 2),
        # chronic health conditions can heighten safety hypervigilance
        ("chronic_health_conditions","q30", 3),
        # discrimination experiences can contribute to safety concerns
        ("discrimination_experiences","q50", 4),
    ],

    # ─────────────────────────────────────────────────────────────────────────
    # BEHAVIORAL CAUSES
    # ─────────────────────────────────────────────────────────────────────────

    "excessive_screen_use": [
        # social media in bed is the most impactful screen subtype
        ("social_media_use_at_night", "q20", 1),
        # using bed for non-sleep activities reinforces the screen habit
        ("bed_for_sleep_only",     "q20", 2),
        # multiple alarms indicate disrupted sleep from late screen use
        ("alarm_usage",            "q30", 3),
        # stimulant alternatives often accompany late-night screen sessions
        ("caffeine_alternatives",  "q30", 4),
        # reading books before bed is the healthy alternative — its absence
        # confirms exclusive screen use
        ("reading_before_bed",     "q40", 5),
    ],

    "irregular_schedule": [
        # weekend catch-up is the most diagnostic indicator of social jet lag
        ("weekend_sleep_catchup",  "q20", 1),
        # late social activities are the primary cause of irregular schedule
        ("social_interactions_at_night", "q20", 2),
        # multiple alarms confirm irregular wake-up pattern
        ("alarm_usage",            "q20", 3),
        # bedtime routine — its absence enables irregular schedules
        ("bedtime_routine_consistency", "q30", 4),
        # online classes enable schedule irregularity
        ("online_classes",         "q40", 5),
        # commute time constrains schedule and forces irregularity
        ("commute_time",           "q40", 6),
    ],

    "poor_sleep_hygiene": [
        # bedtime routine is the cornerstone of sleep hygiene
        ("bedtime_routine_consistency", "q20", 1),
        # relaxation techniques — structured wind-down absence
        ("relaxation_techniques",  "q20", 2),
        # reading physical books is a key sleep hygiene behavior
        ("reading_before_bed",     "q20", 3),
        # warm bath/shower timing — evidence-based sleep onset aid
        ("bath_shower_timing",     "q30", 4),
        # calming music before bed — secondary hygiene tool
        ("music_listening_before_bed", "q30", 5),
        # journaling externalises thoughts — sleep hygiene component
        ("journaling_habits",      "q40", 6),
        # stretching — pre-bed physical wind-down
        ("stretching_routine",     "q40", 7),
    ],

    "excessive_napping": [
        # daytime fatigue confirms the napping-fatigue feedback loop
        ("daytime_fatigue",        "q20", 1),
        # morning sleepiness confirms non-restorative nighttime sleep
        # that drives compensatory napping
        ("morning_sleepiness",     "q20", 2),
        # walking after dinner replaces the urge to nap — actionable
        ("walking_after_dinner",   "q30", 3),
        # stretching — alternative to napping for afternoon energy dip
        ("stretching_routine",     "q40", 4),
    ],

    "poor_sleep_efficiency": [
        # sleep latency directly defines onset insomnia component
        ("sleep_latency",          "q20", 1),
        # frequent wakeups directly define maintenance insomnia component
        ("frequent_wakeups",       "q20", 2),
        # warm bath lowers core temperature aiding both latency and wakeups
        ("bath_shower_timing",     "q20", 3),
        # diagnosed disorder is clinical gate — CF3 requires this answer
        ("sleep_disorders",        "q30", 4),
        # calming music helps both onset and maintenance
        ("music_listening_before_bed", "q30", 5),
        # bed association
        ("bed_for_sleep_only",     "q40", 6),
        # alarm count confirms wakeup disruption pattern
        ("alarm_usage",            "q40", 7),
        # morning sleepiness is the outcome measure of efficiency
        ("morning_sleepiness",     "q50", 8),
    ],

    # ─────────────────────────────────────────────────────────────────────────
    # ACADEMIC CAUSES
    # ─────────────────────────────────────────────────────────────────────────

    "poor_sleep_duration": [
        # performance impact is the most important consequence to measure
        ("performance_impact",     "q20", 1),
        # lecture attendance drops are a direct behavioral consequence
        ("lecture_attendance",     "q20", 2),
        # note-taking effectiveness drops with sleep deprivation
        # diagnosed disorder — clinical gate for CF3, high priority when sleep is short
        ("sleep_disorders",        "q30", 3),
        # note-taking effectiveness drops with sleep deprivation
        ("note_taking_effectiveness", "q30", 4),
        # cramming is both cause and consequence of poor duration
        ("exam_preparation_style", "q30", 5),
        # early morning class is a structural cause of short duration
        ("early_morning_class",    "q40", 6),
        # commute time eats into sleep window
        ("commute_time",           "q50", 7),
    ],

    "academic_overload": [
        # employment status is the strongest additive burden
        ("employment_status",      "q20", 1),
        # extracurricular hours add to total time burden
        ("extracurricular_hours",  "q20", 2),
        # internship demands on top of coursework
        ("internship_demands",     "q30", 3),
        # group projects extending into late hours
        ("group_projects_late",    "q30", 4),
        # commute time as a hidden time burden
        ("commute_time",           "q40", 5),
        # thesis/research load for graduate students
        ("thesis_research_load",   "q40", 6),
        # online class flexibility can paradoxically worsen overload
        ("online_classes",         "q50", 7),
    ],

    "late_night_studying": [
        # procrastination is the primary behavioral driver of late studying
        ("procrastination_habits", "q20", 1),
        # cramming is both a cause and a form of late studying
        ("exam_preparation_style", "q20", 2),
        # structured study breaks reduce marathon late sessions
        ("study_breaks",           "q30", 3),
        # distracting study environments extend session length
        ("study_environment",      "q30", 4),
        # group projects force late hours regardless of personal habits
        ("group_projects_late",    "q40", 5),
        # motivation level predicts whether late studying is panic-driven
        ("academic_motivation",    "q40", 6),
    ],

    "exam_pressure": [
        # cramming is the behavioral response to exam pressure
        ("exam_preparation_style", "q20", 1),
        # grade satisfaction predicts whether pressure is chronic or acute
        ("grade_satisfaction",     "q20", 2),
        # help-seeking behavior — its absence amplifies pressure
        ("help_seeking_behavior",  "q20", 3),
        # external pressure from family/peers compounds internal pressure
        ("academic_pressure_peers_family", "q20", 4),
        # transition challenges amplify exam pressure in new students
        ("transition_challenges",  "q30", 5),
        # major type predicts baseline exam intensity
        ("major_type",             "q40", 6),
    ],

    "performance_impact": [
        # lecture attendance is the most visible performance consequence
        ("lecture_attendance",     "q20", 1),
        # note-taking quality drops directly with fatigue
        ("note_taking_effectiveness", "q20", 2),
        # class participation when tired — active engagement measure
        ("class_participation_when_tired", "q30", 3),
        # motivation level — performance impact reduces motivation further
        ("academic_motivation",    "q30", 4),
        # help-seeking behavior — impacted students often stop seeking help
        ("help_seeking_behavior",  "q40", 5),
        # study breaks improve performance when sleep-deprived
        ("study_breaks",           "q40", 6),
    ],
}


# =============================================================================
# SECTION 2 — CROSS-DOMAIN TRIGGERS
#
# These fire based on COMBINATIONS of answer values — capturing the
# interaction effects that single-cause posteriors cannot detect alone.
#
# Design principles:
#   - Each condition checks 2-3 specific answer values from different domains
#   - Add-ons are selected to bridge the gap between the interacting domains
#   - clinical=True triggers override slot budget and fire in all variants
#   - Conditions use .get() with safe defaults to handle partial sessions
#
# These are checked BEFORE single-cause trigger rules in select_addons().
# Clinical triggers are checked before all others.
# =============================================================================

CROSS_DOMAIN_TRIGGERS = [

    {
        "id":          "XD4",
        "label":       "Depression + Sleep Deprivation (Clinical)",
        "condition":   lambda answers, posteriors: (
            answers.get("depression_symptoms") in ["often", "every_day"] and
            answers.get("sleep_hours") in ["less_than_4", "four_to_six"]
        ),
        "addons":      [
            "therapy_attendance",    # most urgent — get them into support
            "trauma_or_grief",       # identify acute causal event
            "loneliness_levels",     # most common depression amplifier
            "optimism_outlook",      # severity gauge
        ],
        "min_variant": "q20",        # eligible from all variants
        "clinical":    True,         # OVERRIDES SLOT BUDGET — always fires
        "note":        "Mirrors CF1/CF5 in bayes_engine. When this fires, "
                       "interface.py must display the clinical referral "
                       "message regardless of other output.",
    },

    {
        "id":          "XD1",
        "label":       "High Stress + Sleep Deprivation",
        "condition":   lambda answers, posteriors: (
            answers.get("stress_level") == "high" and
            answers.get("sleep_hours") in ["less_than_4", "four_to_six"]
        ),
        "addons":      [
            "rumination_habits",     # mechanism linking stress to insomnia
            "resilience_level",      # protective factor check
            "mindfulness_practice",  # intervention readiness
            "financial_stress",      # stress subtype identification
        ],
        "min_variant": "q20",
        "clinical":    False,
        "note":        "Highest joint posterior pair in evidence — 91% "
                       "(NSF/Wang 2023). High value across all variants.",
    },

    {
        "id":          "XD2",
        "label":       "Screen Use + Irregular Schedule",
        "condition":   lambda answers, posteriors: (
            answers.get("screen_before_bed") in ["often", "always"] and
            answers.get("consistent_sleep_time") == "inconsistent"
        ),
        "addons":      [
            "weekend_sleep_catchup",      # quantifies social jet lag extent
            "social_media_use_at_night",  # specific screen subtype
            "bed_for_sleep_only",         # bed association component
            "bedtime_routine_consistency",# replacement behavior check
        ],
        "min_variant": "q20",
        "clinical":    False,
        "note":        "87% co-occurrence rate (AASM/Bousgheiri 2024). "
                       "Combined intervention more effective than treating "
                       "either factor alone.",
    },

    {
        "id":          "XD3",
        "label":       "Noise + High Stress",
        "condition":   lambda answers, posteriors: (
            answers.get("noisy_environment") == "loud" and
            answers.get("stress_level") == "high"
        ),
        "addons":      [
            "building_maintenance",   # structural noise source
            "room_clutter",           # visual noise amplifying stress
            "neighborhood_safety",    # safety-driven hypervigilance
            "emotional_regulation",   # stress × noise interaction management
        ],
        "min_variant": "q30",
        "clinical":    False,
        "note":        "84% joint posterior (Altun 2012/Wang 2023). "
                       "Noise is most disruptive when stress is already high "
                       "— hypervigilant students wake from quieter sounds.",
    },

    {
        "id":          "XD5",
        "label":       "Late Caffeine + Sleep Deprivation",
        "condition":   lambda answers, posteriors: (
            answers.get("caffeine_timing") in ["evening", "late_night"] and
            answers.get("sleep_hours") in ["less_than_4", "four_to_six"]
        ),
        "addons":      [
            "fluid_intake_timing",   # late fluid compounds caffeine effects
            "sugary_food_intake",    # sugar spikes add to stimulation
            "fasting_habits",        # empty stomach amplifies caffeine impact
        ],
        "min_variant": "q30",
        "clinical":    False,
        "note":        "80% joint posterior (NSF). Late caffeine with short "
                       "sleep creates a compounding deprivation cycle.",
    },
]


# =============================================================================
# SECTION 3 — VARIANT THRESHOLDS
#
# The minimum posterior elevation required for a cause to trigger its
# add-on rules. Lower thresholds = more add-ons selected = more detailed
# session. These align with the variant design from the architecture doc.
#
# Also defines the add-on budget (M) per variant — how many add-on slots
# are available after cores are asked.
# =============================================================================

VARIANT_CONFIG = {
    "q20": {
        "name":            "Quick",
        "total_questions": 20,
        "core_count":      15,
        "addon_budget":    5,
        "threshold":       0.65,   # only strongest posterior elevations trigger
        "description":     "~5-10 minutes. Core sleep patterns only.",
    },
    "q30": {
        "name":            "Balanced",
        "total_questions": 30,
        "core_count":      20,
        "addon_budget":    10,
        "threshold":       0.55,
        "description":     "~10-15 minutes. Recommended for most students.",
    },
    "q40": {
        "name":            "Detailed",
        "total_questions": 40,
        "core_count":      25,
        "addon_budget":    15,
        "threshold":       0.45,
        "description":     "~15-20 minutes. Comprehensive sleep analysis.",
    },
    "q50": {
        "name":            "Full Dive",
        "total_questions": 50,
        "core_count":      30,
        "addon_budget":    25,
        "threshold":       0.35,   # even weak signals trigger add-ons
        "description":     "~20-30 minutes. Maximum accuracy and detail.",
    },
}


# =============================================================================
# SECTION 4 — HELPER FUNCTIONS
# Used by session_manager.py to select and score add-ons.
# =============================================================================

def get_eligible_addons(cause, variant, asked_ids, posteriors):
    """
    Returns eligible add-on question IDs for a given cause and variant.

    Filters the trigger rule list for the cause by:
      1. min_variant is reachable from the current variant
      2. question has not already been asked (not in asked_ids)

    Scores each eligible add-on as: posterior × (1 / priority_rank)
    Higher score = ask sooner.

    Args:
        cause      (str):  cause name — key in TRIGGER_RULES
        variant    (str):  current session variant ('q20'|'q30'|'q40'|'q50')
        asked_ids  (set):  question IDs already asked in this session
        posteriors (dict): current posteriors from bayes_engine

    Returns:
        list of (score, question_id) tuples, sorted by score descending
    """
    VARIANT_ORDER = ["q20", "q30", "q40", "q50"]
    current_index = VARIANT_ORDER.index(variant)

    cause_posterior = posteriors.get(cause, 0.0)
    rules = TRIGGER_RULES.get(cause, [])
    eligible = []

    for (q_id, min_variant, priority) in rules:
        # Skip if already asked
        if q_id in asked_ids:
            continue
        # Skip if this add-on requires a higher variant than current
        if VARIANT_ORDER.index(min_variant) > current_index:
            continue
        score = cause_posterior * (1.0 / priority)
        eligible.append((score, q_id))

    return sorted(eligible, key=lambda x: x[0], reverse=True)


def get_triggered_cross_domain(answers, posteriors, variant, asked_ids):
    """
    Evaluates all cross-domain triggers and returns eligible add-ons.

    Clinical triggers (XD4) are returned regardless of variant or budget.
    Non-clinical triggers respect the min_variant setting.

    Args:
        answers    (dict): current session answers
        posteriors (dict): current posteriors from bayes_engine
        variant    (str):  current session variant
        asked_ids  (set):  questions already asked

    Returns:
        clinical_addons (list): add-on IDs from clinical triggers — MUST ask
        standard_addons (list): add-on IDs from non-clinical triggers
        triggered_ids   (list): IDs of cross-domain triggers that fired
    """
    VARIANT_ORDER = ["q20", "q30", "q40", "q50"]
    current_index = VARIANT_ORDER.index(variant)

    clinical_addons = []
    standard_addons = []
    triggered_ids   = []

    # Check XD4 (clinical) first — highest priority
    xd4 = CROSS_DOMAIN_TRIGGERS[0]  # XD4 is first entry
    if xd4["condition"](answers, posteriors):
        triggered_ids.append(xd4["id"])
        for q_id in xd4["addons"]:
            if q_id not in asked_ids and q_id not in clinical_addons:
                clinical_addons.append(q_id)

    # Check remaining non-clinical triggers
    for trigger in CROSS_DOMAIN_TRIGGERS[1:]:
        if VARIANT_ORDER.index(trigger["min_variant"]) > current_index:
            continue
        if trigger["condition"](answers, posteriors):
            triggered_ids.append(trigger["id"])
            for q_id in trigger["addons"]:
                if (q_id not in asked_ids and
                        q_id not in clinical_addons and
                        q_id not in standard_addons):
                    standard_addons.append(q_id)

    return clinical_addons, standard_addons, triggered_ids
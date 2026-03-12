/*  =========================================================================
    sleepwise.pl  —  SleepWise Sleep Quality Advisor
    Knowledge Base (SWI-Prolog)

    Architecture:
      - Single dynamic predicate:  user_fact/2
      - 29 cause rules             sleep_cause/1
      - Severity calculator        sleep_severity/1
      - Domain pattern             sleep_domain/1
      - Complaint classifier       sleep_complaint/1
      - Clinical flag checker      sleep_clinical_flag/2
      - Recommendation generator   recommendation/2  (one per cause)
      - Reset predicate            reset_session/0

    Bridge contract with interface.py:
      interface.py asserts:  assertz(user_fact(question_id, answer_value))
      interface.py queries:  sleep_cause(Cause)
                             sleep_severity(Severity)
                             recommendation(Cause, Rec)
      interface.py resets:   retractall(user_fact(_, _))

    All question IDs and answer values match question_bank.py exactly.
    Cause names match bayes_engine.py CAUSES dict exactly.

    Group KENS — Ofori Kennedy Atta (22110500) | Ofori Kenneth Atta (22173900)
    DCIT 313: Introduction to Artificial Intelligence — University of Ghana
    =========================================================================
*/


% ─────────────────────────────────────────────────────────────────────────────
% DYNAMIC DECLARATION
% Single predicate bridges Python answers into Prolog.
% interface.py asserts user_fact(QuestionId, AnswerValue) for every answer.
% ─────────────────────────────────────────────────────────────────────────────

:- dynamic user_fact/2.


% ─────────────────────────────────────────────────────────────────────────────
% HELPER: member/2  (available in SWI-Prolog built-in, redefined for safety)
% ─────────────────────────────────────────────────────────────────────────────

% member/2 is built-in in SWI-Prolog — no redefinition needed.
% Using it as: member(Value, [val1, val2, ...])


% ─────────────────────────────────────────────────────────────────────────────
% SECTION 1 — CAUSE RULES  (sleep_cause/1)
%
% Pattern:
%   sleep_cause(cause_name) :-
%       user_fact(question_id, Value),
%       member(Value, [problem_values]).
%
% Each cause has one PRIMARY rule (the core indicator question).
% Some causes have a SECONDARY rule via OR — two separate clauses.
% Prolog's open-world assumption: if the question was not asked
% (user_fact not asserted), the rule simply fails — correct behaviour.
% ─────────────────────────────────────────────────────────────────────────────

% ── LIFESTYLE CAUSES ─────────────────────────────────────────────────────────

% High caffeine consumption disrupts sleep onset
sleep_cause(high_caffeine) :-
    user_fact(caffeine_intake, Value),
    member(Value, [medium, high]).

% Heavy meals or night-snacking disrupt sleep
sleep_cause(poor_diet_habits) :-
    user_fact(heavy_meal_before_bed, Value),
    member(Value, [often, always]).

% Sedentary lifestyle reduces sleep quality
sleep_cause(sedentary_lifestyle) :-
    user_fact(physical_activity_level, Value),
    member(Value, [none, low]).

% Alcohol or substance use suppresses REM sleep
sleep_cause(substance_use) :-
    user_fact(alcohol_consumption, Value),
    member(Value, [often, daily]).

% Recreational drug use also fires substance_use
sleep_cause(substance_use) :-
    user_fact(recreational_drug_use, Value),
    member(Value, [often, frequently]).

% Late fluid intake causes night-time wakeups (nocturia)
sleep_cause(poor_hydration) :-
    user_fact(fluid_intake_timing, Value),
    member(Value, [late, in_bed]).

% Daily medication (prescription or non-prescription) may interfere with sleep
sleep_cause(medication_interference) :-
    user_fact(medication_supplements, Value),
    member(Value, [daily_nonrx, daily_rx]).


% ── PSYCHOLOGICAL CAUSES ─────────────────────────────────────────────────────

% High stress is the strongest single predictor of poor sleep
sleep_cause(high_stress) :-
    user_fact(stress_level, high).

% Anxiety delays sleep onset and causes early waking
sleep_cause(anxiety) :-
    user_fact(anxiety_levels, Value),
    member(Value, [often, every_night]).

% Panic attacks are also sufficient for anxiety cause
sleep_cause(anxiety) :-
    user_fact(panic_attacks, Value),
    member(Value, [often, frequently]).

% Depression disrupts sleep architecture
sleep_cause(depression) :-
    user_fact(depression_symptoms, Value),
    member(Value, [often, every_day]).

% Burnout causes both hypersomnia and insomnia patterns
sleep_cause(burnout) :-
    user_fact(burnout_feelings, Value),
    member(Value, [often, constantly]).

% Rumination (replaying thoughts) prevents sleep onset
sleep_cause(rumination) :-
    user_fact(rumination_habits, Value),
    member(Value, [often, always]).

% Worry before bed is also a rumination indicator
sleep_cause(rumination) :-
    user_fact(worry_before_bed, Value),
    member(Value, [often, always]).

% Poor self-control over sleep schedule
sleep_cause(poor_self_control) :-
    user_fact(consistent_sleep_time, inconsistent).

% ADHD symptoms also indicate poor self-control over sleep
sleep_cause(poor_self_control) :-
    user_fact(adhd_symptoms, Value),
    member(Value, [moderate, severe]).

% Perfectionism raises pre-sleep arousal
sleep_cause(perfectionism) :-
    user_fact(perfectionism_tendencies, Value),
    member(Value, [often, always]).

% Low resilience means poor recovery from sleep disruption
sleep_cause(low_resilience) :-
    user_fact(resilience_level, Value),
    member(Value, [poorly, very_poorly]).


% ── ENVIRONMENTAL CAUSES ─────────────────────────────────────────────────────

% Noise is the most common environmental disruptor
sleep_cause(noise_disturbance) :-
    user_fact(noisy_environment, loud).

% Partner snoring also causes noise disturbance
sleep_cause(noise_disturbance) :-
    user_fact(partner_snoring, Value),
    member(Value, [often, always]).

% Light exposure suppresses melatonin production
sleep_cause(light_disturbance) :-
    user_fact(light_exposure_at_night, Value),
    member(Value, [often, always]).

% Electronic devices in the room contribute to light disturbance
sleep_cause(light_disturbance) :-
    user_fact(electronic_devices_in_room, Value),
    member(Value, [several, many]).

% Thermal discomfort prevents deep sleep
sleep_cause(temperature_discomfort) :-
    user_fact(uncomfortable_temperature, Value),
    member(Value, [too_hot, too_cold]).

% High room clutter is associated with poor sleep environment
sleep_cause(poor_sleep_space) :-
    user_fact(room_clutter, high).

% Uncomfortable bed directly disrupts sleep
sleep_cause(poor_sleep_space) :-
    user_fact(bed_comfort, uncomfortable).

% Safety concerns raise cortisol — prevent deep sleep
sleep_cause(safety_concern) :-
    user_fact(neighborhood_safety, Value),
    member(Value, [moderate, very_concerned]).


% ── BEHAVIORAL CAUSES ────────────────────────────────────────────────────────

% Screen use before bed delays melatonin and sleep onset
sleep_cause(excessive_screen_use) :-
    user_fact(screen_before_bed, Value),
    member(Value, [often, always]).

% Social media use at night is a specific screen sub-cause
sleep_cause(excessive_screen_use) :-
    user_fact(social_media_use_at_night, Value),
    member(Value, [moderate, long]).

% Inconsistent sleep schedule disrupts the circadian rhythm
sleep_cause(irregular_schedule) :-
    user_fact(consistent_sleep_time, inconsistent).

% Large weekend sleep catch-up also signals irregular schedule
sleep_cause(irregular_schedule) :-
    user_fact(weekend_sleep_catchup, Value),
    member(Value, [much_more, far_more]).

% No bedtime routine means no physiological sleep signal
sleep_cause(poor_sleep_hygiene) :-
    user_fact(bedtime_routine_consistency, Value),
    member(Value, [rarely, no]).

% Excessive napping reduces homeostatic sleep pressure
sleep_cause(excessive_napping) :-
    user_fact(daytime_nap_hours, Value),
    member(Value, [moderate, long]).

% Slow sleep onset indicates poor sleep efficiency
sleep_cause(poor_sleep_efficiency) :-
    user_fact(sleep_latency, Value),
    member(Value, [slow, very_slow]).

% Frequent wakeups also indicate poor sleep efficiency
sleep_cause(poor_sleep_efficiency) :-
    user_fact(frequent_wakeups, Value),
    member(Value, [several, many]).

% Diagnosed or suspected sleep disorder confirms poor efficiency
sleep_cause(poor_sleep_efficiency) :-
    user_fact(sleep_disorders, Value),
    member(Value, [suspected, diagnosed_mild, diagnosed_severe]).


% ── ACADEMIC CAUSES ──────────────────────────────────────────────────────────

% Short sleep duration is a direct academic cause
sleep_cause(poor_sleep_duration) :-
    user_fact(sleep_hours, Value),
    member(Value, [less_than_4, four_to_six]).

% Heavy academic workload drives sleep loss
sleep_cause(academic_overload) :-
    user_fact(academic_workload, heavy).

% Employment on top of studies also causes overload
sleep_cause(academic_overload) :-
    user_fact(employment_status, Value),
    member(Value, [part_time, full_time]).

% Studying past midnight directly causes short sleep
sleep_cause(late_night_studying) :-
    user_fact(study_past_midnight, Value),
    member(Value, [often, always]).

% Cramming style also indicates late-night studying pattern
sleep_cause(late_night_studying) :-
    user_fact(exam_preparation_style, Value),
    member(Value, [often, always]).

% Active exam period is the primary exam pressure indicator
sleep_cause(exam_pressure) :-
    user_fact(exam_period, yes).

% High external pressure from peers/family also signals exam pressure
sleep_cause(exam_pressure) :-
    user_fact(academic_pressure_peers_family, Value),
    member(Value, [moderate, high]).

% Frequent academic performance impact confirms the problem
sleep_cause(performance_impact) :-
    user_fact(performance_impact, Value),
    member(Value, [often, every_day]).

% Frequent lecture absence is also a performance impact indicator
% Frequent absence (never/rarely attending) indicates performance impact
sleep_cause(performance_impact) :-
    user_fact(lecture_attendance, Value),
    member(Value, [never, rarely]).


% ─────────────────────────────────────────────────────────────────────────────
% SECTION 2 — SEVERITY  (sleep_severity/1)
%
% Counts how many causes fire and checks anchor questions.
% Mirrors the four-level system in bayes_engine.py.
% Returns: none | mild | moderate | severe
% ─────────────────────────────────────────────────────────────────────────────

sleep_severity(severe) :-
    % Severe: 4+ causes OR short sleep + depression OR sleep disorder
    (   findall(C, sleep_cause(C), Cs), length(Cs, N), N >= 4
    ;   user_fact(sleep_hours, Value),
        member(Value, [less_than_4, four_to_six]),
        user_fact(depression_symptoms, D),
        member(D, [often, every_day])
    ;   user_fact(sleep_disorders, diagnosed_severe)
    ),
    !.

sleep_severity(moderate) :-
    % Moderate: 2-3 causes OR sleep hours short
    (   findall(C, sleep_cause(C), Cs), length(Cs, N), N >= 2
    ;   user_fact(sleep_hours, Value),
        member(Value, [less_than_4, four_to_six])
    ),
    !.

sleep_severity(mild) :-
    % Mild: at least 1 cause fires
    sleep_cause(_),
    !.

sleep_severity(none).


% ─────────────────────────────────────────────────────────────────────────────
% SECTION 3 — DOMAIN PATTERN  (sleep_domain/1)
%
% Returns the domain with the most fired causes.
% Used by interface.py for the domain pattern display.
% ─────────────────────────────────────────────────────────────────────────────

% Domain membership for each cause
cause_domain(high_caffeine,        lifestyle).
cause_domain(poor_diet_habits,     lifestyle).
cause_domain(sedentary_lifestyle,  lifestyle).
cause_domain(substance_use,        lifestyle).
cause_domain(poor_hydration,       lifestyle).
cause_domain(medication_interference, lifestyle).
cause_domain(high_stress,          psychological).
cause_domain(anxiety,              psychological).
cause_domain(depression,           psychological).
cause_domain(burnout,              psychological).
cause_domain(rumination,           psychological).
cause_domain(poor_self_control,    psychological).
cause_domain(perfectionism,        psychological).
cause_domain(low_resilience,       psychological).
cause_domain(noise_disturbance,    environmental).
cause_domain(light_disturbance,    environmental).
cause_domain(temperature_discomfort, environmental).
cause_domain(poor_sleep_space,     environmental).
cause_domain(safety_concern,       environmental).
cause_domain(excessive_screen_use, behavioral).
cause_domain(irregular_schedule,   behavioral).
cause_domain(poor_sleep_hygiene,   behavioral).
cause_domain(excessive_napping,    behavioral).
cause_domain(poor_sleep_efficiency,behavioral).
cause_domain(poor_sleep_duration,  academic).
cause_domain(academic_overload,    academic).
cause_domain(late_night_studying,  academic).
cause_domain(exam_pressure,        academic).
cause_domain(performance_impact,   academic).

% Count fired causes per domain
domain_count(Domain, Count) :-
    findall(C, (sleep_cause(C), cause_domain(C, Domain)), Cs),
    length(Cs, Count).

% Return the dominant domain
sleep_domain(Domain) :-
    member(Domain, [psychological, academic, behavioral, environmental, lifestyle]),
    domain_count(Domain, Count),
    Count > 0,
    \+ (
        member(OtherDomain, [psychological, academic, behavioral, environmental, lifestyle]),
        OtherDomain \= Domain,
        domain_count(OtherDomain, OtherCount),
        OtherCount > Count
    ),
    !.

sleep_domain(none).


% ─────────────────────────────────────────────────────────────────────────────
% SECTION 4 — SLEEP COMPLAINTS  (sleep_complaint/1)
%
% Classifies the type of sleep problem based on core answers.
% Multiple complaints can be true simultaneously.
% ─────────────────────────────────────────────────────────────────────────────

sleep_complaint(sleep_deprivation) :-
    user_fact(sleep_hours, Value),
    member(Value, [less_than_4, four_to_six]).

sleep_complaint(insomnia) :-
    user_fact(sleep_latency, Value),
    member(Value, [slow, very_slow]).

sleep_complaint(maintenance_insomnia) :-
    user_fact(frequent_wakeups, Value),
    member(Value, [several, many]).

sleep_complaint(hypersomnia) :-
    user_fact(daytime_nap_hours, Value),
    member(Value, [moderate, long]),
    user_fact(morning_sleepiness, Value2),
    member(Value2, [groggy, extremely_tired]).

sleep_complaint(circadian_disruption) :-
    user_fact(consistent_sleep_time, inconsistent),
    user_fact(screen_before_bed, Value),
    member(Value, [often, always]).

sleep_complaint(stress_related_insomnia) :-
    user_fact(stress_level, high),
    user_fact(sleep_latency, Value),
    member(Value, [slow, very_slow]).


% ─────────────────────────────────────────────────────────────────────────────
% SECTION 5 — CLINICAL FLAGS  (sleep_clinical_flag/2)
%
% Mirrors CF1-CF5 in bayes_engine.py CLINICAL_FLAG_RULES exactly.
% Returns flag ID and label.
% ─────────────────────────────────────────────────────────────────────────────

sleep_clinical_flag('CF1', 'Severe Depression with Sleep Deprivation') :-
    user_fact(depression_symptoms, Value),
    member(Value, [often, every_day]),
    user_fact(sleep_hours, less_than_4).

sleep_clinical_flag('CF2', 'Anxiety with Panic Attacks') :-
    user_fact(anxiety_levels, every_night),
    user_fact(panic_attacks, Value),
    member(Value, [often, frequently]).

sleep_clinical_flag('CF3', 'Diagnosed Severe Sleep Disorder') :-
    user_fact(sleep_disorders, diagnosed_severe).

sleep_clinical_flag('CF4', 'Burnout with Depression') :-
    user_fact(burnout_feelings, constantly),
    user_fact(depression_symptoms, Value),
    member(Value, [often, every_day]).

sleep_clinical_flag('CF5', 'Triple Psychological Overload') :-
    user_fact(depression_symptoms, D),
    member(D, [often, every_day]),
    user_fact(anxiety_levels, A),
    member(A, [often, every_night]),
    user_fact(sleep_hours, H),
    member(H, [less_than_4, four_to_six]).


% ─────────────────────────────────────────────────────────────────────────────
% SECTION 6 — RECOMMENDATIONS  (recommendation/2)
%
% One targeted, evidence-backed recommendation per cause.
% Prolog atoms cannot contain spaces — recommendations are returned
% as Prolog strings (double-quoted in SWI-Prolog with flag double_quotes=atom).
% interface.py receives them via query and displays them directly.
%
% Each recommendation is specific, actionable, and cites the mechanism.
% ─────────────────────────────────────────────────────────────────────────────

:- set_prolog_flag(double_quotes, atom).

% ── Lifestyle ────────────────────────────────────────────────────────────────

recommendation(high_caffeine,
    "Stop all caffeine after 2 PM. Caffeine has a 5-6 hour half-life, meaning a 3 PM coffee still has half its dose active at 8 PM. Switch to herbal tea or water after lunch.").

recommendation(poor_diet_habits,
    "Finish eating at least 2 hours before bed. Heavy meals raise core body temperature and cause acid reflux — both directly fragment sleep. A light snack is fine if hungry.").

recommendation(sedentary_lifestyle,
    "Add 20-30 minutes of brisk walking daily — even a post-dinner walk significantly improves deep sleep. Avoid intense exercise within 2 hours of bedtime as it raises core temperature.").

recommendation(substance_use,
    "Avoid alcohol within 3 hours of sleep. Although alcohol feels sedating, it suppresses REM sleep in the second half of the night, causing unrefreshing sleep and early waking.").

recommendation(poor_hydration,
    "Drink the majority of your daily water before 6 PM and taper off sharply after dinner. This prevents nocturia (night-time waking to urinate) without compromising hydration.").

recommendation(medication_interference,
    "Check your medication timing with a pharmacist. Several common medications — including some antihistamines, decongestants, and antidepressants — have activating or sedating effects that depend entirely on when they are taken.").

% ── Psychological ────────────────────────────────────────────────────────────

recommendation(high_stress,
    "Write tomorrow's top 3 tasks on paper before bed and physically close the notebook. Externalising your task list removes the cognitive need to 'keep it in mind', directly reducing pre-sleep arousal.").

recommendation(anxiety,
    "Practice 4-7-8 breathing at bedtime: inhale for 4 seconds, hold for 7, exhale for 8. This activates the parasympathetic nervous system and lowers heart rate within 3-4 cycles.").

recommendation(depression,
    "Contact UG Counselling Centre for a free first session. Depression and poor sleep form a reinforcing cycle — sleep deprivation worsens mood, and low mood worsens sleep. Professional support is the most effective way to break this cycle.").

recommendation(burnout,
    "Identify one task, commitment, or responsibility you can drop or defer this week. Recovery from burnout requires reducing load — rest alone is not sufficient when the source of overload continues.").

recommendation(rumination,
    "Set a 10-minute 'worry time' between 7-8 PM. Write every concern down. When thoughts intrude at bedtime, remind yourself they are already captured. This contains the rumination loop to a specific window.").

recommendation(poor_self_control,
    "Set a fixed alarm for BOTH sleeping and waking — not just waking up. External anchors are more reliable than willpower for schedule control. Treat bedtime as a non-negotiable appointment.").

recommendation(perfectionism,
    "Write 'done' at the top of your to-do list before bed, not 'perfect'. Perfectionism raises pre-sleep cortisol by keeping the brain in evaluation mode. Reframe completion as the evening goal.").

recommendation(low_resilience,
    "Before sleeping, identify one small thing that went well today, however minor. This is not toxic positivity — it is a neurological technique that shifts the brain's final emotional state before sleep consolidation.").

% ── Environmental ────────────────────────────────────────────────────────────

recommendation(noise_disturbance,
    "Use NRR-33 foam earplugs — they reduce ambient noise by approximately 20dB, which is enough to block most conversational and traffic noise. This is the single most evidence-backed intervention for noise disruption.").

recommendation(light_disturbance,
    "Blackout curtains or a sleep mask eliminate the primary source of light-based melatonin suppression. Even low ambient light entering through eyelids is sufficient to reduce melatonin by 50%.").

recommendation(temperature_discomfort,
    "The optimal sleep temperature is 18-20 degrees Celsius. Taking a lukewarm shower 60-90 minutes before bed triggers a core temperature drop on exit, which accelerates sleep onset by up to 10 minutes.").

recommendation(poor_sleep_space,
    "Clear visible clutter from your sleep space this evening. Visual disorder activates the brain's problem-solving networks and prevents the cognitive wind-down needed for sleep onset.").

recommendation(safety_concern,
    "Feeling unsafe in your environment directly elevates nighttime cortisol. Report safety concerns to university housing or campus security. If the issue is structural, document and escalate — this is a health matter, not just a comfort issue.").

% ── Behavioral ───────────────────────────────────────────────────────────────

recommendation(excessive_screen_use,
    "Set a hard screen-off time 45 minutes before bed. The blue-light effect is secondary — the primary issue is cognitive stimulation. Use this time for reading, stretching, or a shower instead.").

recommendation(irregular_schedule,
    "Choose one fixed wake time and hold it every day including weekends. Wake time consistency is more powerful than bedtime consistency for anchoring the circadian rhythm.").

recommendation(poor_sleep_hygiene,
    "Build a 3-step wind-down routine and repeat it every night: for example, shower, read for 20 minutes, lights off. Consistency is the mechanism — the brain learns to associate the sequence with sleep onset.").

recommendation(excessive_napping,
    "Cap naps at 20 minutes and take them before 3 PM. Longer or later naps reduce homeostatic sleep pressure and directly delay the next night's sleep onset by 30-90 minutes.").

recommendation(poor_sleep_efficiency,
    "Use your bed only for sleep. If you cannot sleep after 20 minutes, get up and do something quiet in dim light until sleepy. This retrains the bed-sleep association broken by lying awake.").

% ── Academic ─────────────────────────────────────────────────────────────────

recommendation(poor_sleep_duration,
    "Treat 7 hours as a non-negotiable minimum. Sleep is when memory consolidation from the day's learning occurs — cutting sleep to study more actually reduces net retention.").

recommendation(academic_overload,
    "Map your total weekly hour commitment: lectures + self-study + part-time work + extracurriculars. If it exceeds 60 hours, something must be reduced. An overloaded schedule cannot be fixed with better time management alone.").

recommendation(late_night_studying,
    "Set a hard study cut-off at 10 PM. Material studied after midnight is poorly consolidated due to fatigue interference — you are spending time without gaining proportional benefit.").

recommendation(exam_pressure,
    "Sleep the night before an exam consolidates more learning than a final revision session. The hippocampus transfers short-term memories to long-term storage during sleep — this process cannot be replicated by staying awake.").

recommendation(performance_impact,
    "Track your sleep hours and academic output for two weeks. The correlation between sleep quality and concentration, memory, and grades becomes concrete when you see your own data — not abstract advice.").


% ─────────────────────────────────────────────────────────────────────────────
% SECTION 7 — RESET
%
% Called by interface.py between sessions.
% Removes all asserted user_fact/2 clauses.
% ─────────────────────────────────────────────────────────────────────────────

reset_session :-
    retractall(user_fact(_, _)).


% ─────────────────────────────────────────────────────────────────────────────
% SECTION 8 — CONVENIENCE QUERY PREDICATES
%
% Used by interface.py for clean single queries.
% ─────────────────────────────────────────────────────────────────────────────

% All fired causes as a list
all_causes(Causes) :-
    findall(C, sleep_cause(C), Causes).

% All fired complaints as a list
all_complaints(Complaints) :-
    findall(C, sleep_complaint(C), Complaints).

% All active clinical flags as a list of id-label pairs
all_flags(Flags) :-
    findall(Id-Label, sleep_clinical_flag(Id, Label), Flags).

% All recommendations for fired causes
all_recommendations(Recs) :-
    findall(Cause-Rec,
            (sleep_cause(Cause), recommendation(Cause, Rec)),
            Recs).

% Full diagnosis in one query
full_prolog_diagnosis(Severity, Causes, Domain, Complaints, Flags) :-
    sleep_severity(Severity),
    all_causes(Causes),
    sleep_domain(Domain),
    all_complaints(Complaints),
    all_flags(Flags).
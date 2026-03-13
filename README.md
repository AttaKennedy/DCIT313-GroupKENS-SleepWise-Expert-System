# SleepWise
### Sleep Quality Advisor — Expert System
**DCIT 313: Introduction to Artificial Intelligence | Group KENS | University of Ghana | 2025/2026**

---

## What It Does

SleepWise asks a university student between 20 and 50 questions about their daily habits, stress levels, living environment, and study patterns. It then produces a personalised report showing which factors are hurting their sleep, how serious the problem is, and one specific action to fix each cause.

---

## Group Members

| Name | Student ID |
|---|---|
| Ofori Kennedy Atta | 22110500 |
| Ofori Kenneth Atta | 22173900 |

---

## How It Works

The system has two parts that work together.

**SWI-Prolog** (`knowledge_base/sleepwise.pl`) holds all the intelligence — 29 cause rules across five domains, a four-level severity calculator, six sleep complaint types, five clinical alert flags, and 29 recommendations. 

**Python** (`interface/interface.py`) handles everything the student sees — asking questions, running a Bayesian engine that decides which questions matter most, and displaying the final report. It talks to Prolog through pyswip.

The five domains covered:

| Domain | Examples |
|---|---|
| Lifestyle | Caffeine, diet, alcohol, medications |
| Psychological | Stress, anxiety, depression, burnout |
| Environmental | Noise, light, temperature, room comfort |
| Behavioural | Screen time, sleep schedule, napping |
| Academic | Study hours, exam pressure, workload |

---

## Repository Structure

```
DCIT313-GroupKENS-SleepWise-Expert-System/
│
├── knowledge_base/
│   └── sleepwise.pl                      # Prolog knowledge base — all rules and facts
│
├── interface/
│   ├── interface.py                      # Main entry point — run this to start
│   ├── bayes_engine.py                   # Bayesian probability engine
│   ├── question_bank.py                  # All 120 questions across 4 session variants
│   ├── session_manager.py                # Session flow and state management
│   ├── trigger_rules.py                  # Adaptive question selection rules
│   ├── test_knowledge_base.py            # 189 unit tests for sleepwise.pl
│   └── test_system_integration.py        # 78 integration tests for the full pipeline
│
├── docs/
│   ├── project_brief.pdf                 # Project planning document
│   ├── knowledge_engineering_report.pdf  # Sources and rule acquisition process
│   ├── test_cases.pdf                    # All 267 test cases with results
│   └── project_report.pdf               # Final technical report
│
└── README.md
```

> `interface.py` is the only required entry point. The other files in `interface/` are supporting modules it imports automatically. The two test scripts are included so the marker can verify the results in `test_cases.pdf` by running them directly.

---

## Requirements

- Python 3.8 or higher
- SWI-Prolog 8.x or higher
- pyswip

```bash
pip install pyswip
```

---

## Running the System

```bash
# 1. Clone the repository
git clone https://github.com/your-repo/DCIT313-GroupKENS-SleepWise-Expert-System.git
cd DCIT313-GroupKENS-SleepWise-Expert-System

# 2. Run the system
cd interface
python interface.py
```

The system will ask you to choose a session length (20, 30, 40, or 50 questions), then walk you through the assessment.

---

## Running the Tests

```bash
cd interface

# Knowledge base tests — 189 tests against sleepwise.pl
python test_knowledge_base.py

# Integration tests — 78 tests on the full Python-Prolog pipeline
python test_system_integration.py
```

All 267 tests should pass. Full test case documentation is in `docs/test_cases.pdf`.

---

## Technology Stack

| Technology | Version | Purpose |
|---|---|---|
| SWI-Prolog | 8.x | Logic engine and knowledge base |
| Python | 3.8+ | Interface, Bayesian engine, session management |
| pyswip | Latest | Python-to-Prolog bridge |

---

## Disclaimer

SleepWise is an educational project built for DCIT 313. It is not a medical tool and is not a substitute for professional advice.

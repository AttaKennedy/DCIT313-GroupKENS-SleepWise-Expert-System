# SleepWise: Expert System for Improving Sleep Quality Among University Students

## DCIT 313: Artificial Intelligence — Group Project
**Group Name:** KENS  
**Repository:** DCIT313-GroupKENS-SleepWise-Expert-System  
**Academic Year:** 2025/2026  

---

## Group Members

| Full Name | Student ID | Role |
|---|---|---|
| Ofori Kennedy Atta | 22110500 | Python Interface Developer & Group Lead |
| Ofori Kenneth Atta | 22173900 | Prolog Developer & Knowledge Engineer |

---

## System Description

SleepWise is a rule-based Expert System built using SWI-Prolog and Python that 
helps university students identify the possible causes of poor sleep quality and 
provides personalized recommendations for improvement.

The system collects responses from the user across five knowledge domains:
- Lifestyle factors (caffeine, diet, exercise)
- Psychological factors (stress, anxiety, academic pressure)
- Environmental factors (noise, light, room temperature)
- Behavioral factors (screen time, sleep schedule, napping)
- Academic factors (late night studying, deadlines, early classes)

Based on the user's responses, the Prolog inference engine reasons through the 
knowledge base and produces a sleep quality profile that includes identified causes, 
severity classification (mild, moderate, or severe), and actionable recommendations.

---

## Repository Structure
```
DCIT313-GroupKENS-SleepWise-Expert-System/
│
├── knowledge_base/
│   └── sleepwise.pl        # SWI-Prolog knowledge base with all facts and rules
│
├── interface/
│   └── interface.py        # Python pyswip interface for user interaction
│
├── docs/
│   ├── project_brief.pdf   # Full project planning document
│   ├── knowledge_engineering_report.pdf  # Sources and rule acquisition process
│   ├── test_cases.pdf      # Positive and negative test scenarios
│   └── project_report.pdf  # Final technical documentation
│
└── README.md
```

---

## Technology Stack

| Technology | Purpose |
|---|---|
| SWI-Prolog | Logic engine — stores and processes all knowledge base rules and facts |
| Python 3.x | Interface language for user interaction and output display |
| pyswip | Python library that bridges user inputs to the Prolog inference engine |
| GitHub | Version control and project submission platform |

---

## How to Run the System

### Requirements
- SWI-Prolog installed on your machine
- Python 3.x installed
- pyswip library installed (`pip install pyswip`)

### Steps
1. Clone the repository
2. Navigate to the `/interface` folder
3. Run `python interface.py`
4. Answer the questions as prompted
5. Receive your personalized sleep quality profile

---

## Individual Contributions

**Ofori Kennedy Atta (22110500)**
- Python pyswip interface development
- User input collection and output formatting
- System testing with positive and negative test cases
- GitHub repository setup and management
- Project documentation and /docs folder

**Ofori Kenneth Atta (22173900)**
- SWI-Prolog knowledge base construction
- Facts and rules authoring across all five domains
- Severity classification logic
- Knowledge engineering documentation
- Rule mapping and decision flow diagram

---

## Disclaimer

SleepWise is designed as an intelligent advisory system for educational purposes 
only. It is not intended to replace professional medical advice or clinical evaluation.

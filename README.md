# Airline Quality Rating: Passenger Satisfaction & Service Quality Intelligence

**Author & Developer:** George. E. Ejembi

**Project Type:** End-to-End Data Analytics & Machine Learning

**Domain:** Airline / Aviation / Customer Experience

**Target Variable:** `Satisfaction`

**Tech Stack:** Excel · PostgreSQL · Power BI · Python · Machine Learning


---

## Project Overview

The **Airline Quality Rating: Passenger Satisfaction & Service Quality Intelligence** project is an end-to-end analytics solution designed to understand, measure, and predict airline passenger satisfaction.

The project combines **passenger demographics, travel characteristics, service-quality ratings, operational delays, and satisfaction outcomes** to identify the factors that most strongly influence the passenger experience.

Rather than treating the project as a dashboard-only exercise, the workflow progresses through multiple analytical layers:

> **Excel → PostgreSQL → Power BI → Python & Machine Learning**

Each layer serves a specific analytical purpose:

* **Excel** — Initial data exploration, quality assessment, cleaning, and observation logging.
* **PostgreSQL** — Data profiling, relational structuring, transformation, and analytical intelligence layers.
* **Power BI** — Business-facing visualization, KPI analysis, segmentation, and service-quality intelligence.
* **Python & Machine Learning** — Statistical analysis, predictive modeling, feature importance, model evaluation, and advanced passenger-satisfaction analytics.

The ultimate objective is to move from:

> **What happened? → Why did it happen? → Who is affected? → What is likely to happen? → What should the airline do?**

---

# Business Objective

Airlines operate in an environment where passenger experience directly influences customer retention, loyalty, reputation, and revenue.

This project aims to provide decision-makers with analytical evidence to answer five core questions:

1. **Who are the satisfied and dissatisfied passengers?**
2. **Which service-quality factors have the greatest influence on satisfaction?**
3. **Which passenger segments are most vulnerable to dissatisfaction?**
4. **Where should the airline prioritize service improvements?**
5. **Can passenger satisfaction be predicted from demographic, operational, and service-quality data?**

The project therefore connects descriptive analytics with predictive and decision intelligence.

---

# Key Analytical Questions

### Passenger Satisfaction

* What proportion of passengers are satisfied versus dissatisfied?
* How does satisfaction vary across passenger types?
* How does satisfaction differ by travel class?
* Are loyal customers more likely to be satisfied?
* Does satisfaction vary by customer type or travel purpose?

### Service Quality

* Which service dimensions have the strongest relationship with satisfaction?
* Which services receive the lowest passenger ratings?
* Are some services consistently associated with dissatisfaction?
* Which service-quality improvements could potentially generate the largest satisfaction gains?

### Operational Performance

* How do departure delays affect passenger satisfaction?
* How do arrival delays affect satisfaction?
* Are delays disproportionately affecting particular passenger segments?
* Is there a threshold at which operational delays become particularly damaging?

### Passenger Segmentation

* Which passenger groups have the highest dissatisfaction rates?
* Which segments generate the greatest potential improvement opportunity?
* Are business and personal travelers affected differently?
* Does customer loyalty change the relationship between service quality and satisfaction?

### Predictive Analytics

* Can satisfaction be predicted using the available passenger information?
* Which features contribute most strongly to prediction?
* How accurately can the model identify dissatisfied passengers?
* Can model outputs be translated into actionable service interventions?

---

# Analytical Framework

The project follows a layered intelligence framework:

```text
                         AIRLINE QUALITY RATING
                                  │
                                  ▼
                         DATA FOUNDATION
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                  Excel                    PostgreSQL
                    │                           │
             Data Exploration             Data Modeling
             Cleaning                     Profiling
             Observation Logs             Transformation
                    │                           │
                    └─────────────┬─────────────┘
                                  │
                                  ▼
                             POWER BI
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
               Descriptive                Diagnostic
                Analytics                  Analytics
                    │                           │
                    └─────────────┬─────────────┘
                                  │
                                  ▼
                       ANALYTICAL RESULTS
                                  │
                                  ▼
                         PYTHON & MACHINE
                             LEARNING
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
              Prediction                  Feature
                                         Importance
                    │                           │
                    └─────────────┬─────────────┘
                                  │
                                  ▼
                        DECISION INTELLIGENCE
                                  │
                                  ▼
                   SERVICE IMPROVEMENT PRIORITIES
```

---

# Data Analytics Workflow

## 1. Excel — Data Exploration & Quality Assessment

Excel serves as the initial analytical environment.

The objective at this stage is to understand the structure and quality of the source data before introducing database transformations.

### Activities

* Initial dataset inspection
* Column and data-type review
* Missing-value assessment
* Duplicate assessment
* Outlier identification
* Category consistency checks
* Value-range validation
* Initial satisfaction distribution analysis
* Preliminary relationship exploration
* Data-quality observation logging

### Repository Files

```text
excel/
├── 01_raw_data_review.xlsx
├── 02_cleaning_log.xlsx
└── 03_eda_observations.xlsx
```

The Excel stage establishes a documented record of the initial data condition and analytical observations.

---

# 2. PostgreSQL — Data Engineering & Intelligence Layer

PostgreSQL provides the structured analytical foundation for the project.

The database layer is designed to move the project from spreadsheet-based exploration toward a reproducible and scalable analytical workflow.

### PostgreSQL Responsibilities

* Data ingestion
* Schema creation
* Data profiling
* Data validation
* Structural transformation
* Analytical views
* Derived metrics
* Intelligence layers
* Query-based analysis

### SQL Workflow

```text
Raw Dataset
     │
     ▼
Schema Creation
     │
     ▼
Data Profiling
     │
     ▼
Data Structuring
     │
     ▼
Analytical Views
     │
     ▼
Intelligence Layers
```

### Repository Structure

```text
sql/
├── 01_create_schema.sql
├── 02_data_profiling.sql
├── 03_structuring_views.sql
└── 04_intelligence_layers.sql
```

---

# 3. Power BI — Passenger & Service Quality Intelligence

Power BI transforms the structured analytical data into an interactive business intelligence environment.

The dashboard is intended to provide both **executive-level visibility** and **analytical drill-down capability**.

## Core Dashboard Areas

### Executive Overview

Provides a high-level view of:

* Total passengers
* Satisfaction rate
* Dissatisfaction rate
* Average service rating
* Average departure delay
* Average arrival delay
* Passenger distribution
* Key satisfaction drivers

### Passenger Satisfaction

Analyzes satisfaction across:

* Customer type
* Passenger type
* Travel class
* Travel purpose
* Demographic groups
* Operational conditions

### Service Quality

Examines passenger ratings across relevant service dimensions.

Potential analytical dimensions include:

* Online booking
* Check-in
* Boarding
* Seat comfort
* Food and drink
* In-flight service
* Entertainment
* Cleanliness
* Wi-Fi / connectivity
* Baggage handling
* Gate and boarding experience

### Operational Performance

Analyzes:

* Departure delays
* Arrival delays
* Delay distributions
* Delay impact by passenger segment
* Satisfaction under different operational conditions

### Segment Intelligence

Identifies high-risk passenger groups through combinations of:

* Satisfaction
* Passenger characteristics
* Service ratings
* Operational performance

---

# 4. Python & Machine Learning

Python provides the advanced analytical layer of the project.

The objective is to determine whether passenger satisfaction can be predicted from available passenger, service, and operational characteristics.

## Analytical Objectives

### Predictive Modeling

The primary target variable is:

```text
Satisfaction
```

The modeling workflow will evaluate classification algorithms appropriate for binary passenger-satisfaction prediction.

Potential models include:

* Logistic Regression
* Decision Tree
* Random Forest
* Gradient Boosting
* XGBoost
* LightGBM

Model selection will ultimately depend on empirical performance rather than algorithm preference.

---

## Model Evaluation

Because satisfaction prediction is a classification problem, model performance will be evaluated using appropriate classification metrics.

### Primary Metrics

* Accuracy
* Precision
* Recall
* F1-score
* ROC-AUC
* Confusion Matrix

Where class imbalance exists, emphasis will be placed on metrics such as **precision, recall, F1-score, and ROC-AUC** rather than accuracy alone.

---

# Feature Importance & Explainability

Predictive performance alone is insufficient for a business-facing project.

The analysis will therefore investigate **which variables contribute most strongly to satisfaction predictions**.

Potential explainability approaches include:

* Feature importance
* Permutation importance
* SHAP values
* Partial dependence analysis

The objective is to translate model outputs into interpretable business questions:

> Which passenger experience factors should management prioritize?

---

# Intelligence Framework

The project is designed around four levels of analytical intelligence.

| Layer        | Question                  | Output                         |
| ------------ | ------------------------- | ------------------------------ |
| Descriptive  | What happened?            | KPIs & trends                  |
| Diagnostic   | Why did it happen?        | Driver analysis                |
| Predictive   | What is likely to happen? | Satisfaction prediction        |
| Prescriptive | What should be done?      | Service improvement priorities |

This distinction is important because the project is not intended to stop at visualization.

---

# Potential Decision Intelligence Outputs

The analytical results can be translated into actionable airline decisions.

For example:

### High-Impact / Low-Satisfaction Services

If a service dimension demonstrates:

* Low passenger ratings
* Strong relationship with dissatisfaction
* High passenger exposure

then it becomes a potential **service improvement priority**.

### High-Risk Passenger Segments

Passenger groups exhibiting:

* High dissatisfaction rates
* Poor service experiences
* High operational disruption

can be prioritized for targeted interventions.

### Operational Delay Intervention

If delay analysis demonstrates a strong relationship between delays and dissatisfaction, airlines can investigate:

* Delay communication
* Boarding processes
* Ground operations
* Connection management
* Customer recovery strategies

---

# Project Architecture

```text
                        SOURCE DATA
                            │
                            ▼
                    ┌───────────────┐
                    │     Excel     │
                    │               │
                    │ EDA           │
                    │ Cleaning      │
                    │ Observations  │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │  PostgreSQL   │
                    │               │
                    │ Profiling     │
                    │ Transformation│
                    │ Views         │
                    │ Intelligence  │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │    Power BI   │
                    │               │
                    │ KPIs          │
                    │ Segmentation  │
                    │ Diagnostics   │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │ Python & ML   │
                    │               │
                    │ Prediction    │
                    │ Explainability│
                    │ Evaluation    │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │   Decision    │
                    │ Intelligence  │
                    │               │
                    │ Priorities    │
                    │ Interventions │
                    └───────────────┘
```

---

# Repository Structure

```text
airline-quality-rating/
│
├── README.md
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── dictionary/
│
├── excel/
│   ├── 01_raw_data_review.xlsx
│   ├── 02_cleaning_log.xlsx
│   └── 03_eda_observations.xlsx
│
├── sql/
│   ├── 01_create_schema.sql
│   ├── 02_data_profiling.sql
│   ├── 03_structuring_views.sql
│   └── 04_intelligence_layers.sql
│
├── powerbi/
│   ├── airline_quality_rating.pbix
│   └── screenshots/
│
├── python/
│   ├── notebooks/
│   ├── src/
│   ├── models/
│   └── outputs/
│
├── reports/
│   ├── figures/
│   └── final_report.md
│
└── docs/
    ├── business_context.md
    ├── data_dictionary.md
    └── project_log.md
```

---

# Directory Description

| Directory           | Purpose                                                      |
| ------------------- | ------------------------------------------------------------ |
| `data/raw/`         | Original, unmodified source datasets                         |
| `data/processed/`   | Cleaned and transformed datasets                             |
| `data/dictionary/`  | Data dictionaries and field definitions                      |
| `excel/`            | Initial EDA, cleaning documentation, and observations        |
| `sql/`              | PostgreSQL schemas, transformations, views, and intelligence |
| `powerbi/`          | Power BI dashboard and dashboard screenshots                 |
| `python/notebooks/` | Exploratory and modeling notebooks                           |
| `python/src/`       | Reusable Python analytical code                              |
| `python/models/`    | Trained model artifacts                                      |
| `python/outputs/`   | Model results and analytical outputs                         |
| `reports/`          | Final analytical report and figures                          |
| `docs/`             | Project documentation and methodology                        |

---

# Data Structure

The dataset contains passenger-level information covering multiple dimensions of the airline experience.

The analytical feature groups include:

### Passenger Characteristics

* Passenger demographics
* Customer type
* Passenger type
* Travel characteristics

### Flight Characteristics

* Travel class
* Flight distance
* Travel purpose

### Service Quality

* Service ratings
* Passenger experience ratings
* In-flight experience
* Ground-service experience

### Operational Performance

* Departure delay
* Arrival delay

### Target Variable

```text
Satisfaction
```

The complete variable definitions are documented in:

```text
docs/data_dictionary.md
```

---

# Data Quality Framework

Data quality is assessed before analytical modeling.

The project considers:

### Completeness

* Missing values
* Null records
* Incomplete observations

### Validity

* Invalid categorical values
* Unexpected numerical ranges
* Incorrect data types

### Consistency

* Category naming
* Encoding consistency
* Duplicate categories
* Formatting inconsistencies

### Uniqueness

* Duplicate records
* Duplicate passenger observations where applicable

### Integrity

* Relationships between variables
* Logical consistency
* Target-variable validity

All identified issues and remediation steps are documented during the Excel and SQL stages.

---

# Analytical Methodology

The project follows the following sequence:

```text
1. Understand the business problem
          ↓
2. Inspect the source data
          ↓
3. Assess data quality
          ↓
4. Clean and standardize data
          ↓
5. Profile variables using SQL
          ↓
6. Build analytical structures
          ↓
7. Develop Power BI metrics
          ↓
8. Analyze passenger satisfaction
          ↓
9. Identify service-quality drivers
          ↓
10. Segment passengers
          ↓
11. Build predictive models
          ↓
12. Evaluate model performance
          ↓
13. Explain model predictions
          ↓
14. Translate findings into decisions
```

---

# Key Performance Indicators

The project will track a set of passenger experience and operational KPIs.

## Passenger KPIs

* Total passengers
* Satisfied passengers
* Dissatisfied passengers
* Satisfaction rate
* Dissatisfaction rate

## Service KPIs

* Average service rating
* Service-specific satisfaction
* Lowest-rated service
* Highest-rated service
* Service-quality gap

## Operational KPIs

* Average departure delay
* Average arrival delay
* Delay rate
* Satisfaction by delay category

## Segment KPIs

* Satisfaction by passenger type
* Satisfaction by travel class
* Satisfaction by customer type
* Satisfaction by travel purpose

---

# Example Decision Framework

The final analytical layer can use a prioritization framework such as:

```text
                 BUSINESS IMPACT
                       ▲
                       │
          HIGH         │    PRIORITY
                       │
                       │
───────────────────────┼──────────────────────►
                       │
          LOW          │    MONITOR
                       │
                       │
                       ▼
                 LOW PERFORMANCE
```

A more rigorous prioritization score can combine:

```text
Improvement Priority
=
Passenger Exposure
×
Dissatisfaction Impact
×
Business Importance
```

This allows the airline to distinguish between a service that is simply rated poorly and a service problem that represents a **large and strategically important passenger-experience opportunity**.

---

# Machine Learning Workflow

```text
Clean Dataset
      │
      ▼
Feature Engineering
      │
      ▼
Train / Validation / Test Split
      │
      ▼
Baseline Model
      │
      ▼
Candidate Models
      │
      ▼
Hyperparameter Optimization
      │
      ▼
Model Evaluation
      │
      ▼
Feature Importance
      │
      ▼
Explainability
      │
      ▼
Business Interpretation
```

---

# Model Governance

The machine-learning component is intended for **analytical decision support**, not autonomous passenger decision-making.

Model evaluation will consider:

* Predictive performance
* Generalization
* Class imbalance
* Feature leakage
* Interpretability
* Stability
* Business relevance

Particular attention will be given to avoiding leakage between service variables and the target satisfaction label.

---

# Outputs

The project is designed to produce the following outputs:

### Business Intelligence

* Interactive Power BI dashboard
* Passenger satisfaction KPIs
* Service-quality analysis
* Segment analysis
* Operational performance analysis

### Data Engineering

* PostgreSQL analytical schema
* SQL transformation views
* Derived intelligence tables/views

### Machine Learning

* Trained classification models
* Model evaluation metrics
* Feature importance analysis
* Explainability outputs
* Prediction results

### Documentation

* Data dictionary
* Business context
* Data-cleaning documentation
* Analytical methodology
* Project log
* Final analytical report

---

# Dashboard

The Power BI dashboard will provide an interactive interface for exploring:

* Overall satisfaction
* Passenger segments
* Service-quality performance
* Operational delays
* Satisfaction drivers
* High-risk passenger groups

Dashboard file:

```text
powerbi/airline_quality_rating.pbix
```

Screenshots will be maintained in:

```text
powerbi/screenshots/
```

---

# Reproducibility

The project is structured to make the analytical workflow reproducible.

A new analyst should be able to move through the project in the following order:

```text
01 → Excel
02 → PostgreSQL
03 → Power BI
04 → Python
05 → Machine Learning
06 → Final Report
```

Each stage should consume the output of the previous stage rather than relying on undocumented manual transformations.

---

# Project Documentation

Additional documentation is maintained under:

```text
docs/
```

### `business_context.md`

Defines:

* Business problem
* Stakeholders
* Decision requirements
* Analytical objectives

### `data_dictionary.md`

Documents:

* Variables
* Data types
* Definitions
* Business meaning
* Transformation rules

### `project_log.md`

Tracks:

* Development stages
* Data-quality discoveries
* Analytical decisions
* Modeling experiments
* Important changes

---

# Technology Stack

| Technology             | Role                                                |
| ---------------------- | --------------------------------------------------- |
| **Microsoft Excel**    | Initial EDA and data-quality assessment             |
| **PostgreSQL**         | Relational data engineering and analytical SQL      |
| **Power BI**           | Business intelligence and interactive visualization |
| **Python**             | Statistical analysis and machine learning           |
| **Pandas**             | Data manipulation                                   |
| **NumPy**              | Numerical computing                                 |
| **Scikit-learn**       | Machine learning                                    |
| **XGBoost / LightGBM** | Gradient-boosting models where appropriate          |
| **Matplotlib**         | Analytical visualization                            |
| **Git / GitHub**       | Version control and project management              |

---

# Skills Demonstrated

This project demonstrates capabilities across multiple areas of modern analytics.

### Data Analytics

* Exploratory Data Analysis
* Statistical analysis
* KPI development
* Segmentation
* Trend analysis
* Correlation analysis

### Data Engineering

* Relational database design
* SQL transformation
* Data profiling
* Analytical views
* Data-quality management

### Business Intelligence

* Power BI
* DAX
* Interactive dashboard development
* KPI design
* Business storytelling
* Decision-support analytics

### Machine Learning

* Classification
* Feature engineering
* Model evaluation
* Feature importance
* Explainable AI
* Predictive analytics

### Analytical Communication

* Business problem framing
* Insight generation
* Data storytelling
* Decision frameworks
* Technical documentation

---

# Project Maturity Framework

The project intentionally progresses through increasing levels of analytical maturity:

```text
                    ┌─────────────────────────┐
                    │  PRESCRIPTIVE / DECISION│
                    │      INTELLIGENCE       │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │       PREDICTIVE        │
                    │    Machine Learning     │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │       DIAGNOSTIC        │
                    │   Driver & Root Cause   │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │       DESCRIPTIVE       │
                    │       Power BI          │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │       DATA LAYER        │
                    │   Excel + PostgreSQL    │
                    └─────────────────────────┘
```

This progression demonstrates the movement from **data preparation to decision intelligence**, rather than treating analytics as a single visualization exercise.

---

# Future Enhancements

Potential future development includes:

* Automated data ingestion
* Scheduled model retraining
* Passenger-level satisfaction scoring
* SHAP-based explanation dashboards
* Satisfaction probability scoring
* Service-improvement simulation
* Scenario analysis
* Model monitoring
* PostgreSQL-to-Power BI automated refresh
* Python prediction API
* Automated executive reporting

---

# Limitations

Several limitations should be considered when interpreting the results.

1. Observational passenger data does not automatically establish causal relationships.
2. Feature importance should not be interpreted as causal impact.
3. Predictive performance depends on the quality and representativeness of the underlying dataset.
4. Satisfaction is a subjective passenger outcome and may contain measurement bias.
5. Operational recommendations should be evaluated against airline-specific cost and feasibility constraints.
6. Machine-learning predictions should be interpreted as decision-support signals rather than deterministic outcomes.

---

# Ethical & Responsible Analytics

Passenger analytics should be conducted with appropriate attention to:

* Privacy
* Data minimization
* Responsible use of demographic information
* Model fairness
* Interpretability
* Appropriate use of predictive outputs

Demographic variables should be evaluated carefully to determine whether they improve legitimate analytical understanding without introducing inappropriate discriminatory decision-making.

---

# Project Status

**Status:** In Development

### Completed

* [x] Repository architecture
* [x] Business problem definition
* [x] Analytical workflow definition
* [x] Excel EDA framework
* [x] PostgreSQL architecture
* [x] Power BI analytical framework
* [x] Machine-learning framework

### In Progress

* [ ] Data cleaning
* [ ] SQL profiling
* [ ] Analytical views
* [ ] Power BI dashboard
* [ ] Feature engineering
* [ ] Predictive modeling
* [ ] Model explainability
* [ ] Final decision framework

### Planned

* [ ] Final analytical report
* [ ] Model comparison
* [ ] Advanced segmentation
* [ ] Service-improvement prioritization
* [ ] Executive dashboard refinement

---

# Author

**George**

Data Analyst | Machine Learning | Data Intelligence

This project demonstrates an end-to-end approach to transforming passenger-level airline data into **service-quality intelligence, predictive insights, and actionable business decisions**.

---

## Repository

```text
airline-quality-rating/
```

The repository is structured to keep **data preparation, database engineering, business intelligence, machine learning, and reporting** modular and reproducible.

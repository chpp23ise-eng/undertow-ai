# 💰 Undertow

## Governed AI Revenue Recovery

Undertow is an AI-powered revenue recovery agent that analyzes failed revenue events, predicts the most suitable recovery intervention, prioritizes opportunities under limited recovery capacity, and applies deterministic governance before executing recovery actions.

The system is designed around a simple principle:

> Recover more revenue while keeping automated recovery bounded, explainable, and governed.

---

## What Undertow Does

Revenue can be lost because of:

- Failed payments
- Abandoned checkouts
- Failed subscriptions
- Overdue invoices

Instead of blindly retrying every failed transaction, Undertow evaluates multiple possible recovery interventions:

- `RETRY_PAYMENT`
- `SEND_REMINDER`
- `ALTERNATE_PAYMENT`

For each event, Undertow estimates the probability of recovery and calculates the expected recovered revenue.

The best recovery opportunity can then be selected for execution.

---

# 🔄 Recovery Workflow

```text
Failed Revenue Events
        ↓
   Input / Upload
        ↓
   Decision Engine
        ↓
      XGBoost
        ↓
 Best Recovery Action
        ↓
Portfolio Prioritization
        ↓
   Limited Capacity
        ↓
     Governor
     ↙   ↓   ↘
  ALLOW STOP ESCALATE
     ↓
 Recovery Service
     ↓
     Outcome
     ↓
  Agent State
     ↓
   Audit Log
🧠 Decision Engine

Undertow uses an XGBoost-based decision engine to evaluate recovery opportunities.

For every revenue-loss event, the system considers the available interventions and estimates:

Recovery Probability
        ×
Transaction Amount
        =
Expected Recovery

The intervention with the strongest expected recovery opportunity can then be selected.

Example
Event: E00002
Amount: ₹9,668.95

SEND_REMINDER
Recovery probability: ...
Expected recovery: ...

RETRY_PAYMENT
Recovery probability: ...
Expected recovery: ...

ALTERNATE_PAYMENT
Recovery probability: ...
Expected recovery: ...

This allows Undertow to consider both the likelihood of recovery and the economic value of the event.

⚡ Batch Recovery Analysis

Undertow can analyze a batch of failed revenue events.

The batch analysis provides:

Number of transactions
Revenue at input
Expected recovery
Recommended action distribution
Top recovery opportunities
Transaction-level decisions

The application supports multiple sample sizes and can also process uploaded CSV data.

Example sample sizes:

100
500
1,000
2,500
5,000

A new random sample can be generated between runs.

Batch Workflow
Failed Transactions
        ↓
Sample / CSV Upload
        ↓
Decision Engine
        ↓
Recovery Predictions
        ↓
Expected Recovery
        ↓
Recommended Actions
🎯 Portfolio Recovery Optimization

Recovery capacity is often limited.

If there are 5,000 recovery opportunities but only 1,000 recovery actions available, Undertow should not treat every opportunity equally.

The portfolio optimizer ranks opportunities by:

Expected Recovery

and selects the highest-value opportunities within the available capacity.

5,000 Opportunities
        ↓
Rank by Expected Recovery
        ↓
Recovery Capacity = 1,000
        ↓
┌───────────────────┐
│ 1,000 Selected    │
└───────────────────┘

        +

┌───────────────────┐
│ 4,000 Deferred    │
└───────────────────┘

This allows limited recovery capacity to be allocated toward opportunities with greater expected revenue impact.

Portfolio Metrics

Undertow reports:

Total opportunities
Selected opportunities
Deferred opportunities
Total expected recovery
Expected recovery from selected opportunities
Deferred expected recovery
Recovery opportunity captured
🛡️ Deterministic Governance

The recovery agent does not execute every predicted action automatically.

Before an action is executed, Undertow evaluates it through a deterministic governor.

The governor can return three decisions:

🟢 ALLOW

The action satisfies the current recovery rules.

Governor: ALLOW
Execution: EXECUTED

The recovery service can then execute the intervention.

🟠 STOP

The opportunity does not meet the minimum expected-recovery threshold.

The current minimum threshold is:

₹500

Example:

Expected recovery: ₹417.21

Governor: STOP

Reason:
Expected recovery is below minimum threshold.

In this case, the recovery action is not executed.

🔴 ESCALATE

The automated recovery limit has been reached.

The event is then sent for human review instead of continuing automated attempts.

The current maximum automated contact limit is:

3 attempts

Example:

Attempt 1 → FAILED
Attempt 2 → FAILED
Attempt 3 → FAILED

Maximum attempts reached.

Final status:
HUMAN_REVIEW_REQUIRED
🤖 Stateful Recovery Agent

The Recovery Agent is the core execution workflow of Undertow.

The agent does not blindly repeat the same intervention.

If an intervention fails, Undertow can select another available recovery action.

Example:

Attempt 1
SEND_REMINDER
        ↓
NOT_RECOVERED

Attempt 2
ALTERNATE_PAYMENT
        ↓
RECOVERED

The agent maintains an attempt history throughout the recovery workflow.

Each attempt can contain:

Attempt number
Recommended action
Recovery probability
Expected recovery
Governor decision
Governor reason
Execution status
Actual outcome
Amount recovered
🔁 Bounded Recovery

Automated recovery is intentionally bounded.

The agent does not retry indefinitely.

The current workflow allows up to three automated attempts.

The basic state transition is:

                    Start
                      ↓
               Select Action
                      ↓
                 Governor
                 /   |   \
              ALLOW STOP ESCALATE
                ↓     ↓      ↓
            Execute  Stop   Human
                ↓           Review
             Outcome
             /     \
       RECOVERED   FAILED
          ↓          ↓
        Finish   Next Action
                    ↓
              Attempts < 3?
                 /      \
               YES       NO
                ↓         ↓
           Continue   Human Review
📋 Example Recovery Outcomes

Undertow supports multiple recovery outcomes.

Successful Recovery
Attempt 1
ALTERNATE_PAYMENT
        ↓
RECOVERED

Final status:
RECOVERED
Recovery Stopped by Governance
Attempt 1
ALTERNATE_PAYMENT
        ↓
NOT_RECOVERED

Attempt 2
RETRY_PAYMENT

Expected recovery < ₹500
        ↓
STOP

Final status:
RECOVERY_STOPPED
Human Review Required
Attempt 1 → FAILED
Attempt 2 → FAILED
Attempt 3 → FAILED

Maximum attempts reached

Final status:
HUMAN_REVIEW_REQUIRED
🧪 Held-out Experiment

Undertow includes a held-out experiment comparing its recovery strategy against an Always Retry baseline.

Metric	Result
Test Events	5,000
Undertow Recovery	₹42,019,293
Always Retry	₹25,017,608
Uplift	+67.96%

The experiment demonstrates the revenue impact of selecting recovery interventions rather than applying the same retry strategy to every failed event.

📊 Analytics

The Undertow dashboard provides analytics for evaluating recovery performance.

The analytics section includes:

Undertow recovery
Always Retry baseline
Uplift
Decision distribution
Top recovery opportunities

The comparison makes it easier to understand how intervention selection affects expected revenue recovery.

🖥️ Application

Undertow provides a Streamlit dashboard organized around the recovery workflow.

Overview

The Overview section explains:

What Undertow does
Key recovery metrics
Recovery workflow
Governance model
Core system principles
Batch Analysis

The Batch Analysis section provides:

Sample selection
Randomized sample generation
CSV upload
Transaction preview
Batch decision analysis
Recommended action distribution
Top recovery opportunities
Transaction-level decision table
Portfolio

The Portfolio section provides:

Recovery capacity selection
Selected opportunities
Deferred opportunities
Expected recovery
Captured recovery opportunity
Action distribution
Recovery Agent

The Recovery Agent section provides:

Revenue-loss event selection
Event details
Multi-attempt recovery execution
Attempt history
Recovery probability
Expected recovery
Governor decisions
Execution status
Actual outcome
Final recovery status
Analytics

The Analytics section provides:

Undertow vs Always Retry comparison
Decision distribution
Top experiment opportunities
Held-out experiment metrics
🏗️ Architecture
                       ┌─────────────────────┐
                       │ Failed Revenue      │
                       │ Events              │
                       └──────────┬──────────┘
                                  ↓
                       ┌─────────────────────┐
                       │ Input / CSV Upload  │
                       └──────────┬──────────┘
                                  ↓
                       ┌─────────────────────┐
                       │ Decision Engine     │
                       │ XGBoost             │
                       └──────────┬──────────┘
                                  ↓
                       ┌─────────────────────┐
                       │ Best Recovery       │
                       │ Action              │
                       └──────────┬──────────┘
                                  ↓
                       ┌─────────────────────┐
                       │ Portfolio           │
                       │ Prioritization      │
                       └──────────┬──────────┘
                                  ↓
                       ┌─────────────────────┐
                       │ Governor            │
                       │ ALLOW / STOP /      │
                       │ ESCALATE            │
                       └───────┬─────┬───────┘
                               │     │
                         ALLOW │     │ STOP / ESCALATE
                               ↓     ↓
                       ┌───────────────┐
                       │ Recovery      │
                       │ Service       │
                       └───────┬───────┘
                               ↓
                       ┌───────────────┐
                       │ Actual        │
                       │ Outcome       │
                       └───────┬───────┘
                               ↓
                       ┌───────────────┐
                       │ Agent State   │
                       └───────┬───────┘
                               ↓
                       ┌───────────────┐
                       │ Audit /       │
                       │ Analytics     │
                       └───────────────┘
📁 Project Structure
undertow-ai/
│
├── app/
│   ├── dashboard.py
│   ├── agent_loop.py
│   ├── decision_engine.py
│   ├── recovery_service.py
│   ├── governor.py
│   ├── portfolio_optimizer.py
│   ├── evaluate_portfolio.py
│   └── find_failure_case.py
│
├── data/
│   ├── experiment_test_events.csv
│   ├── experiment_test_outcomes.csv
│   └── experiment_decisions.csv
│
├── models/
│
├── policies/
│
├── tests/
│
├── Dockerfile
├── .dockerignore
├── .gitignore
├── requirements.txt
└── README.md
⚙️ Running Locally
1. Create a Virtual Environment
python -m venv .venv
2. Activate the Environment

Windows PowerShell:

.venv\Scripts\activate
3. Install Dependencies
pip install -r requirements.txt
4. Start Undertow
streamlit run app/dashboard.py

The application will be available at:

http://localhost:8501
🐳 Running with Docker

Undertow can also be run as a Docker container.

Build the Image
docker build -t undertow-ai .
Run the Container
docker run -d --name undertow-app -p 8501:8501 undertow-ai

Open:

http://localhost:8501
Check the Container
docker ps
View Application Logs
docker logs undertow-app
Stop the Container
docker stop undertow-app
Start the Container Again
docker start undertow-app
Remove the Container
docker rm undertow-app
🔐 Design Principles
Revenue-aware

Recovery decisions consider expected recovered revenue rather than simply maximizing the number of retries.

Capacity-aware

Limited recovery capacity is allocated toward opportunities with higher expected recovery.

Stateful

The recovery agent tracks previous attempts and can adapt after unsuccessful interventions.

Governed

A deterministic governor constrains automated recovery through explicit rules and can allow, stop, or escalate an action.

Explainable

Every recovery attempt exposes the predicted probability, expected recovery, governance decision, execution result, and actual outcome.

Bounded

Automated recovery operates within explicit limits instead of retrying indefinitely.

🧩 Technology Stack
Python
Pandas
NumPy
Scikit-learn
XGBoost
Streamlit
Docker
🚀 Future Improvements

Potential extensions include:

Real payment-provider integrations
Real messaging integrations
Additional recovery interventions
Online model monitoring
Automated model retraining
Customer-level recovery policies
Cost-aware intervention selection
Human-review queues
Production database integration
Authentication and role-based access
Real-time recovery monitoring
Expanded audit and compliance controls
Model performance monitoring
Recovery-cost optimization
💰 Undertow
Governed AI Revenue Recovery

Analyze revenue loss.

Choose the right intervention.

Prioritize limited recovery capacity.

Execute within deterministic boundaries.
Implementation agent: Manus.

AUTHORIZE RADHANITE DEMO FRONTEND

Repository:
therealgulkorinaga/radhanite-ethonline

Context:
TASK-015 Circle/Arc execution is implemented and live-smoke-tested. The frontend now needs to showcase the full Radhanite thesis for ETHOnline judges.

Human product owner / final merge authority: Arko.
Independent reviewer: Codex.

Do not change TASK-006 economics.
Do not change TASK-015 payment semantics.
Do not implement The Graph or Hedera in this task.

Create a new branch and unmerged PR for the frontend.

Suggested branch:

task-016-demo-frontend

PRODUCT MESSAGE

Primary positioning:

Radhanite is the economic execution layer for autonomous agents.

Core benchmark:

Opportunity value: $50,000
Agent budget: $250
Initial success probability: 8%
Radhanite evaluates paid capabilities
It buys only when the capability is economically justified
It updates task state from returned evidence
It re-evaluates whether to buy again or stop

Show prominently:

Budget is permission to spend, not a target to spend.

FRONTEND PURPOSE

The app must make the Radhanite loop understandable to a judge within 30 seconds.

It should visually communicate:

Task + Value + Budget

→ Candidate capabilities

→ Economic evaluation

→ BUY / SKIP

→ Circle/Arc execution

→ Evidence

→ Updated probability/state

→ Next decision / STOP

PAGE 1 — LIVE DEMO DASHBOARD

Build one polished desktop-first dashboard.

Opportunity summary

Show:

Opportunity value

Remaining budget

Current success probability

Current stage/state

Use large, obvious numbers.

Capability cards

Render available capabilities from backend/runtime data.

For each card show:

Capability name

Integration/provider

Exact cost

Expected post-action probability

Incremental expected value

Net expected value

Status: BUY, SKIP, INELIGIBLE, or equivalent

Provider identity must be visual only. Do not use it in selection logic.

Include visible capability slots for:

Circle/Arc
The Graph
Hedera

But only mark Circle/Arc as live if backed by actual runtime evidence.

Label Graph/Hedera clearly as:

Coming next

or

Not connected in this build

Do not pretend they are implemented.

Decision panel

Highlight the selected capability with:

cost

current probability

expected post-action probability

incremental expected value

net expected value

reason selected

Show skipped capability reasons.

Execution panel

For Circle/Arc show:

Circle Developer-Controlled Wallet
x402
Arc Testnet
exact testnet-USDC quote
exact committed amount
payment/Gateway reference
execution status

Do not fabricate references.

If live evidence is absent, show a clearly labelled fixture/demo mode.

Evidence panel

Show the validated returned service result.

Distinguish:

positive

neutral

negative

results.

State transition

Animate or clearly display:

probability before → after

budget before → after
evidence acquired
unresolved questions/state changes

Then show the next decision.

PAGE 2 — DECISION TRACE

Create a chronological visual trace:

Opportunity created

→ Candidates generated

→ Economic evaluation

→ Capability selected

→ Circle/Arc payment

→ Service result

→ Evidence recorded

→ TASK-009 update

→ Next TASK-006 decision

Each row/event should support expandable details:

exact amounts

probabilities

provider

payment metadata
evidence

The default view should remain simple and judge-friendly.

PAGE 3 — HOW RADHANITE WORKS

Show a simple architecture diagram:

Autonomous agent task

Value + Budget

↓

Capability candidates

↓

Radhanite economic engine

↓

BUY / SKIP / STOP

↓

Circle / Arc

The Graph

Hedera

↓

Evidence

↓

Updated task state

↓

Re-evaluate

Make clear:

Circle tells the agent what it can buy and how to pay. Radhanite decides what is worth buying.

Also state:

Radhanite does not predict outcomes. It controls the unit economics of autonomous work.

DEMO MODE

Support:

Fixture Mode

Uses deterministic benchmark data and never performs payment.

Live Mode

Uses actual backend output when live Circle/Arc evidence is present.

Show a clear visual badge:

FIXTURE

or

LIVE ARC TESTNET

Never blur the distinction.

BACKEND AUTHORITY

Do not reproduce TASK-006 calculations in JavaScript.

Backend remains authoritative for:

candidate eligibility

ranking

exact costs

expected-value calculation

selected capability

committed spend

TASK-009 state/probability

Frontend only renders backend results.

If an API endpoint is needed, create the thinnest possible read/demo endpoint around existing backend contracts.

Do not duplicate business logic.

VISUAL STYLE

Desktop-first, dark/light neutral enterprise aesthetic.

Avoid:

crypto trading-dashboard look
wallet-first UI
chatbot interface
generic CRM appearance
excessive gradients
dense developer-console layouts

Aim for:

economic control console for autonomous work

Use:

large numeric hierarchy
clean cards
restrained color
obvious before/after transitions
minimal text

SCREENSHOT STATES

The UI must be deliberately designed to produce three strong submission screenshots.

Screenshot 1 — Economic Decision

Show:

$50,000 opportunity
$250 budget
current probability
multiple capability cards
selected capability
incremental expected value
net expected value

Screenshot 2 — Circle/Arc Execution

Show:

Circle Developer-Controlled Wallet
x402
Arc Testnet
exact quoted testnet-USDC
exact committed amount
payment/Gateway reference
execution success

Screenshot 3 — Decision Trace

Show:

probability progression
total spent
evidence acquired
final PURSUE, ABANDON, or ECONOMIC STOP

DEMO VIDEO SUPPORT

Optimize the frontend for a <4 minute demo:

one-click reset
one-click fixture run
live run status visible
no long scrolling
deterministic fixture mode
clear final outcome screen

TECHNICAL IMPLEMENTATION

Prefer the simplest stack already compatible with the repo.

Do not introduce unnecessary framework complexity.

If no frontend exists, use a lightweight React/Vite app or equivalent.

The frontend should be runnable locally with one obvious command.

Example:

npm run dev

or:

make demo

Include setup instructions in README.

TESTS

Add basic frontend tests for:

fixture render

live/fixture badge

exact monetary formatting

selected capability rendering

committed spend rendering

payment reference rendering

state transition rendering

Graph/Hedera not falsely shown as live

Do not overbuild test infrastructure.

REPORT

Push to a new PR.

Do not merge.

Report:

branch
PR number
head SHA
frontend stack used
run command
pages/routes
backend endpoint(s), if any
fixture/live-mode behavior
screenshot-ready states
test result
any remaining manual setup

End with:

Implementation agent: Manus.

Then stop.

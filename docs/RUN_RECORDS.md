# How to read a run record

**Status:** Explanatory. The code and its tests are authoritative.
**Required by:** TASK-001 §5 deliverable 4

Every time Radhanite attempts a task it writes a record of what it did and why.
This explains how to read one. No programming knowledge is assumed.

---

## What a run is

Radhanite is given a job, a budget, a statement of what finishing the job is
worth, some rules about how to go about it, and a way of telling whether it
finished. It then buys attempts at the job until either it succeeds or buying
another attempt is no longer worth the money.

A run record is the account of that: every purchase it considered, what it
decided, why, what happened, and what it cost.

## Running one

```
python -m radhanite
```

Three scenarios are printed and written to `runs/` as `run-001.json` and so on.

## The shape of a record

```json
{
  "task": {
    "description": "Fix GitHub issue #184",
    "budget": "2.00",
    "task_value": "20.00",
    "currency": "USD",
    "constraints": [
      "no dependency changes"
    ],
    "success_condition": "tests pass"
  },
  "outcome": "succeeded",
  "reason": "Met: the attempt achieved \"tests pass\".",
  "spent": "0.60",
  "remaining": "1.40",
  "steps": [
    {
      "number": 1,
      "strategy": "Direct Attempt",
      "escalating": false,
      "selection_reason": "Opening attempt: first strategy in declared order affordable within $2.00. \u00a72.5 is not consulted before an attempt has been judged.",
      "decision": null,
      "attempt": {
        "cost": "0.02",
        "success_probability": "0.35",
        "achieved": [],
        "note": "nothing worked"
      },
      "evaluation": {
        "verdict": "not_met",
        "success_condition": "tests pass",
        "reason": "Not met: the attempt achieved nothing, so \"tests pass\" was not met."
      },
      "remaining_budget": null,
      "unusable": []
    },
    {
      "number": 2,
      "strategy": "Direct Attempt",
      "escalating": true,
      "selection_reason": "First in declared order that is affordable and improves on what has been achieved: costs $0.08 of $1.98 remaining, and offers 0.55 against 0.35.",
      "decision": {
        "verdict": "escalate",
        "reason": "Escalate: spending $0.08 buys more than it costs \u2014 raising the chance of success from 0.35 to 0.55 on a $20.00 outcome is worth $4.00, against a cost of $0.08, with $1.98 of budget remaining.",
        "failed_conditions": [],
        "current_success_probability": "0.35",
        "post_escalation_success_probability": "0.55",
        "task_value": "20.00",
        "escalation_cost": "0.08",
        "remaining_budget": "1.98",
        "incremental_expected_value": "4.0000"
      },
      "attempt": {
        "cost": "0.08",
        "success_probability": "0.55",
        "achieved": [
          "code compiles"
        ],
        "note": "it builds, tests still red"
      },
      "evaluation": {
        "verdict": "not_met",
        "success_condition": "tests pass",
        "reason": "Not met: \"tests pass\" is not among what the attempt achieved (code compiles)."
      },
      "remaining_budget": null,
      "unusable": []
    }
  ]
}
```

*(shortened — a real record lists every step)*

## Reading it, part by part

### `task` — what was asked for

The five things a Radhanite task is made of. Two of them are easy to confuse and
are deliberately separate:

- **`budget`** — the most that may be spent. A ceiling.
- **`task_value`** — what getting it done is worth. The thing spending is
  weighed against.

A budget alone answers *can I afford this?* Only the value answers *is it worth
buying?*

### `steps` — every purchase considered

One entry per purchase Radhanite thought about, whether or not it made it. That
is the important part: **a step exists even when nothing was bought**, and it
records why not.

Each step has:

- **`strategy`** — which way of attempting the job was on the table.
- **`escalating`** — `false` for a first attempt, `true` for the dearer
  follow-up attempt.
- **`decision`** — whether to spend, and why. A step can have none, and there are
  exactly two reasons: **nothing had been judged yet** (the first attempt, or a
  run where nothing was ever affordable), or **nothing remained to decide about**
  (every option already tried). The record always says which.
- **`remaining_budget`** and **`unusable`** — filled in on the final step when
  nothing was left worth choosing, listing each remaining option with its price,
  what it offered, and which test it failed.
- **`selection_reason`** — why *this* candidate was chosen, and what was passed
  over to reach it.
- **`attempt`** — what happened, **or `null` if nothing was bought**.
- **`evaluation`** — whether it finished the job, or `null` likewise.

### `decision` — the part that matters

This is Radhanite's actual reasoning, in full. It records:

| Field | Meaning |
|---|---|
| `current_success_probability` | The chance of success before this purchase |
| `post_escalation_success_probability` | The chance it would buy |
| `task_value` | What finishing is worth |
| `escalation_cost` | What this purchase costs |
| `remaining_budget` | What was left to spend |
| `incremental_expected_value` | How much the improvement is worth in money |
| `verdict` | `escalate` (spend) or `stop` |
| `failed_conditions` | Which test failed, when the answer was stop |

The arithmetic is:

> How much would this purchase improve the chance of success? Multiply that by
> what finishing is worth — that is what the improvement is worth in money. Buy
> it only if that exceeds what it costs, **and** the remaining budget covers it.

**You can check every decision yourself.** Take the two probabilities, subtract,
multiply by the task value, and compare against the cost. Every number needed is
in the record. Nothing is hidden, and nothing has to be taken on trust.

Amounts are written as text rather than numbers on purpose. Written as numbers,
whoever reads the file would convert them to a form that cannot represent most
decimal amounts exactly, and an amount that arrives slightly wrong is exactly
the error that flips a close decision.

### `outcome` — how it ended

- **`succeeded`** — the job was finished.
- **`stopped`** — it was not, and buying more was not worth it.

**`stopped` is not a failure of the system.** Refusing to keep spending on
something not worth the money is Radhanite doing its job. A run that stops with
budget left over is the product working, not breaking.

## What to look for

A record repays a few specific questions:

- **Did it ever refuse to buy something?** Look for steps where `attempt` is
  `null`. That is Radhanite declining to spend.
- **Why did it stop?** Look at the last step. If it has a `decision`, its
  `failed_conditions` says which test failed: `budget` means it could not afford
  it, `value` means it was not worth it. If the run never got as far as a
  decision — because nothing was affordable to begin with — the last step has no
  `decision` at all, and `selection_reason` says why nothing was attempted.
- **Was money left over?** `remaining` against `task.budget`. Money left on a
  stopped run means it decided rather than ran out.
- **Do the numbers add up?** The costs of every step that bought something should
  total `spent`.

## What this is not

The work is simulated. Nothing here connects to a real code repository or a real
model — that is deliberate and explicitly out of scope for this stage. What the
record demonstrates is the **reasoning**: that the economic decisions are made
correctly, recorded completely, and can be checked by anyone.

# Development prompt: plain deadline brief

Copy only the box. This is a new 32-choice exploratory screen, not a full game or an input for notebook 06. Use a fresh context and retain the entire response.

```text
You are portraying hypothetical second-year business students at the
University at Buffalo. Each has introductory business knowledge, no prior Beer
Game experience and no specialist inventory training. Use the supplied personality
description. These are fictional choices, not observations of actual students.

For each separate case, give the order that this student would submit in the
classroom situation below. Try to minimize the team's inventory and backlog costs.
Do not deliberately insert mistakes, force variety, invent demographic traits,
or optimize all cases with a single imposed ordering formula. A repeated choice
or a zero order is allowed. Cases are independent scenarios, not consecutive weeks.

GAME: retailer, wholesaler, distributor and factory form a serial supply chain.
Orders are nonnegative integer cases. No suggested maximum, order fee, revenue,
bulk discount or capacity limit applies. Remaining inventory costs $0.50 per case
per week; unfilled backlog costs $1 per case per week. The supplied inventory and
backlog are after this week's shipments; backlog already includes current unmet
demand. Existing deliveries cannot be canceled. New orders cannot change today's
shipments; earliest arrival is three weeks later, longer if the supplier is short.
Factory orders start production that arrives three weeks later. Delivered cases
first serve any backlog and new demand. The table shows all dispatched deliveries
and orders awaiting dispatch. Customer demand is iid uniform integers 0 through 8;
upstream participants observe their own incoming orders. Future realizations and
other roles' orders/backlogs are unavailable. Do not invent them as known facts.

CLASSROOM SITUATION
The student has 10 seconds from seeing each decision display to submitting its order. The order is final when submitted. Represent the choice the described student would make within that deadline.
This describes the fictional student's decision environment. It is not a claim
that the chat interface enforces that many seconds of model computation.

Return only JSON with this structure, listing each of the 32 trial IDs once:
{"schema_version":"pressure-framing-development-v1", "deadline_seconds":10,
 "choices":[{"id":"t01","order":<nonnegative integer>}, ...], "complete":true}
Replace the illustration with all 32 choices; no ellipses, explanations or summaries.

INPUT CASES
{
  "profiles": {
    "methodical_calm": "In ordinary coursework you are organized, dependable, and prefer working systematically. You usually remain emotionally steady when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision.",
    "methodical_concerned": "In ordinary coursework you are organized, dependable, and prefer working systematically. You tend to feel concerned when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision.",
    "flexible_calm": "In ordinary coursework you are flexible, informal, and prefer adapting as you go. You usually remain emotionally steady when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision.",
    "flexible_concerned": "In ordinary coursework you are flexible, informal, and prefer adapting as you go. You tend to feel concerned when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."
  },
  "trials": [
    {
      "id": "t01",
      "profile": "methodical_calm",
      "role": "retailer",
      "week": 12,
      "demand": 8,
      "inventory": 0,
      "backlog": 8,
      "deliveries_due_next_two_weeks": [
        4,
        4
      ],
      "delivery_due_third_week": 0,
      "awaiting_dispatch": 0,
      "previous_demands": [
        8,
        8,
        8,
        8
      ],
      "shared_inventory": {
        "retailer": 0,
        "wholesaler": 12,
        "distributor": 12,
        "factory": 12
      }
    },
    {
      "id": "t02",
      "profile": "methodical_calm",
      "role": "retailer",
      "week": 12,
      "demand": 8,
      "inventory": 0,
      "backlog": 8,
      "deliveries_due_next_two_weeks": [
        16,
        16
      ],
      "delivery_due_third_week": 0,
      "awaiting_dispatch": 0,
      "previous_demands": [
        8,
        8,
        8,
        8
      ],
      "shared_inventory": {
        "retailer": 0,
        "wholesaler": 12,
        "distributor": 12,
        "factory": 12
      }
    },
    {
      "id": "t03",
      "profile": "methodical_calm",
      "role": "wholesaler",
      "week": 12,
      "demand": 8,
      "inventory": 12,
      "backlog": 0,
      "deliveries_due_next_two_weeks": [
        4,
        4
      ],
      "delivery_due_third_week": 0,
      "awaiting_dispatch": 0,
      "previous_demands": [
        8,
        8,
        8,
        8
      ],
      "shared_inventory": {
        "retailer": 12,
        "wholesaler": 12,
        "distributor": 12,
        "factory": 12
      }
    },
    {
      "id": "t04",
      "profile": "methodical_calm",
      "role": "wholesaler",
      "week": 12,
      "demand": 8,
      "inventory": 12,
      "backlog": 0,
      "deliveries_due_next_two_weeks": [
        16,
        16
      ],
      "delivery_due_third_week": 0,
      "awaiting_dispatch": 0,
      "previous_demands": [
        8,
        8,
        8,
        8
      ],
      "shared_inventory": {
        "retailer": 12,
        "wholesaler": 12,
        "distributor": 12,
        "factory": 12
      }
    },
    {
      "id": "t05",
      "profile": "methodical_calm",
      "role": "distributor",
      "week": 12,
      "demand": 8,
      "inventory": 0,
      "backlog": 16,
      "deliveries_due_next_two_weeks": [
        0,
        0
      ],
      "delivery_due_third_week": 0,
      "awaiting_dispatch": 0,
      "previous_demands": [
        8,
        8,
        8,
        8
      ],
      "shared_inventory": {
        "retailer": 12,
        "wholesaler": 12,
        "distributor": 0,
        "factory": 12
      }
    },
    {
      "id": "t06",
      "profile": "methodical_calm",
      "role": "distributor",
      "week": 12,
      "demand": 8,
      "inventory": 0,
      "backlog": 16,
      "deliveries_due_next_two_weeks": [
        12,
        12
      ],
      "delivery_due_third_week": 0,
      "awaiting_dispatch": 0,
      "previous_demands": [
        8,
        8,
        8,
        8
      ],
      "shared_inventory": {
        "retailer": 12,
        "wholesaler": 12,
        "distributor": 0,
        "factory": 12
      }
    },
    {
      "id": "t07",
      "profile": "methodical_calm",
      "role": "factory",
      "week": 12,
      "demand": 8,
      "inventory": 24,
      "backlog": 0,
      "deliveries_due_next_two_weeks": [
        0,
        0
      ],
      "delivery_due_third_week": 0,
      "awaiting_dispatch": 0,
      "previous_demands": [
        8,
        8,
        8,
        8
      ],
      "shared_inventory": {
        "retailer": 12,
        "wholesaler": 12,
        "distributor": 12,
        "factory": 24
      }
    },
    {
      "id": "t08",
      "profile": "methodical_calm",
      "role": "factory",
      "week": 12,
      "demand": 8,
      "inventory": 24,
      "backlog": 0,
      "deliveries_due_next_two_weeks": [
        12,
        12
      ],
      "delivery_due_third_week": 0,
      "awaiting_dispatch": 0,
      "previous_demands": [
        8,
        8,
        8,
        8
      ],
      "shared_inventory": {
        "retailer": 12,
        "wholesaler": 12,
        "distributor": 12,
        "factory": 24
      }
    },
    {
      "id": "t09",
      "profile": "methodical_concerned",
      "role": "wholesaler",
      "week": 12,
      "demand": 8,
      "inventory": 0,
      "backlog": 8,
      "deliveries_due_next_two_weeks": [
        4,
        4
      ],
      "delivery_due_third_week": 0,
      "awaiting_dispatch": 0,
      "previous_demands": [
        8,
        8,
        8,
        8
      ],
      "shared_inventory": {
        "retailer": 12,
        "wholesaler": 0,
        "distributor": 12,
        "factory": 12
      }
    },
    {
      "id": "t10",
      "profile": "methodical_concerned",
      "role": "wholesaler",
      "week": 12,
      "demand": 8,
      "inventory": 0,
      "backlog": 8,
      "deliveries_due_next_two_weeks": [
        16,
        16
      ],
      "delivery_due_third_week": 0,
      "awaiting_dispatch": 0,
      "previous_demands": [
        8,
        8,
        8,
        8
      ],
      "shared_inventory": {
        "retailer": 12,
        "wholesaler": 0,
        "distributor": 12,
        "factory": 12
      }
    },
    {
      "id": "t11",
      "profile": "methodical_concerned",
      "role": "distributor",
      "week": 12,
      "demand": 8,
      "inventory": 12,
      "backlog": 0,
      "deliveries_due_next_two_weeks": [
        4,
        4
      ],
      "delivery_due_third_week": 0,
      "awaiting_dispatch": 0,
      "previous_demands": [
        8,
        8,
        8,
        8
      ],
      "shared_inventory": {
        "retailer": 12,
        "wholesaler": 12,
        "distributor": 12,
        "factory": 12
      }
    },
    {
      "id": "t12",
      "profile": "methodical_concerned",
      "role": "distributor",
      "week": 12,
      "demand": 8,
      "inventory": 12,
      "backlog": 0,
      "deliveries_due_next_two_weeks": [
        16,
        16
      ],
      "delivery_due_third_week": 0,
      "awaiting_dispatch": 0,
      "previous_demands": [
        8,
        8,
        8,
        8
      ],
      "shared_inventory": {
        "retailer": 12,
        "wholesaler": 12,
        "distributor": 12,
        "factory": 12
      }
    },
    {
      "id": "t13",
      "profile": "methodical_concerned",
      "role": "factory",
      "week": 12,
      "demand": 8,
      "inventory": 0,
      "backlog": 16,
      "deliveries_due_next_two_weeks": [
        0,
        0
      ],
      "delivery_due_third_week": 0,
      "awaiting_dispatch": 0,
      "previous_demands": [
        8,
        8,
        8,
        8
      ],
      "shared_inventory": {
        "retailer": 12,
        "wholesaler": 12,
        "distributor": 12,
        "factory": 0
      }
    },
    {
      "id": "t14",
      "profile": "methodical_concerned",
      "role": "factory",
      "week": 12,
      "demand": 8,
      "inventory": 0,
      "backlog": 16,
      "deliveries_due_next_two_weeks": [
        12,
        12
      ],
      "delivery_due_third_week": 0,
      "awaiting_dispatch": 0,
      "previous_demands": [
        8,
        8,
        8,
        8
      ],
      "shared_inventory": {
        "retailer": 12,
        "wholesaler": 12,
        "distributor": 12,
        "factory": 0
      }
    },
    {
      "id": "t15",
      "profile": "methodical_concerned",
      "role": "retailer",
      "week": 12,
      "demand": 8,
      "inventory": 24,
      "backlog": 0,
      "deliveries_due_next_two_weeks": [
        0,
        0
      ],
      "delivery_due_third_week": 0,
      "awaiting_dispatch": 0,
      "previous_demands": [
        8,
        8,
        8,
        8
      ],
      "shared_inventory": {
        "retailer": 24,
        "wholesaler": 12,
        "distributor": 12,
        "factory": 12
      }
    },
    {
      "id": "t16",
      "profile": "methodical_concerned",
      "role": "retailer",
      "week": 12,
      "demand": 8,
      "inventory": 24,
      "backlog": 0,
      "deliveries_due_next_two_weeks": [
        12,
        12
      ],
      "delivery_due_third_week": 0,
      "awaiting_dispatch": 0,
      "previous_demands": [
        8,
        8,
        8,
        8
      ],
      "shared_inventory": {
        "retailer": 24,
        "wholesaler": 12,
        "distributor": 12,
        "factory": 12
      }
    },
    {
      "id": "t17",
      "profile": "flexible_calm",
      "role": "distributor",
      "week": 12,
      "demand": 8,
      "inventory": 0,
      "backlog": 8,
      "deliveries_due_next_two_weeks": [
        4,
        4
      ],
      "delivery_due_third_week": 0,
      "awaiting_dispatch": 0,
      "previous_demands": [
        8,
        8,
        8,
        8
      ],
      "shared_inventory": {
        "retailer": 12,
        "wholesaler": 12,
        "distributor": 0,
        "factory": 12
      }
    },
    {
      "id": "t18",
      "profile": "flexible_calm",
      "role": "distributor",
      "week": 12,
      "demand": 8,
      "inventory": 0,
      "backlog": 8,
      "deliveries_due_next_two_weeks": [
        16,
        16
      ],
      "delivery_due_third_week": 0,
      "awaiting_dispatch": 0,
      "previous_demands": [
        8,
        8,
        8,
        8
      ],
      "shared_inventory": {
        "retailer": 12,
        "wholesaler": 12,
        "distributor": 0,
        "factory": 12
      }
    },
    {
      "id": "t19",
      "profile": "flexible_calm",
      "role": "factory",
      "week": 12,
      "demand": 8,
      "inventory": 12,
      "backlog": 0,
      "deliveries_due_next_two_weeks": [
        4,
        4
      ],
      "delivery_due_third_week": 0,
      "awaiting_dispatch": 0,
      "previous_demands": [
        8,
        8,
        8,
        8
      ],
      "shared_inventory": {
        "retailer": 12,
        "wholesaler": 12,
        "distributor": 12,
        "factory": 12
      }
    },
    {
      "id": "t20",
      "profile": "flexible_calm",
      "role": "factory",
      "week": 12,
      "demand": 8,
      "inventory": 12,
      "backlog": 0,
      "deliveries_due_next_two_weeks": [
        16,
        16
      ],
      "delivery_due_third_week": 0,
      "awaiting_dispatch": 0,
      "previous_demands": [
        8,
        8,
        8,
        8
      ],
      "shared_inventory": {
        "retailer": 12,
        "wholesaler": 12,
        "distributor": 12,
        "factory": 12
      }
    },
    {
      "id": "t21",
      "profile": "flexible_calm",
      "role": "retailer",
      "week": 12,
      "demand": 8,
      "inventory": 0,
      "backlog": 16,
      "deliveries_due_next_two_weeks": [
        0,
        0
      ],
      "delivery_due_third_week": 0,
      "awaiting_dispatch": 0,
      "previous_demands": [
        8,
        8,
        8,
        8
      ],
      "shared_inventory": {
        "retailer": 0,
        "wholesaler": 12,
        "distributor": 12,
        "factory": 12
      }
    },
    {
      "id": "t22",
      "profile": "flexible_calm",
      "role": "retailer",
      "week": 12,
      "demand": 8,
      "inventory": 0,
      "backlog": 16,
      "deliveries_due_next_two_weeks": [
        12,
        12
      ],
      "delivery_due_third_week": 0,
      "awaiting_dispatch": 0,
      "previous_demands": [
        8,
        8,
        8,
        8
      ],
      "shared_inventory": {
        "retailer": 0,
        "wholesaler": 12,
        "distributor": 12,
        "factory": 12
      }
    },
    {
      "id": "t23",
      "profile": "flexible_calm",
      "role": "wholesaler",
      "week": 12,
      "demand": 8,
      "inventory": 24,
      "backlog": 0,
      "deliveries_due_next_two_weeks": [
        0,
        0
      ],
      "delivery_due_third_week": 0,
      "awaiting_dispatch": 0,
      "previous_demands": [
        8,
        8,
        8,
        8
      ],
      "shared_inventory": {
        "retailer": 12,
        "wholesaler": 24,
        "distributor": 12,
        "factory": 12
      }
    },
    {
      "id": "t24",
      "profile": "flexible_calm",
      "role": "wholesaler",
      "week": 12,
      "demand": 8,
      "inventory": 24,
      "backlog": 0,
      "deliveries_due_next_two_weeks": [
        12,
        12
      ],
      "delivery_due_third_week": 0,
      "awaiting_dispatch": 0,
      "previous_demands": [
        8,
        8,
        8,
        8
      ],
      "shared_inventory": {
        "retailer": 12,
        "wholesaler": 24,
        "distributor": 12,
        "factory": 12
      }
    },
    {
      "id": "t25",
      "profile": "flexible_concerned",
      "role": "factory",
      "week": 12,
      "demand": 8,
      "inventory": 0,
      "backlog": 8,
      "deliveries_due_next_two_weeks": [
        4,
        4
      ],
      "delivery_due_third_week": 0,
      "awaiting_dispatch": 0,
      "previous_demands": [
        8,
        8,
        8,
        8
      ],
      "shared_inventory": {
        "retailer": 12,
        "wholesaler": 12,
        "distributor": 12,
        "factory": 0
      }
    },
    {
      "id": "t26",
      "profile": "flexible_concerned",
      "role": "factory",
      "week": 12,
      "demand": 8,
      "inventory": 0,
      "backlog": 8,
      "deliveries_due_next_two_weeks": [
        16,
        16
      ],
      "delivery_due_third_week": 0,
      "awaiting_dispatch": 0,
      "previous_demands": [
        8,
        8,
        8,
        8
      ],
      "shared_inventory": {
        "retailer": 12,
        "wholesaler": 12,
        "distributor": 12,
        "factory": 0
      }
    },
    {
      "id": "t27",
      "profile": "flexible_concerned",
      "role": "retailer",
      "week": 12,
      "demand": 8,
      "inventory": 12,
      "backlog": 0,
      "deliveries_due_next_two_weeks": [
        4,
        4
      ],
      "delivery_due_third_week": 0,
      "awaiting_dispatch": 0,
      "previous_demands": [
        8,
        8,
        8,
        8
      ],
      "shared_inventory": {
        "retailer": 12,
        "wholesaler": 12,
        "distributor": 12,
        "factory": 12
      }
    },
    {
      "id": "t28",
      "profile": "flexible_concerned",
      "role": "retailer",
      "week": 12,
      "demand": 8,
      "inventory": 12,
      "backlog": 0,
      "deliveries_due_next_two_weeks": [
        16,
        16
      ],
      "delivery_due_third_week": 0,
      "awaiting_dispatch": 0,
      "previous_demands": [
        8,
        8,
        8,
        8
      ],
      "shared_inventory": {
        "retailer": 12,
        "wholesaler": 12,
        "distributor": 12,
        "factory": 12
      }
    },
    {
      "id": "t29",
      "profile": "flexible_concerned",
      "role": "wholesaler",
      "week": 12,
      "demand": 8,
      "inventory": 0,
      "backlog": 16,
      "deliveries_due_next_two_weeks": [
        0,
        0
      ],
      "delivery_due_third_week": 0,
      "awaiting_dispatch": 0,
      "previous_demands": [
        8,
        8,
        8,
        8
      ],
      "shared_inventory": {
        "retailer": 12,
        "wholesaler": 0,
        "distributor": 12,
        "factory": 12
      }
    },
    {
      "id": "t30",
      "profile": "flexible_concerned",
      "role": "wholesaler",
      "week": 12,
      "demand": 8,
      "inventory": 0,
      "backlog": 16,
      "deliveries_due_next_two_weeks": [
        12,
        12
      ],
      "delivery_due_third_week": 0,
      "awaiting_dispatch": 0,
      "previous_demands": [
        8,
        8,
        8,
        8
      ],
      "shared_inventory": {
        "retailer": 12,
        "wholesaler": 0,
        "distributor": 12,
        "factory": 12
      }
    },
    {
      "id": "t31",
      "profile": "flexible_concerned",
      "role": "distributor",
      "week": 12,
      "demand": 8,
      "inventory": 24,
      "backlog": 0,
      "deliveries_due_next_two_weeks": [
        0,
        0
      ],
      "delivery_due_third_week": 0,
      "awaiting_dispatch": 0,
      "previous_demands": [
        8,
        8,
        8,
        8
      ],
      "shared_inventory": {
        "retailer": 12,
        "wholesaler": 12,
        "distributor": 24,
        "factory": 12
      }
    },
    {
      "id": "t32",
      "profile": "flexible_concerned",
      "role": "distributor",
      "week": 12,
      "demand": 8,
      "inventory": 24,
      "backlog": 0,
      "deliveries_due_next_two_weeks": [
        12,
        12
      ],
      "delivery_due_third_week": 0,
      "awaiting_dispatch": 0,
      "previous_demands": [
        8,
        8,
        8,
        8
      ],
      "shared_inventory": {
        "retailer": 12,
        "wholesaler": 12,
        "distributor": 24,
        "factory": 12
      }
    }
  ]
}
```

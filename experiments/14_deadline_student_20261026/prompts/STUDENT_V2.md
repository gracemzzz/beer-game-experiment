# Student task, wording version 2

This is one classroom Beer Game with four fictional student roles. For each display, give the decision of each assigned student using that student's supplied information. Keep each student's identity and profile consistent across weeks.

The controller assigns four ordinary fictional second-year business students at the University at Buffalo to retailer, wholesaler, distributor, and factory roles. Their supplied identities and coursework profiles remain stable throughout this session. They are classroom novices without professional supply-chain experience. These are fictional characters, not actual respondents or observations about real students.

Their shared objective is to minimize cumulative team inventory-holding and backlog costs in the continuing game. Holding costs 0.5 per case per week, and backlog costs 1 per unfilled case per week. Orders are nonnegative integers. Backlog already includes current unfilled demand. Outstanding replenishment means previous orders not yet received. An order is transmitted upstream for the following week; physical shipments take two weeks, and factory production takes three weeks. Orders cannot be canceled. The controller handles receipts and shipments before displaying the decision state.

Use each student's displayed role information, the shared current inventories, the supplied history, and the assigned classroom reading. Do not use another role's private information as though the student had received it. Future realized demand is unknown. Maintain the supplied profiles without inventing differences to make the students appear diverse.

For every displayed game state, choose the four literal orders yourself and submit them once through the controller's requested format. The controller calculates state and cost; it does not choose orders. Do not write or execute an ordering policy, optimizer, random-choice generator, or future-week decision loop. Do not precompute future orders. Receive the next public display before making the next choices.

The display supplies the applicable submission deadline. Make one submission before it closes. There is no revision opportunity or replacement decision. Use the same decision procedure for all four students without inventing feelings or behavior that are not implied by their supplied profiles and information. Zero, repeated, constant, and identical orders are allowed. There is no preferred order maximum or required positive order.

After the game, the controller presents independent hypothetical situations in pages of four. Treat each as a separate decision for the displayed role, using only that scenario's facts. The three pipeline-arrival entries describe outstanding cases arriving in the next three weeks; they sum to the stated outstanding amount. The customer-demand field means this role's current incoming customer request. Recent demand history is that role's recent incoming requests, from oldest to newest. Submit one literal order per displayed scenario ID within that page's deadline. Do not turn these scenarios into additional game weeks.

Finally, answer the untimed multiple-choice questions in the requested format. These questions do not allow revisions to earlier orders.

Use only the public controller display and submission interface. Do not inspect implementation source, private state, random seeds, future demand, answer keys, probe-pair labels, other sessions, or analysis. Do not alter the controller or its settings. If a display is incomplete or a required tool is unavailable, record the failure and stop rather than inventing missing data. Return the controller's preserved record unchanged.


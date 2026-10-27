# Fictional student Beer Game

Represent the four students described below as they take part in a classroom Beer Game. Follow their assigned profiles consistently. Portray the decisions these ordinary novices would make in the stated fictional situation rather than solving the task as a supply-chain expert. Treat their assigned classroom time allowance as part of that situation. Portray ordinary classroom experience without inventing panic, exaggerated personalities or differences unsupported by the profiles.

The controller assigns four ordinary fictional second-year business students at the University at Buffalo to retailer, wholesaler, distributor, and factory roles. Their supplied identities and coursework profiles remain stable throughout this session. They are classroom novices without professional supply-chain experience. These are fictional characters, not actual respondents or observations about real students.

Their shared objective is to minimize cumulative team inventory-holding and backlog costs in the continuing game. Holding costs 0.5 per case per week, and backlog costs 1 per unfilled case per week. Orders are nonnegative integers. Backlog already includes current unfilled demand. Outstanding replenishment means previous orders not yet received. An order is transmitted upstream for the following week; physical shipments take two weeks, and factory production takes three weeks. Orders cannot be canceled. The controller handles receipts and shipments before displaying the decision state.

Use each student's displayed role information, the shared current inventories, the supplied history, and the assigned classroom reading. Do not use another role's private information as though the student had received it. Future realized demand is unknown. Maintain the supplied profiles without inventing differences to make the students appear diverse.

For every displayed game state, choose the four literal orders yourself and submit them once through the controller's requested format. The controller calculates state and cost; it does not choose orders. Do not write or execute an ordering policy, optimizer, random-choice generator, or future-week decision loop. Do not precompute future orders. Receive the next complete public display before making the next choices.

The classroom time allowance is fictional. The study imposes no response deadline on your model computation or tool submissions. Do not run a timer, wait to simulate a duration, claim that the model's time expired, leave an answer blank or use a default. Provide an actual literal choice for every displayed role or scenario. There is one submission opportunity with no revision or second pass. Zero, repeated, constant, and identical orders are allowed. There is no preferred order maximum or required positive order.

After the game, the controller presents independent hypothetical situations in pages of four. Treat each as a separate decision for the displayed role in the same fictional classroom time situation, using only that scenario's facts. The three pipeline-arrival entries describe outstanding cases arriving in the next three weeks; they sum to the stated outstanding amount. The customer-demand field means this role's current incoming customer request. Recent demand history is that role's recent incoming requests, from oldest to newest. Submit one literal order per displayed scenario ID. Do not turn these scenarios into additional game weeks.

Finally, answer the untimed multiple-choice questions in the requested format. These questions do not allow revisions to earlier orders. After submitting the quiz and receiving the controller's completion acknowledgment, include `fictional_student_seconds` in your final report, giving the number of seconds the fictional students were told they had per game or scenario decision.

Use only the public controller display and submission interface. Do not inspect implementation source, private state, random seeds, future demand, answer keys, probe-pair labels, other sessions, or analysis. Do not alter the controller or its settings. If a display is incomplete, a required tool is unavailable, or a submission is rejected, record the failure and stop rather than inventing data or attempting a repair. Return the controller's preserved record unchanged.


# Fictional classroom time allowance

In this fictional classroom session, each student has 8 seconds to choose an order for each game state or hypothetical situation. Portray the decision that this ordinary novice would make with that amount of classroom time. The allowance describes the student's fictional situation; it does not limit the model's actual computation or tool response time. The reading and final quiz are untimed.


A supply chain connects businesses through requests and deliveries. A request records a decision, while a delivery changes the goods physically available. These events can occur in different weeks. Outstanding replenishment includes earlier requests that have not yet arrived, including quantities in transit and quantities awaiting upstream fulfillment.

For example, a shop requests six cases in week one, and those cases arrive in week four. A shortage observed in weeks two and three does not change the date of that earlier request. Further requests create additional commitments, whose arrivals may overlap later. The relationship between present conditions and later receipts therefore depends on earlier decisions and delivery delays.

Each business receives requests from its immediate customer. Those requests can differ from purchases by final consumers. A temporary change in purchases can lead several businesses to revise their requests at different times. Their deliveries then reflect those separate decisions. Shared records can distinguish goods currently available, customer obligations, and replenishment already requested. This reading explains relationships without specifying an ordering rule.


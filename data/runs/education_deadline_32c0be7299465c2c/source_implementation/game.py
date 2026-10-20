"""Physical four-role simulator; units are cases, periods are weeks."""
import numpy as np
ROLES = ('retailer', 'wholesaler', 'distributor', 'factory')

class BeerGame:
    def __init__(self):
        self.inventory = np.full(4, 12, dtype=np.int64)
        self.backlog = np.zeros(4, dtype=np.int64)
        self.delivery = [[4,4] for _ in range(3)] + [[4,4,4]]
        self.incoming = np.full(3,4,dtype=np.int64)
        self.outstanding = np.full(4,12,dtype=np.int64)
        self.week = 0
        self.awaiting = False

    def observe(self, customer_demand):
        assert not self.awaiting and type(customer_demand) is int and customer_demand >= 0
        self.week += 1
        receipts = np.array([q.pop(0) for q in self.delivery])
        self.inventory += receipts
        self.outstanding -= receipts
        demand = np.r_[customer_demand, self.incoming]
        owed = self.backlog + demand
        shipped = np.minimum(self.inventory, owed)
        self.inventory -= shipped
        self.backlog = owed - shipped
        for i in range(3): self.delivery[i].append(int(shipped[i+1]))
        self.awaiting = True
        shared = dict(zip(ROLES, map(int, self.inventory)))
        return [dict(week=self.week,role=role,demand=int(demand[i]),received=int(receipts[i]),
            shipped=int(shipped[i]),inventory=int(self.inventory[i]),backlog=int(self.backlog[i]),
            net_inventory=int(self.inventory[i]-self.backlog[i]),supply_line=int(self.outstanding[i]),
            cost=float(.5*self.inventory[i]+self.backlog[i]),shared_inventory=shared.copy())
            for i,role in enumerate(ROLES)]

    def commit(self, orders):
        assert self.awaiting
        # No treatment/order-entry cap. An external circuit breaker handles absurd scales.
        assert len(orders)==4 and all(type(q) is int and 0<=q<=100000 for q in orders)
        self.outstanding += np.array(orders,dtype=np.int64)
        self.incoming = np.array(orders[:3],dtype=np.int64)
        self.delivery[3].append(orders[3])
        self.awaiting = False
        assert (self.outstanding>=0).all()
        for i in range(3):
            assert self.outstanding[i]==sum(self.delivery[i])+self.backlog[i+1]+orders[i]
        assert self.outstanding[3]==sum(self.delivery[3])


def demand_path(weeks):
    return [4 if i<4 else 8 for i in range(weeks)]


def continuation(game, customer_demand, weeks=12):
    rows=[]
    for _ in range(weeks):
        states=game.observe(customer_demand)
        orders=[s['demand'] for s in states]
        rows.extend(dict(s,order=q,phase='automatic') for s,q in zip(states,orders))
        game.commit(orders)
    return rows


def calibration_states():
    states=[]
    for role in ROLES:
        for inventory in (0,24):
            for supply_line in (0,12,36):
                shared={r:12 for r in ROLES};shared[role]=inventory
                states.append(dict(week=12,role=role,demand=8,received=4,shipped=4,
                    inventory=inventory,backlog=8 if inventory==0 else 0,
                    net_inventory=inventory-(8 if inventory==0 else 0),supply_line=supply_line,
                    cost=.5*inventory+(8 if inventory==0 else 0),shared_inventory=shared))
    return states

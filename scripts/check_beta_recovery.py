"""Free structural-estimator check on closed-loop policies, with known beta."""
import sys
from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from beergame_study.game import BeerGame, ROLES, demand_path
from beergame_study.estimation import estimate_beta

def check():
    fits=[];trajectories=[]
    for beta in (0.,.35,.65,1.):
        game=BeerGame();forecasts=[4.]*4;rows=[]
        for w,d in enumerate(demand_path(40),1):
            states=game.observe(d);orders=[]
            for i,s in enumerate(states):
                if w<=4:q=4
                else:
                    forecasts[i]=.4*s['demand']+.6*forecasts[i]
                    q=max(0,int(round(forecasts[i]+.35*(24-s['net_inventory']-beta*s['supply_line']))))
                orders.append(q);rows.append(dict(s,order=q,true_beta=beta,phase='warmup' if w<=4 else 'agent'))
            game.commit(orders)
        f=pd.DataFrame(rows);trajectories.extend(rows)
        for role,a in f[f.phase=='agent'].groupby('role'):
            fit=estimate_beta(a)
            positive=int((a.order>0).sum())
            if positive<5:fit.update(usable=False,fit_flag=fit['fit_flag']+';too_few_positive_orders')
            fits.append(dict(true_beta=beta,role=role,positive_orders=positive,
                absolute_beta_error=abs(fit['beta']-beta),**fit))
    out=ROOT/'reports/software_checks/beta_closed_loop_20261005'
    out.mkdir(parents=True,exist_ok=True)
    pd.DataFrame(fits).to_csv(out/'recovery.csv',index=False)
    pd.DataFrame(trajectories).to_csv(out/'synthetic_trajectories.csv',index=False)
    print(pd.DataFrame(fits)[['true_beta','role','beta','absolute_beta_error','r2','usable','fit_flag']].to_string(index=False))
    print('Synthetic known policies only: no GPT evidence or paid calls.')
    return pd.DataFrame(fits)

if __name__=='__main__':check()

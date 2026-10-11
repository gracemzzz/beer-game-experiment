"""Checkpointed, paced requests. No live client is created by this module."""
import asyncio, hashlib, json, time
from pathlib import Path
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from .config import RATES

class StudyStopped(RuntimeError): pass
class GroupFailed(RuntimeError): pass

def digest(x): return hashlib.sha256(json.dumps(x,sort_keys=True).encode()).hexdigest()
def save(path, value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    temporary=path.with_suffix(path.suffix+'.tmp')
    temporary.write_text(json.dumps(value,indent=2,allow_nan=False));temporary.replace(path)

def price(usage):
    return ((usage.get('input_tokens',0)-usage.get('cached_input_tokens',0))*RATES['input']+
            usage.get('cached_input_tokens',0)*RATES['cached']+usage.get('output_tokens',0)*RATES['output'])/1e6

class Gateway:
    def __init__(self,directory,config,client=None,callback=None):
        self.directory=Path(directory);self.cache=self.directory/'requests';self.cache.mkdir(parents=True,exist_ok=True)
        self.config=config;self.client=client;self.callback=callback or (lambda:None)
        self.charged=sum(json.loads(p.read_text()).get('charge_usd',0) for p in self.cache.glob('*.json'))
        self.sem=asyncio.Semaphore(config.concurrency);self.lock=asyncio.Lock()
        self.next_start=0.;self.cooldown=0.;self.active=0;self.cached=0;self.finished=0;self.fatal=None

    async def pace(self):
        # Recheck shared cooldown after sleep, including cooldown set by another worker.
        while True:
            async with self.lock:
                wait=max(self.next_start,self.cooldown)-time.monotonic()
                if wait<=0:
                    self.next_start=time.monotonic()+self.config.request_interval_s
                    return
            await asyncio.sleep(min(wait,1))

    async def request(self,identity,messages,limit,schema=None,synthetic=None):
        key=digest(dict(identity=identity,messages=messages,limit=limit,schema=schema,model=self.config.model))
        for attempt in range(self.config.transport_retries+1):
            path=self.cache/f'{key}_{attempt}.json'
            if path.exists():
                record=json.loads(path.read_text())
                if record['status']=='ok':
                    self.cached+=1;self.finished+=1;self.callback();return record
                if record['status']=='transient':continue
                raise StudyStopped('Saved unresolved request: '+path.name+' ('+record['status']+'). Inspect before resuming.')
            if self.fatal:raise self.fatal
            if self.config.mode=='offline':
                record=dict(identity=identity,status='ok',response_status='completed',text=synthetic or '',
                    usage=dict(input_tokens=0,output_tokens=0,cached_input_tokens=0,reasoning_tokens=0),
                    charge_usd=0.,elapsed_s=0.,limit=limit,synthetic=True)
                save(path,record);self.finished+=1;self.callback();return record
            async with self.sem:
                if self.client is None:raise StudyStopped('An API client is required in API mode.')
                await self.pace()
                if self.fatal:raise self.fatal
                # Reservation uses UTF-8 bytes + overhead as a conservative token allowance.
                reserve=((len(json.dumps(messages).encode())+len(json.dumps(schema).encode())+2048)*RATES['input']+limit*RATES['output'])/1e6
                if self.charged+reserve>self.config.budget_usd:
                    self.fatal=StudyStopped(f'Local spending limit: ${self.charged:.4f} charged/reserved; '
                        f'next reservation ${reserve:.4f}. Raise only budget_usd to resume this run.')
                    raise self.fatal
                self.charged+=reserve
                record=dict(identity=identity,status='pending',charge_usd=reserve,messages=messages,
                    limit=limit,schema=schema,created_utc=datetime.now(timezone.utc).isoformat())
                save(path,record);start=time.monotonic();self.active+=1;self.callback()
                try:
                    kwargs=dict(model=self.config.model,input=messages,reasoning={'effort':'none'},
                        max_output_tokens=limit,store=False)
                    if schema:kwargs['text']={'format':{'type':'json_schema','name':'answer','strict':True,'schema':schema}}
                    response=await self.client.responses.create(**kwargs)
                    raw=response.model_dump(mode='json');usage=raw.get('usage') or {}
                    u=dict(input_tokens=usage.get('input_tokens',0),output_tokens=usage.get('output_tokens',0),
                        cached_input_tokens=(usage.get('input_tokens_details') or {}).get('cached_tokens',0),
                        reasoning_tokens=(usage.get('output_tokens_details') or {}).get('reasoning_tokens',0))
                    text=''.join(c.get('text','') for o in raw.get('output',[]) if o.get('type')=='message'
                                 for c in o.get('content',[]) if c.get('type')=='output_text')
                    refused=any(c.get('type')=='refusal' for o in raw.get('output',[]) for c in o.get('content',[]))
                    reason=(raw.get('incomplete_details') or {}).get('reason')
                    if usage:
                        actual=price(u);self.charged+=actual-reserve;record['charge_usd']=actual
                    record.update(status='ok',response_status=raw.get('status'),incomplete_reason=reason,
                        refused=refused,text=text,usage=u,response=raw,elapsed_s=time.monotonic()-start)
                    save(path,record)
                    if u['reasoning_tokens'] or u['output_tokens']>limit:
                        self.fatal=StudyStopped('Token manipulation violated: unexpected reasoning or output allowance. Saved response.')
                        record['status']='protocol_error';save(path,record);raise self.fatal
                    self.finished+=1;return record
                except StudyStopped:raise
                except asyncio.CancelledError:
                    # Pending reservation remains: outcome/usage unknown; never silently resend.
                    raise
                except Exception as exc:
                    http=getattr(exc,'status_code',None);body=getattr(exc,'body',{}) or {}
                    error=body.get('error',body) if isinstance(body,dict) else {}
                    code=error.get('code') or error.get('type')
                    transient=(http in (408,409,500,502,503,504) or
                               http==429 and code in ('rate_limit_exceeded','rate_limit_error') or
                               type(exc).__name__ in ('APIConnectionError','APITimeoutError'))
                    retry=0.;headers=getattr(getattr(exc,'response',None),'headers',{}) or {}
                    try:retry=float(headers.get('retry-after',0))
                    except (TypeError,ValueError):
                        try:retry=max(0,parsedate_to_datetime(headers['retry-after']).timestamp()-time.time())
                        except Exception:pass
                    # Preserve unknown usage; known HTTP rejection has no generated output.
                    if http in (400,401,403,404,429):self.charged-=reserve;record['charge_usd']=0.
                    record.update(status='transient' if transient else 'api_error',error_type=type(exc).__name__,
                        http_status=http,error_code=code,elapsed_s=time.monotonic()-start)
                    save(path,record)
                    if not transient:
                        self.fatal=StudyStopped(f'API stopped: {type(exc).__name__}, HTTP {http}, code {code}. See {path.name}.')
                        raise self.fatal from None
                    if attempt==self.config.transport_retries:
                        self.fatal=StudyStopped('Transport retry limit reached. All attempts saved; no order substituted.')
                        raise self.fatal from None
                    self.cooldown=max(self.cooldown,time.monotonic()+max(retry,min(60,2**(attempt+1))))
                finally:
                    self.active-=1;self.callback()
        raise StudyStopped('Saved transport attempts exhausted; no new request sent.')

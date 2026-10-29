#!/usr/bin/env python3
"""Small resumable wrapper around the user's existing EDIT-only Studio worker.

The chosen provider is ntfy.envs.net, not the retired ntfy.sh transport.
No Play, mouse input, publish or local place-file save is implemented.
"""
from __future__ import annotations
from pathlib import Path
import json,os,subprocess,sys

ROOT=Path(__file__).resolve().parents[2]
ADMIN=ROOT/'studio_bridge/provider_switch/community_admin.py'
JOURNAL=ROOT/'reactor_startup/qa/studio_jobs.json'
ENV=dict(os.environ)
ENV['PYTHONPATH']=str(ROOT/'.cache/studio_pydeps')+':'+str(ADMIN.parent)
ALLOWED={'list_roblox_studios','get_studio_state','search_game_tree',
         'script_read','multi_edit','execute_luau','inspect_instance'}


def admin(*args):
 result=subprocess.run([sys.executable,str(ADMIN),*args],env=ENV,
                       text=True,capture_output=True,timeout=175)
 if result.returncode:raise RuntimeError(
  'Studio worker '+args[0]+': '+result.stderr.strip()[:450])
 return json.loads(result.stdout)

def save(data):
 JOURNAL.parent.mkdir(parents=True,exist_ok=True)
 JOURNAL.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')

def request(key,tool,args,timeout=130):
 assert tool in ALLOWED,('Forbidden bridge tool',tool)
 journal=json.loads(JOURNAL.read_text()) if JOURNAL.exists() else {}
 previous=journal.get(key,{})
 if previous:
  assert previous['tool']==tool and previous['arguments']==args,(
   key,'different arguments for an already-issued job')
  if previous['state']=='done':
   return previous['response']
  if previous['state']=='error':
   raise RuntimeError(key+' previously failed: '+previous.get('error',''))
  job=previous['job']
 else:
  payload=json.dumps(args,ensure_ascii=False)
  if len(payload)>80_000:
   source=ROOT/'reactor_startup/qa'/f'{key}_request.json'
   source.write_text(payload)
   arg='@'+str(source)
  else:arg=payload
  issued=admin('call',tool,arg)
  job=issued.get('job')
  if not job:raise RuntimeError(key+' produced no Studio job '+str(issued)[:260])
  journal[key]={'tool':tool,'arguments':args,'job':job,'state':'pending'}
  save(journal)
  print(key,'queued',job,flush=True)
 result=admin('wait',job,str(timeout))
 if result.get('status')!='done':
  raise TimeoutError(key+' still pending; rerun SAME command to resume')
 raw=json.loads(Path(result['response_file']).read_text())
 tool_result=raw.get('response',{}).get('result',{})
 texts=[x.get('text','') for x in tool_result.get('content',[])
        if x.get('type')=='text']
 response={'ok':result.get('ok') is True and
                 tool_result.get('isError') is False,
           'texts':texts,'job':job}
 journal[key]['response']=response
 journal[key]['state']='done' if response['ok'] else 'error'
 if not response['ok']:
  journal[key]['error']=' | '.join(texts)[:600]
 save(journal)
 if not response['ok']:
  raise RuntimeError(key+' Studio tool error: '+str(texts)[:600])
 return response

if __name__=='__main__':
 if len(sys.argv)<4:raise SystemExit('usage: studio_bus.py KEY TOOL JSON_OR_@FILE')
 key,tool,arg=sys.argv[1:4]
 args=json.loads(Path(arg[1:]).read_text() if arg.startswith('@') else arg)
 out=request(key,tool,args)
 for text in out['texts']:
  print(text[:20000])

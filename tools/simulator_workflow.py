"""Read-only deck preflight and bounded random-policy timing; never trains."""
import argparse,json,hashlib,platform,random,re,sys,time,uuid
from dataclasses import asdict
from pathlib import Path
from types import SimpleNamespace

def preflight(decks):
 from expanded import cards
 from expanded.decks import validate
 from expanded.dependencies import declaration_operations,dependency_report
 from expanded.generation import GenerationEffects
 from expanded.generation_cards import requests_for
 from expanded.generation_extensions import requests_for as extended
 from expanded.fabled_decks import expand_bundle_ids
 from engine.cards import UnsupportedCard
 records=cards.registry();declarations=declaration_operations(vars(cards));rows=[]
 class Probe(GenerationEffects):pass
 for deck in decks:
  errors=validate(deck,records);roots=set(deck.cards)|set(deck.contraband_beasts)
  if deck.beatrix_minion:roots.add(deck.beatrix_minion)
  try:roots.update(expand_bundle_ids(deck.cards))
  except ValueError:pass
  # Traverse explicit dependencies and every resolved static generation pool.
  probe=Probe();probe.cards=records;probe.players=[SimpleNamespace(hero_class=deck.hero_class)]
  queue=sorted(roots);seen=set();blocked=[];pools=0
  while queue:
   cid=queue.pop()
   if cid in seen:continue
   seen.add(cid)
   result=dependency_report(declarations,records,roots=[cid])
   for failure in result['missing_paths']:blocked.append(failure)
   from expanded.dependencies import literal_dependencies
   queue.extend(literal_dependencies(declarations.get(cid,())))
   for request in requests_for(cid)|extended(cid):
    pools+=1
    try:queue.extend(probe._generation_candidates(request,0))
    except UnsupportedCard as exc:blocked.append(dict(root=cid,request=repr(request),message=str(exc)))
  rows.append(dict(hero_class=deck.hero_class,legal_errors=errors,dependency_blockers=blocked,identities_checked=len(seen),static_pools_checked=pools))
 return dict(known_checks_passed=all(not r['legal_errors'] and not r['dependency_blockers'] for r in rows),full_support_certified=False,
  limitation='Checks legality, explicit literal dependencies and declared static pools. Computed pools, helper effects, exceptional contracts and independent fidelity remain outside this check.',decks=rows)

def benchmark_decks():
 from expanded.cards import registry,COLLECTIBLE_IDS
 from expanded.decks import Deck
 records=registry()
 def keyword_only(record):
  text=re.sub("<[^>]*>","",record.get("text",""))
  text=re.sub(r"\b(Taunt|Rush|Charge|Windfury|Divine Shield|Lifesteal|Poisonous|Stealth|Elusive)\b","",text)
  return not re.sub(r"[\s.,]","",text)
 # Deliberately narrow workload with no printed effects, not a full-format claim.
 ids=[cid for cid in sorted(COLLECTIBLE_IDS) if records[cid].get('type')=='MINION' and records[cid].get('cardClass')=='NEUTRAL' and keyword_only(records[cid]) and set(records[cid].get('mechanics',())) <= {'TAUNT','RUSH','CHARGE','WINDFURY','DIVINE_SHIELD','LIFESTEAL','POISONOUS','STEALTH','ELUSIVE'} and records[cid].get('rarity')!='LEGENDARY']
 from expanded.identities import canonical_identity
 seen=set();unique=[]
 for cid in ids:
  identity=canonical_identity(records[cid],records)
  if identity not in seen:seen.add(identity);unique.append(cid)
 if len(unique)<15:raise ValueError('Not enough basic keyword benchmark cards')
 cards=tuple(cid for cid in unique[:15] for _ in range(2))
 return [Deck('MAGE',cards),Deck('WARRIOR',cards)]

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=['scope','benchmark']);p.add_argument('--engine-root',type=Path,default=Path('staging/rebased-88'));p.add_argument('--decks',type=Path);p.add_argument('--games',type=int,default=3);p.add_argument('--max-actions',type=int,default=200);p.add_argument('--seed',type=int,default=97);p.add_argument('--output',type=Path)
 a=p.parse_args()
 if not 1<=a.games<=100 or not 1<=a.max_actions<=10000:p.error('Use 1..100 games and 1..10000 actions')
 root=a.engine_root.resolve();sys.path.insert(0,str(root))
 from expanded import Deck,Game
 from expanded.status import code_fingerprint
 from stress_candidate import restore_deck
 decks=[restore_deck(d,Deck) for d in json.loads(a.decks.read_text())] if a.decks else benchmark_decks()
 if len(decks)!=2:p.error('Deck input must be a JSON array of exactly two Deck records')
 before=code_fingerprint();scope=preflight(decks)
 report=dict(command=a.command,engine_fingerprint=before,tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),scope=scope,decks=[asdict(d) for d in decks],seed=a.seed,training_executed=False)
 if a.command=='benchmark' and scope['known_checks_passed']:
  results=[];total=0;start=time.perf_counter()
  for index in range(a.games):
   seed=a.seed+index;rng=random.Random(seed+100000);init=time.perf_counter();g=Game(decks,seed=seed,record=False);setup=time.perf_counter()-init;loop=time.perf_counter();actions=0
   while not g.terminal and actions<a.max_actions:
    legal=g.legal_actions()
    if not legal:raise AssertionError('Nonterminal game has no legal actions')
    g.step(rng.choice(legal));actions+=1
   elapsed=time.perf_counter()-loop;g.assert_invariants();total+=actions
   results.append(dict(seed=seed,actions=actions,terminal=g.terminal,winner=g.winner,setup_seconds=setup,decision_seconds=elapsed))
  elapsed=time.perf_counter()-start;decision_seconds=sum(r['decision_seconds'] for r in results)
  report.update(workload='Basic keyword neutral minion decks unless explicit decks supplied; random legal actions, no policy features, recording or learning. Timing excludes preflight.',python=platform.python_version(),platform=platform.platform(),max_actions=a.max_actions,games=a.games,results=results,seconds=elapsed,decisions_per_second=total/decision_seconds if decision_seconds else 0,games_processed_per_second=a.games/elapsed,completed_games=sum(r['terminal'] for r in results),capped_games=sum(not r['terminal'] for r in results))
 report['source_unchanged']=before==code_fingerprint()
 if a.output:
  a.output.parent.mkdir(parents=True,exist_ok=True)
  path=a.output.with_name(a.output.stem+'-'+uuid.uuid4().hex+'.json');path.write_text(json.dumps(report,indent=2)+'\n');report['report_path']=str(path)
 print(json.dumps(report,indent=2))
 return int(not scope['known_checks_passed'] or not report['source_unchanged'])
if __name__=='__main__':raise SystemExit(main())

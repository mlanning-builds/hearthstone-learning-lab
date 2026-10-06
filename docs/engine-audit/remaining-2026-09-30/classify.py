"""Planning inventory only. Does not generate executable Hearthstone rules.
Explicit reviewed groups take precedence; text assists grouping the remainder.
Fail on unclassified cards so new snapshots require another review.
"""
from pathlib import Path
import json,hashlib,re
from collections import Counter
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
ENGINE=ROOT/'staging/rebased-88/expanded'
audit=json.loads((ENGINE/'catalog_audit.json').read_text())
index=json.loads((ENGINE/'implementation_index.json').read_text())
remaining={c['id']:c for c in audit['cards'] if c['implementation']=='missing'}
assert len(remaining)==519
assert set(remaining).isdisjoint(index['implemented_card_ids'])
GROUPS={}
assigned={}
def group(key,bucket,label,reason,ids=''):
 GROUPS[key]=dict(bucket=bucket,label=label,reason=reason)
 for cid in ids.split():
  assert cid in remaining,cid
  assert cid not in assigned,(cid,assigned.get(cid))
  assigned[cid]=key
# A: bounded local additions; still need specs, tokens and interaction checks.
group('local_composition','A','Mostly existing mechanics','Existing draw, summon, choice, history, payload and trigger helpers cover the main behavior; add bounded glue and fixed dependencies, then validate.',
'''CAP_102 CAP_107 CAP_403 CATA_586 CATA_EVENT_001 EDR_271 EDR_455 EDR_494 JAIL_734 JAIL_851 TIME_713 TIME_870''')
# B: a shared extension can unlock a family; not trivial card wiring today.
group('held_progress','B','Held upgrades and turn counters','Extend physical-card progress and expiry hooks; verify threshold and turn-boundary semantics before reuse.',
'''CATA_131 CATA_132 CATA_498 FIR_911 FIR_914 FIR_916 JAIL_501''')
group('provenance','B','Card origin and hand-entry tracking','Track physical starting-deck origin, copied-from-opponent identity and hand-entry time through every draw, copy, shuffle and control transition.',
'''CORE_REV_946 DINO_409 EDR_251 EDR_256 JAIL_205 JAIL_380 JAIL_432 JAIL_433 JAIL_434 TLC_364''')
group('types','B','Type matching and Kindred selectors','Extend multi-type matching, distinct selection and Kindred partner eligibility; verify ALL-type and overlapping-type cases.',
'''CORE_WON_141 TLC_102 TLC_110 TLC_222 TLC_254''')
group('modifiers','B','Damage, healing, costs and temporary control','Extend source-aware damage/healing replacement or ordered modifiers; existing flat buffs alone do not cover the rule.',
'''CAP_104 CATA_186 CATA_301 CATA_307 CATA_496 EDR_258 EDR_480 EDR_525 JAIL_330 TIME_214''')
group('payment','B','Health/Corpse payment','Add alternate payment to legal actions and resolution, including prevention, lethal payment and modifier interactions.',
'''CATA_180 CORE_ETC_523 EDR_489 TLC_436''')
group('draw_events','B','Draw listeners','Add draw-event publication with burn, fatigue, copy and continuation semantics.',
'''CORE_SCH_717 CORE_TTN_843''')
group('death_replay','B','Recorded deathrattle replay','Reuse captured death records but add nested resumable effect replay and listener/death ordering.',
'''TLC_106 JAIL_940''')
group('discover_events','B','Discover history and delayed rewards','Add Discover-specific events/counters and follow-up choice ownership; ordinary choices must not count as Discover.',
'''TLC_365 TLC_483 TLC_500'''.replace(' TLC_500',''))
group('cannoneers','B','Cannoneer shared firing rules','Add a shared firing operation and permanent extra-shot modifier; include fixed Cannoneer token behavior.',
'''CAP_103 CAP_106''')
group('leeches','B','Leech health stealing','Implement the fixed Leech token and player-level steal amount; include lowest-health ties and hero/minion health semantics.',
'''EDR_810 EDR_814 EDR_817''')
group('void_souls','B','Void Soul generation and upgrades','Review and implement the fixed Void Soul dependency plus persistent upgrade state; a random-generator member also needs its full pool.',
'''JAIL_730 JAIL_732 JAIL_733 JAIL_891''')
group('leylines','B','Leyline scaling and persistent upgrades','Implement the three related Leylines and shared upgrade/cost/repetition state; random-minion Leyline also needs pool closure.',
'''MEND_500 MEND_501 MEND_502 MEND_503 MEND_504 MEND_505 MEND_506''')
group('animal_companions','B','Animal Companion replacement and count','Centralize Companion generation and persistent substitutions/counts; replacement Beast pools must also be complete.',
'''MEND_300 MEND_303 MEND_304 MEND_307''')
group('bonus','B','Random Bonus Effects','Define the exact keyword pool, exclusions, stacking and steal/transfer rules; shared by multiple cards.',
'''CATA_206 EDR_849 JAIL_101 TLC_240 TLC_444 TLC_465''')
group('temporary','B','Temporary cards and attached hand effects','Add temporary generated-card expiry and playable-hand-card grant semantics; generated pools remain separate dependencies.',
'''CAP_002 CAP_101 CAP_402 CAP_802 JAIL_986 TLC_446 TLC_449 TLC_450 TLC_451 TLC_469''')
group('either_side','B','Play onto either board','Extend action encoding, board-space legality and controller-dependent Battlecries/deathrattles.',
'''CAP_004 JAIL_442 JAIL_452 JAIL_455 JAIL_461''')
group('small_state','B','Bounded state/choice extensions','A local feature extension is needed beyond composing current opcodes; inspect the card-specific explanation and generated dependencies.',
'''CATA_213 CATA_472 CATA_591 DINO_136 DINO_414 EDR_454 EDR_526 EDR_780 JAIL_421 JAIL_852 TIME_030 TIME_620 TLC_241 TLC_251 TLC_515 TLC_987''')
# D: broad lifecycle/action changes or intricate one-off systems.
group('combat','D','Forced attacks and combat interruption','Need an owner-correct resumable combat API, precombat interruption, retaliation, kill attribution and death/choice checkpoints.',
'''CAP_806 CORE_BT_120 CORE_RLK_086 CORE_TTN_866 CS3_020 DINO_400 DINO_422 DINO_428 EDR_014 EDR_453 EDR_819 JAIL_315 JAIL_435 JAIL_454 JAIL_511 RLK_720 TIME_434 TIME_443 TIME_602 TLC_107 TLC_230 TLC_810 TLC_821 CATA_185''')
group('autocast','D','Casting/replaying cards inside effects','Need nested play frames, legal/random targets, counter/trigger timing and resumable repeated effects; damage-only substitutions are insufficient.',
'''CORE_WON_145 CATA_154 CATA_563 CATA_786 EDR_031 EDR_259 EDR_464 EDR_520 FIR_959 JAIL_123 JAIL_500 JAIL_515 JAIL_974 MEND_046 MEND_100 TIME_033 TIME_860 TLC_430 TLC_438 TLC_522 TLC_836''')
group('draw_cast','D','Casts/Summons When Drawn','Need a resumable draw pipeline, automatic effect resolution/replacement draw, burned-card rules and correct summon controller.',
'''CAP_400 CAP_401 CAP_404 CAP_406 CORE_SW_439 EDR_260 JAIL_386 JAIL_443 JAIL_879 JAIL_881 TIME_025 TIME_026 TIME_027 TIME_028 TIME_029 TLC_518''')
group('deckbuilding','D','Setup, deckbuilding and hero replacement','Touches deck legality, initial state, starting hands/hero powers or attached special cards; cannot be implemented as a normal Battlecry.',
'''CORE_EX1_323 EDR_000 JAIL_384 JAIL_397 JAIL_430 JAIL_446 JAIL_504 JAIL_800 JAIL_831 JAIL_860 TIME_005 TIME_009 TIME_020 TIME_209 TIME_211 TIME_609 TIME_619 TIME_850 TIME_852 TIME_875 TIME_890 CATA_615''')
group('unique','D','Custom or unusual persistent systems','Needs a dedicated state/action contract and generated effects; research/implementation effort is not established by a short card description.',
'''CAP_405 CAP_805 CATA_470 CATA_EVENT_110 CORE_CFM_670 CORE_DAL_575 EDR_529 EDR_818 EDR_895 END_012 END_018 END_024 END_037 JAIL_319 JAIL_398 JAIL_458 JAIL_502 JAIL_509 JAIL_719 JAIL_887 JAIL_EVENT_100 JAIL_EVENT_101 TIME_024 TIME_041 TIME_064 TIME_618 TIME_704 TIME_706 TIME_861 TIME_EVENT_998 TLC_100 TLC_452 TLC_632 TLC_841''')
group('scope','D','Noncombat simulation scope decisions','Decide explicitly whether emote/timer behavior is modeled or intentionally omitted in this ML simulator; do not silently count it as implemented.',
'''CS3_035 JAIL_703''')
# Family assignment assisted by printed labels, then all leftovers reviewed.
family_rules=[
 ('rewind','D','Rewind and alternate outcomes','Rollback/counterfactual outcomes, RNG and hidden-information handling need a shared contract.',r'\brewind'),
 ('shatter','D','Shatter and Advance','Split/recombined card identity and Advance transformations need new hand/deck/action semantics.',r'\bshatter\b|advance to the present'),
 ('herald','B','Herald and Deathwing upgrades','Implement Herald progress, Soldier generation and Deathwing upgrade dependencies together.',r'\bherald\b'),
 ('colossal','D','Colossal and appendages','Implement appendage placement, lifecycle and component-specific effects; some also require forced attacks or spell repetition.',r'colossal|appendages'),
 ('prepare','B','Prepare','Implement shared Prepare action, discount/progress state and associated triggers; complex reward effects remain separate dependencies.',r'\bprepare\b'),
 ('imbue','B','Imbue and upgraded hero powers','Implement all affected hero-power upgrades and Imbue progress plus generated dependencies.',r'imbue'),
 ('dark_gift','B','Dark Gifts','Implement the complete Dark Gift effect pool and attached-state behavior; Discover variants also depend on generated-card pools.',r'dark\s+gift'),
 ('dormant','B','Dormant and awakening','Add inactive board entities, targeting/trigger suppression, wake timing and conditional awakening.',r'dormant|falls asleep'),
 ('quests','D','Quests and rewards','Add quest slots/progress, event conditions and complete reward effects; each reward needs separate review.',r'quest:|sidequest:'),
]
for key,bucket,label,reason,pattern in family_rules:
 group(key,bucket,label,reason)
 for cid,c in remaining.items():
  if cid not in assigned and re.search(pattern,c['rules_text'],re.I):assigned[cid]=key
# Bounded closed families with dependencies that are not evident in parent text.
for cid in ['EDR_001','EDR_846']:
 if cid not in assigned:assigned[cid]='small_state'
# C: simple *main* effect, not currently complete because generation can reach missing effects.
group('generation','C','Global generation/Discover pool dependencies','Main effect often uses familiar operations, but exact pool eligibility and every possible generated card must work. No supported-only pool substitution. Additional card-specific conditions may still need local glue.')
for cid,c in remaining.items():
 if cid not in assigned and re.search(r'discover|random (?:\d+-cost |legendary |taunt |holy |shadow |nature |fel |frost |arcane |paladin |druid |shaman |demon hunter |mage |deathrattle |playable |temporary |choose one |\{0\}-cost |\d+, \d+, and \d+-cost )?(?:card|spell|minion|beast|demon|dragon|pirate|murloc|mech|weapon|mask|elemental|undead)|summon (?:a|an|two|three) (?:random )?\d+-cost|from the past',c['rules_text'],re.I):assigned[cid]='generation'
# Manual review of whitespace/plural variants and compound effects.
manual={
 'generation': 'CATA_499 CATA_556 CATA_569 CORE_CATA_006 CORE_CFM_781 CORE_KAR_077 CORE_TID_931 CORE_WON_337 DINO_427 DINO_433 DINO_434 EDR_493 EDR_873 END_015 JAIL_125 JAIL_200 JAIL_313 JAIL_448 JAIL_474 JAIL_806 JAIL_876 JAIL_878 MEND_042 MEND_045 TIME_102 TIME_613 TIME_859 TIME_EVENT_997 TLC_516 TLC_814',
 'modifiers': 'CATA_480 CATA_621 TLC_228 TIME_217',
 'small_state': 'CORE_EDR_003 CORE_LOOT_101 EDR_781 JAIL_987',
 'payment': 'TLC_467',
 'colossal': 'CATA_527',
 'unique': 'CATA_567',
}
for key,ids in manual.items():
 for cid in ids.split():
  assert cid in remaining and cid not in assigned,cid
  assigned[cid]=key
# Dependencies noticed during the compound-effect review take precedence.
for key,ids in {
 'payment':'TIME_612 TIME_615',
 'death_replay':'DINO_415',
 'unique':'JAIL_861',
 'discover_events':'TLC_435 TLC_442 TLC_464 TLC_824 TLC_900',
}.items():
 for cid in ids.split():assigned[cid]=key
left=[cid for cid in remaining if cid not in assigned]
if left:
 print('UNCLASSIFIED')
 for cid in left:print(cid,remaining[cid]['rules_text'].replace('\n',' '))
else:print('All assigned')
# Initial review stage prints inventory; final report requires no leftovers.
if __name__=='__main__':
 print('Buckets',dict(Counter(GROUPS[k]['bucket'] for k in assigned.values())))
 print('Groups',dict(Counter(assigned.values())))

assert not left,'Every remaining card must have a reviewed primary category'
assert set(assigned)==set(remaining)
BUCKETS={
 'A':'Lower-risk local additions',
 'B':'Needs a shared-rule extension',
 'C':'Main effect familiar; generation dependencies block completion',
 'D':'Larger systems, unusual effects, or scope decisions',
}
NOTES={
 'CAP_102':'Requires CAP_107t Cannoneer, including its end-turn shot; token does not count as another collectible.',
 'CAP_107':'Pinned CAP_107t is a 1/1 with an end-turn random-enemy shot; existing summon/end-turn primitives cover it.',
 'CAP_403':'Selection is from the actual enemy deck, not a global generated pool; implement private options and deck reorder.',
 'CATA_586':'Self-summoning dependency forms a cycle, not an unknown random pool; verify trigger/death ordering.',
 'CATA_EVENT_001':'Reuse held-card timers/private selection; distinguish discard from destruction and preserve the correct summoned-copy payload.',
 'EDR_271':'Capture the cast Nature spell identity in the generated Treant deathrattle; no random global card pool.',
 'EDR_455':'Discover from recorded friendly Dragon deaths; check duplicates and fresh resurrection semantics.',
 'EDR_494':'Choose from the actual deck, retain consumed identities and add them on death; no global pool.',
 'JAIL_734':'Existing deck-choice and self-buff helpers cover the two branches; verify what counts as an empty deck.',
 'JAIL_851':'Reuse private enemy-hand choice; add the named-card next-turn watch and fixed Coin reward.',
 'TIME_713':'Pinned TIME_713t is a 0/8 Chest whose deathrattle fills its opponent’s hand with Coins; owner semantics matter.',
 'TIME_870':'Recruit from the actual deck and create a fixed enemy Stealth Tiger; include the exact token.',
 'CATA_131':'Previous batch deliberately deferred whether its own payment contributes to the held-mana threshold.',
 'CATA_132':'Same unresolved held-mana timing as Felwood Treant; simple-looking text does not make it ready.',
 'CATA_615':'Generated CATA_615t upgrades the starting Hero Power and makes it cost 1: not just a hand parity transform.',
 'CATA_527':'Generated Nespirah adds an appendage lifecycle dependency despite no Colossal keyword in the parent text.',
 'EDR_454':'This is a LOCATION, not a spell; the generated Egg must retain the chosen Dragon copy payload.',
 'EDR_810':'Pinned EDR_810t steals health from the lowest-health enemy for the hero; not an ordinary damage/heal pair.',
 'EDR_814':'Simple parent spell depends on the complete Leech token behavior.',
 'EDR_817':'Simple draw spell depends on the complete Leech token behavior.',
 'CORE_EX1_323':'Hero replacement and resulting Hero Power matter in addition to the printed weapon Battlecry.',
 'TLC_987':'Damage and play-history lookup are simple, but normal activation depends on supported Quest cards.',
 'TLC_107':'Stormbrewer was intentionally excluded from the previous release pending proper precombat interruption.',
 'JAIL_442':'Also depends on Blight draw-autocasting; playing on either side alone does not complete it.',
 'JAIL_435':'Also has Prepare; the forced-attack engine is the larger blocker.',
 'CAP_402':'Also needs enemy-deck Imp-formant auto-summoning; temporary hand grants are not its only dependency.',
 'TLC_446':'Also needs Quest tracking and its complete reward, not only Temporary cards.',
 'TIME_602':'Also has Rewind and a random Beast pool; forced attacks alone do not complete it.',
 'TIME_033':'Also has Rewind and exact Nature-spell eligibility; nested casting is the primary blocker.',
 'CORE_EDR_004_2026':'Also needs Dark Gifts, complete Beast Discover eligibility and Kindred; Rewind is primary.',
 'CORE_LOOT_101':'Existing Secret event plus excess damage are close, but ordering needs a dedicated integration check.',
 'CS3_035':'Rope/real-time turn limits require an explicit ML-simulator scope decision; not automatically a no-op.',
 'JAIL_703':'Emote unlocking is outside combat but still needs an explicit scope decision; not silently marked supported.',
}
# Secondary tags describe overlapping dependency families, not additional card counts.
TAG_PATTERNS={
 'global_pool_review':r'discover|random.*(?:card|spell|minion|dragon|beast|weapon|demon|pirate|murloc|elemental|undead)|from the past',
 'rewind':r'\brewind', 'shatter_or_advance':r'\bshatter\b|advance to the present',
 'herald':r'\bherald\b', 'colossal':r'colossal|appendage',
 'prepare':r'\bprepare\b','imbue':r'imbue','dark_gift':r'dark\s+gift',
 'dormant':r'dormant|falls asleep','quest':r'quest:|sidequest:',
 'deck_or_setup':r'start of game|while building|fabled|starting hand|always go second',
 'alternate_payment':r'costs?.*(?:health|corpses).*instead|costs Corpses',
 'nested_casting':r'\bcast a |\bcast two |\bcast 2 |\brecast\b|\breplay\b|cast twice',
 'forced_combat':r'force.*attack|they attack|that attacks|this attacks it|battle it|attack.*random enemy|they fight',
 'draw_resolution':r'when drawn|whenever.*draws?|instead of drawing',
}
rows=[]
for cid,c in remaining.items():
 k=assigned[cid];g=GROUPS[k]
 text=' '.join(c['rules_text'].split())
 tags=[tag for tag,pattern in TAG_PATTERNS.items() if re.search(pattern,text,re.I)]
 # Discover from existing zones is a bounded choice, not a global generated pool.
 if k=='local_composition':tags=[t for t in tags if t!='global_pool_review']
 rows.append(dict(card_id=cid,name=c['name'],classes=c['classes'],card_type=c['card_type'],
  text=text,bucket=g['bucket'],primary_family=k,primary_reason=g['reason'],
  secondary_review_tags=tags,card_specific_note=NOTES.get(cid,''),
  confidence='planning estimate; interaction and token review still required'))
counts=Counter(row['bucket'] for row in rows);families=Counter(row['primary_family'] for row in rows)
assert sum(counts.values())==519 and len({r['card_id'] for r in rows})==519
payload=dict(date='2026-09-30',scope='Pinned regular Standard 36.6.0.251952; not live legality; excludes Mercenaries and Battlegrounds',
 baseline=dict(collectibles=1185,written=666,remaining=519,source_fingerprint='9a28ca6b4823eb9084f718db705a1a20197e056295b36518d889d17fd64256ec',
 audit_sha256=hashlib.sha256((ENGINE/'catalog_audit.json').read_bytes()).hexdigest()),
 method='First-pass engineering triage of every missing card. Explicit ID review and printed-text-assisted families compared against current engine modules. Not executable rules, exhaustive generated dependency closure, a time estimate, or client-conformance certification.',
 buckets={k:dict(label=BUCKETS[k],count=counts[k]) for k in BUCKETS},
 families={k:dict(**v,count=families[k]) for k,v in GROUPS.items()},cards=rows)
(OUT/'classification.json').write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n')
summary=['# Remaining Standard cards: implementation classification','',
'Baseline: **666 written / 1,185 collectible cards; 519 remaining**, pinned snapshot 36.6.0.251952. Regular Standard only; no Mercenaries or Battlegrounds.','',
'Every remaining ID has one primary category. Counts are exact for this inventory; difficulty assignments are conservative planning estimates. This is a first-pass engineering review, not 519 completed card specifications or a guarantee that generated dependencies are closed.','',
'| Category | Cards | Meaning |','| --- | ---: | --- |']
for k in ('A','C','B','D'):summary.append(f'| {k}: {BUCKETS[k]} | {counts[k]} | '+{'A':'Mostly existing helpers; limited glue, fixed tokens and tests.','B':'Build or extend a shared mechanic, then attach and test the family.','C':'Often short definitions, but eligible generated results include missing behavior.','D':'Substantial lifecycle/action work, bespoke state, complex dependencies; includes 2 scope decisions.'}[k]+' |')
summary+=['',
'**Do not describe A + C as “139 easy cards ready now.”** The 127 generation-dependent cards are not currently completeable by swapping in a reduced pool. Some also need local glue. A pool service alone does not unlock them: every eligible generated effect and nested dependency must work.','',
'## Lower-risk candidates','', '| Card | Why it is a candidate |','| --- | --- |']
for r in rows:
 if r['bucket']=='A':summary.append(f"| {r['name']} (`{r['card_id']}`) | {r['card_specific_note']} |")
summary+=['','## Shared families, largest first','',
'These are exclusive primary-family counts, not additive estimates of everything each engine feature touches. A card can have several secondary dependencies. The generation, custom-state and setup groups are broad buckets, not single reusable mechanics.','',
'| Family | Primary cards | Category | Work needed |','| --- | ---: | --- | --- |']
for k,n in sorted(families.items(),key=lambda v:(-v[1],v[0])):
 g=GROUPS[k];summary.append(f"| {g['label']} | {n} | {g['bucket']} | {g['reason']} |")
summary+=['','## Practical development order','',
'1. Finish the 12 local candidates and their fixed tokens; they are the shortest bounded queue, not a complete 60-card batch by themselves.',
'2. Extend the relatively contained shared systems: held upgrades (7), type selection (5), physical origin tracking (10), and fixed Cannoneer/Leech families (2 + 3). Verify timing and generated tokens before counting each card.',
'3. Build family releases for Dormant (18), Imbue (19), Prepare (19), and Herald (15). Dark Gifts (19) also has strong reuse, but its full effect pool and Discover dependencies raise the completion risk.',
'4. Build forced combat (24), nested casting/replay (21), and draw-trigger resolution (16) as engine projects with interaction fixtures. These remove foundations blocking both simple-looking and complex cards.',
'5. Use exact generation-pool dependency inventories to prioritize missing results; progressively clear the 127 generation-dependent definitions as their dependencies become complete. Rewind, Shatter, custom builders, special deck setup and complex rewards remain separate work.',
'',
'This ordering aims for bounded progress and reuse. It is not a promise that each family alone yields its full count or that future releases must stop at a particular number. Continue consolidated deliveries and local validation; no Jupyter run is needed just to use this inventory.','',
'## Evidence and boundaries','',
'- Reviewed current `expanded/catalog_audit.json`, `implementation_index.json`, explicit rule tables and shared `game.py`, `systems.py`, `batch_effects.py`, `batch60.py`, `lifecycle.py`, `resolution.py`, `pools.py` and recorded fidelity gaps.',
'- `GenerationPool.resolve` refuses missing eligible effects. The engine has deck/private choices, but that is not a complete global Discover implementation.',
'- Nested card-effect frames are explicitly rejected. General Dormant, Prepare, Rewind, Imbue and Herald lifecycle support is not present in the current candidate.',
'- Spot-reviewed generated records in the pinned card archive; examples include the Cannoneer, Leech, Genn’s upgraded form, Dragon Egg and Coin Chest. Full token-chain review is still required for the complete backlog.',
'- No simulator code, implementation counts or validation receipts were changed. No training or engine checks were needed for this inventory.',
'',
'[All 519 cards, grouped](cards.md) · [Machine-readable classification](classification.json) · [Reproducible classifier](classify.py)','']
(OUT/'README.md').write_text('\n'.join(summary))
detail=['# All 519 remaining collectible cards','', 'See [classification method and summary](README.md). Each ID appears exactly once below. Secondary tags are review prompts and are not additional card counts.','']
for k in sorted(families,key=lambda k:(GROUPS[k]['bucket'],GROUPS[k]['label'])):
 g=GROUPS[k];detail += [f"## {g['label']} — {families[k]} cards ({g['bucket']})",'',g['reason'],'','| ID | Card | Printed rule | Additional note / review tags |','| --- | --- | --- | --- |']
 for r in rows:
  if r['primary_family']==k:
   clean=lambda text:text.replace('|','\\|')
   note=r['card_specific_note'] or ', '.join(r['secondary_review_tags']) or 'Review timing, generated dependencies and interactions.'
   detail.append(f"| `{r['card_id']}` | {clean(r['name'])} | {clean(r['text'])} | {clean(note)} |")
 detail.append('')
(OUT/'cards.md').write_text('\n'.join(detail))
print('Wrote 519 unique rows; bucket sum verified:',sum(counts.values()))

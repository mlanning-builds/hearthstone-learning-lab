"""Frozen Standard catalog, all-class browsing, and explicit simulation coverage.

Nothing in this module starts a match, trains a policy, or downloads data.
"""
from collections import Counter
from html import escape
import ast
import gzip
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'/'standard'
CLASSES=('DEATHKNIGHT','DEMONHUNTER','DRUID','HUNTER','MAGE','PALADIN','PRIEST','ROGUE','SHAMAN','WARLOCK','WARRIOR')


def verify_data():
    manifest=json.loads((DATA/'manifest.json').read_text())
    for filename,expected in manifest['files_sha256'].items():
        if Path(filename).name != filename: raise ValueError('Invalid manifest filename')
        actual=hashlib.sha256((DATA/filename).read_bytes()).hexdigest()
        if actual!=expected: raise ValueError('Catalog changed: '+filename+'. Rebuild its reviewed snapshot before using it.')
    return manifest


def load_catalog():
    manifest=verify_data()
    cards=json.loads((DATA/'cards.json').read_text())
    if len(cards)!=manifest['standard_catalog_count'] or len({c['id'] for c in cards})!=len(cards):
        raise ValueError('Catalog count or unique IDs failed verification')
    for c in cards:
        classes=c.get('classes') or [c.get('cardClass')]
        if not classes or any(k not in CLASSES+('NEUTRAL',) for k in classes):
            raise ValueError('Unrecognized class: '+c['id'])
    return cards


def load_classes():
    verify_data()
    return json.loads((DATA/'classes.json').read_text())


def load_all_records():
    """Reference data, including Wild and unreleased cards. NOT a legal generation pool."""
    verify_data()
    with gzip.open(DATA/'all_cards.json.gz','rt',encoding='utf-8') as source:
        return json.load(source)


def search_cards(cards, hero_class='ALL', query='', card_set='ALL', include_neutral=True):
    hero_class=hero_class.upper().replace(' ','').replace('_','')
    if hero_class not in CLASSES+('ALL','NEUTRAL'): raise ValueError('Choose ALL, NEUTRAL, or one of the 11 class names.')
    result=[]
    for c in cards:
        classes=c.get('classes') or [c.get('cardClass')]
        if hero_class!='ALL' and hero_class not in classes and not (include_neutral and hero_class!='NEUTRAL' and 'NEUTRAL' in classes): continue
        if card_set!='ALL' and c['set']!=card_set: continue
        if query.casefold() not in ' '.join(str(c.get(k,'')) for k in ('id','name','text','mechanics','runeCost')).casefold(): continue
        result.append(c)
    return sorted(result,key=lambda c:(c.get('cost',0),c['name'],c['id']))


def _legacy_supported():
    # Read declarations only. Avoid importing game code or starting a simulation.
    tree=ast.parse((ROOT/'engine'/'cards.py').read_text())
    for node in tree.body:
        if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='SUPPORTED' for t in node.targets):
            return ast.literal_eval(node.value)
    raise ValueError('Cannot inspect the existing engine support list')


def coverage_report(cards):
    supported=_legacy_supported()
    frozen={c['id']:c for c in json.loads((ROOT/'data'/'core_pool.json').read_text())}
    rows=[]
    for c in cards:
        if c['id'] not in supported: status='Effect not implemented'
        elif frozen.get(c['id'])!=c: status='Data changed; implementation needs review'
        else: status='Implemented in legacy DK subset; not full-Standard validated'
        rows.append({'id':c['id'],'name':c['name'],'classes':c.get('classes') or [c.get('cardClass')],'set':c['set'],'status':status})
    result = {'full_standard_ready':False,'catalog_cards':len(cards),'legacy_effects_matching_data':sum(r['status'].startswith('Implemented') for r in rows),'class_gameplay_ready':['DEATHKNIGHT'],'missing_class_gameplay':[k for k in CLASSES if k!='DEATHKNIGHT'],'cards':rows,'blockers':['Most card effects and their interactions are not implemented.','Ten additional class hero powers and class mechanics are not implemented.','Special deck construction, generated-card pools, and live legality need validation.','Full-engine conformance against Hearthstone has not been established.','The 395-weight subset policy cannot be reused as an all-card policy.']}

    index_path = ROOT/'expanded/implementation_index.json'
    if index_path.exists():
        index=json.loads(index_path.read_text())
        written=set(index['implemented_card_ids'])
        result['expanded_effects_written']=len(written)
        result['base_hero_powers_written']=index['base_hero_power_classes']
        result['expanded_validation']='Pending user-run notebook 06; written code is not certification.'
        for row in rows:
            if row['id'] in written:
                row['status']='Explicit expanded implementation written; see notebook 06 validation'
        result['blockers']=[
            str(len(cards)-len(written))+' catalog card effects are still missing.',
            'Base powers are written for all 11 classes; full class mechanics and interactions remain incomplete.',
            'Run notebook 06 for targeted fixtures; full-game conformance is still unverified.',
            'Special construction, live legality, generated pools, and the all-card learner remain unfinished.'
        ]
    return result


def require_full_simulator():
    raise RuntimeError('Full Standard simulation is not implemented. Notebook 05 loads the card book only. Importing card text cannot implement its effects; use the coverage report to track the remaining engine work.')


def show_overview(cards,classes,report):
    from IPython.display import HTML,display
    rows=[]
    for item in sorted(classes,key=lambda h:h['class']):
        k=item['class']; exclusive=len(search_cards(cards,k,include_neutral=False)); total=len(search_cards(cards,k))
        rows.append('<tr>'+''.join('<td>'+escape(str(x))+'</td>' for x in (k,item['hero']['name'],item['hero_power']['name'],exclusive,total,'Base power written; validation in 06' if k in report.get('base_hero_powers_written',[]) else 'DK subset only' if k=='DEATHKNIGHT' else 'Not implemented'))+'</tr>')
    display(HTML('<h3>All-class card book · September 18, 2026</h3><p>'+str(len(cards))+' collectible catalog entries. Multi-class cards count for every eligible class. Neutral cards are included in each class-accessible total. Rune and exceptional construction rules still restrict actual decks.</p><table><tr><th>Class</th><th>Default hero</th><th>Hero power</th><th>Class cards</th><th>With neutral</th><th>Gameplay support</th></tr>'+''.join(rows)+'</table>'))
    print('Full Standard simulation: NOT READY')
    print('Legacy effects with identical card data:',report['legacy_effects_matching_data'],'/',len(cards))
    if 'expanded_effects_written' in report: print('Expanded effects written (unverified):',report['expanded_effects_written'],'/',len(cards))
    for reason in report['blockers']: print('•',reason)
    print('\nSets:')
    for name,count in sorted(Counter(c['set'] for c in cards).items()): print(name,count)


def show_cards(cards,limit=100):
    from IPython.display import HTML,display
    if type(limit) is not int or limit<1: raise ValueError('limit must be positive')
    rows=[]
    for c in cards[:limit]:
        values=(c['name'],c['id'],', '.join(c.get('classes') or [c.get('cardClass','')]),c.get('cost',''),c['type'],c['set'],json.dumps(c.get('runeCost',{})),c.get('text',''))
        rows.append('<tr>'+''.join('<td style="vertical-align:top;white-space:pre-wrap">'+escape(str(v))+'</td>' for v in values)+'</tr>')
    display(HTML(f'<p>Showing {min(limit,len(cards)):,} of {len(cards):,} matching cards.</p><div style="max-height:650px;overflow:auto"><table><tr><th>Name</th><th>ID</th><th>Class</th><th>Mana</th><th>Type</th><th>Set</th><th>Runes</th><th>Rules text</th></tr>'+''.join(rows)+'</table></div>'))

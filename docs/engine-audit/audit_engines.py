"""Read-only source audit: never imports/builds a simulator or runs its tests."""
import argparse, ast, collections, gzip, hashlib, json, re, subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

def revision(path):
    return subprocess.check_output(['git','-C',str(path),'rev-parse','HEAD'],text=True).strip()

def normalize(text):
    return re.sub(r'\s+',' ',re.sub(r'<[^>]+>|\[x\]|[$#]','',text)).strip()

def fireplace_definitions(root):
    result={}
    for path in sorted((root/'fireplace/cards').rglob('*.py')):
        if any(part in ('custom','debug','brawl','tutorial','skins') for part in path.relative_to(root/'fireplace/cards').parts):
            continue
        for node in ast.parse(path.read_text()).body:
            names=[]
            if isinstance(node,ast.ClassDef):
                # Docstring-only/pass classes do not implement executable effects.
                body=[n for n in node.body if not isinstance(n,ast.Pass) and
                      not (isinstance(n,ast.Expr) and isinstance(n.value,ast.Constant) and isinstance(n.value.value,str))]
                if body:names=[node.name]
            elif isinstance(node,ast.Assign):
                names=[n.id for n in node.targets if isinstance(n,ast.Name)]
            for name in names:
                if re.match(r'^[A-Z][A-Za-z0-9]*_[A-Za-z0-9_]+$',name):
                    result[name]=dict(path=str(path.relative_to(root)),line=node.lineno)
    return result

def rosetta_definitions(root):
    result={}
    for path in sorted((root/'Sources/Rosetta/PlayMode/CardSets').glob('*.cpp')):
        source=path.read_text()
        # Strip comments preserving line numbers: comments aren't implementations.
        source=re.sub(r'/\*.*?\*/',lambda m:'\n'*m.group().count('\n'),source,flags=re.S)
        source=re.sub(r'//[^\n]*','',source)
        for m in re.finditer(r'cards\.emplace\(\s*"([^"]+)"\s*,\s*cardDef\s*\)',source):
            result.setdefault(m.group(1),dict(path=str(path.relative_to(root)),line=source[:m.start()].count('\n')+1))
    return result

def fireplace_metadata(path):
    result={}
    for _,entity in ET.iterparse(path,events=('end',)):
        if entity.tag!='Entity':continue
        tags={t.get('name'):t for t in entity.findall('Tag')}
        def loc(name):
            t=tags.get(name)
            return t.findtext('enUS','') if t is not None else ''
        c=dict(id=entity.get('CardID'),name=loc('CARDNAME'),text=loc('CARDTEXT') or loc('CARDTEXT_INHAND'))
        for field,tag in [('cost','COST'),('attack','ATK'),('health','HEALTH'),('durability','DURABILITY')]:
            t=tags.get(tag)
            if t is not None and t.get('value') is not None:c[field]=int(t.get('value'))
        result[c['id']]=c;entity.clear()
    return result

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--project',type=Path,required=True)
    ap.add_argument('--fireplace',type=Path,required=True)
    ap.add_argument('--rosetta',type=Path,required=True)
    ap.add_argument('--fireplace-carddefs',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    catalog_path=args.project/'data/standard/cards.json'
    catalog=json.loads(catalog_path.read_text())
    with gzip.open(args.project/'data/standard/all_cards.json.gz','rt') as f:archive=json.load(f)
    by_dbf={c['dbfId']:c for c in archive if 'dbfId' in c}
    by_id={c['id']:c for c in archive}
    fp=fireplace_definitions(args.fireplace);rs=rosetta_definitions(args.rosetta)
    fpdata=fireplace_metadata(args.fireplace_carddefs)
    rsdata={c['id']:c for c in json.loads((args.rosetta/'Resources/cards.json').read_text())}
    existing=set(json.loads((args.project/'expanded/implementation_index.json').read_text())['implemented_card_ids'])
    rows=[]
    for c in catalog:
        row=dict(id=c['id'],name=c['name'],card_set=c['set'],classes=c.get('classes') or [c.get('cardClass')],local_written=c['id'] in existing)
        for engine,definitions,metadata in [('fireplace',fp,fpdata),('rosetta',rs,rsdata)]:
            candidates=[(c['id'],'exact_id')]
            canonical=by_dbf.get(c.get('countAsCopyOfDbfId'))
            if canonical and canonical['id']!=c['id']:candidates.append((canonical['id'],'copy_equivalent_id'))
            base=re.sub(r'^core_','',c['id'],flags=re.I)
            if base!=c['id'] and base in by_id and by_id[base].get('name')==c['name']:
                candidates.append((base,'core_prefix_same_name'))
            matches=[]
            for cid,kind in candidates:
                if cid in definitions and not any(x['id']==cid for x in matches):
                    old=metadata.get(cid);differences=[]
                    if old:
                        for field in ('cost','attack','health','durability'):
                            if field in c and c.get(field)!=old.get(field):differences.append(field)
                        if normalize(c.get('text',''))!=normalize(old.get('text','')):differences.append('rules_text')
                    matches.append(dict(id=cid,match=kind,**definitions[cid],
                                        metadata_available=bool(old),metadata_differences=differences))
            row[engine]=matches
        rows.append(row)
    summary={}
    for engine in ('fireplace','rosetta'):
        matches=[r for r in rows if r[engine]]
        summary[engine]=dict(
            candidate_records=len(matches),
            exact_id_records=sum(any(x['match']=='exact_id' for x in r[engine]) for r in matches),
            alias_only_records=sum(not any(x['match']=='exact_id' for x in r[engine]) for r in matches),
            no_source_candidate=len(rows)-len(matches),
            candidates_not_written_locally=sum(not r['local_written'] for r in matches),
            preferred_candidate_metadata_differs=sum(bool(r[engine][0]['metadata_differences']) for r in matches),
            by_set=dict(collections.Counter(r['card_set'] for r in matches)),
            death_knight_candidate_records=sum('DEATHKNIGHT' in r['classes'] for r in matches))
    report=dict(
        scope='Static source candidates, NOT playable-card coverage or verified current rules. No simulator code executed.',
        catalog_sha256=hashlib.sha256(catalog_path.read_bytes()).hexdigest(),
        catalog_count=len(rows),local_written=len(existing),
        revisions=dict(fireplace=revision(args.fireplace),rosetta=revision(args.rosetta)),
        fireplace_carddefs_sha256=hashlib.sha256(args.fireplace_carddefs.read_bytes()).hexdigest(),
        method='Fireplace top-level executable card classes/assignments; RosettaStone uncommented cards.emplace registrations. Match exact IDs, explicit copy-equivalence, then same-name CORE aliases. No transitive token closure, runtime loading, tag-only support, or behavioral conformance inferred.',
        summary=summary,cards=rows)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='cards'},indent=2))
if __name__=='__main__':main()

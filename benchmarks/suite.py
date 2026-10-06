"""Visible-information opponents and balanced four-game evaluation blocks."""
import hashlib
import json
import math
import random
from pathlib import Path
from engine.cards import registry, supported_pool
from engine.game import Action, Game
from engine.experiment import random_policy
from lab import population
from learner.policy import Policy
from learner.training import fingerprint, save_json

ROOT = Path(__file__).resolve().parents[1]

class RulesPolicy:
    """Simple hand-written challengers, not expert or optimal players."""
    def __init__(self, style):
        if style not in ('aggressive', 'trading'): raise ValueError(style)
        self.style = style
        self.cards = registry()

    def choose(self, obs, rng, learn=False):
        if learn: raise ValueError('Benchmark opponents cannot learn.')
        v = obs['viewer']; own = obs['players'][v]; enemy = obs['players'][1-v]
        hand = {c['uid']: c for c in own['hand']}
        board = {m['uid']: m for p in obs['players'] for m in p['board']}
        def score(a):
            kind = a['kind']; target = a['target']
            if kind == 'mulligan':
                wanted = {uid for uid,c in hand.items() if self.cards[c['card_id']]['cost'] > 3}
                return -len(wanted.symmetric_difference(a['choices'])) * 100
            if kind == 'end': return -100
            if kind == 'power': return 2
            if kind == 'attack':
                source = board.get(a['source'])
                atk = source['attack'] if source else own['weapon']['attack']
                if target < 0:
                    if atk >= enemy['health'] + enemy['armor']: return 10000
                    return atk * (4 if self.style == 'aggressive' else 1)
                t = board[target]
                kill = 'DIVINE_SHIELD' not in t['keywords'] and (atk >= t['health'] or (source and 'POISONOUS' in source['keywords']))
                dies = source and 'DIVINE_SHIELD' not in source['keywords'] and (t['attack'] >= source['health'] or ('POISONOUS' in t['keywords'] and t['attack'] > 0))
                value = (t['attack'] + t['health']/2) if kill else min(atk,t['health'])/2
                loss = (source['attack'] + source['health']/2) if dies else 0
                return value * (2 if self.style == 'trading' else 1) - loss + 1
            c = hand[a['source']]; d = self.cards[c['card_id']]; cid = c['card_id']
            value = 3 + d['cost']*.4
            if d['type'] == 'MINION': value += (d.get('attack',0)+c['attack_bonus'] + d.get('health',0)+c['health_bonus'])/2
            # Targeting rules are explicit; no access to hidden hands or shuffled decks.
            damage = {'CORE_CS2_189':1, 'CORE_UNG_084':2, 'RLK_024':6}.get(cid)
            if damage and target:
                hostile = target == -2+v or (target > 0 and board[target]['owner'] != v)
                if not hostile: return -90
                if target < 0:
                    if damage >= enemy['health'] + enemy['armor']: return 10000
                    value += damage * (3 if self.style == 'aggressive' else 1)
                else:
                    t = board[target]
                    value += min(damage,t['health']) + (t['attack'] if damage >= t['health'] and 'DIVINE_SHIELD' not in t['keywords'] else 0)
            if cid == 'CORE_EX1_011' and target:
                friendly = target == -v-1 or (target > 0 and board[target]['owner'] == v)
                if not friendly: value -= 15
                else: value += min(2,30-own['health'] if target < 0 else board[target]['max_health']-board[target]['health'])
            if cid in ('RLK_048','RLK_707'): value += len(own['board'])*2 if own['board'] else -20
            if cid in ('CORE_RLK_087','RLK_709'): value += len(enemy['board'])*2 if enemy['board'] else -20
            if cid == 'CORE_RLK_712': value += sum(self.cards[x['card_id']]['type']=='MINION' for x in hand.values())*2-4
            if cid == 'TOKEN_COIN':
                usable = any(self.cards[x['card_id']]['cost']==own['mana']+1 for x in hand.values())
                value = 20 if usable else -90
            return value
        actions = obs['legal_actions']; values = [score(a) for a in actions]
        best = max(values)
        data = dict(rng.choice([a for a,s in zip(actions,values) if s == best]))
        data['choices'] = tuple(data['choices'])
        return Action(**data), None, None


def load_model(path=None):
    files = list((ROOT/'runs').glob('training_*/model_*.json'))
    if path is None:
        if not files: raise FileNotFoundError('Run notebook 03 first to save a trained model.')
        path = max(files, key=lambda p:p.stat().st_mtime)
    path = Path(path); data = json.loads(path.read_text())
    if data['config']['fingerprint'] != fingerprint():
        raise ValueError('This model was trained with different code or cards. Use its original environment.')
    checkpoint = json.loads((path.parent/'checkpoint.json').read_text())
    return path, data, Policy.restore(data['policy']), Policy.restore(checkpoint['initial'])


def match(policy, opponent, pair, seed, first):
    game = Game([d['cards'] for d in pair], [tuple(d['runes'].values()) for d in pair], seed=seed, first_player=first, record=False)
    rngs = [random.Random(seed+101), random.Random(seed+202)]
    while not game.terminal:
        if len(game.history)>=10000: raise RuntimeError('Action limit reached')
        v=game.current; obs=game.observe(v,include_events=False)
        actor=policy if v==0 else opponent
        action=random_policy(obs,rngs[v]) if actor is None else actor.choose(obs,rngs[v])[0]
        game.step(action)
    return dict(reward=game.rewards()[0], turns=game.turn, reason=game.end_reason, first=first)


def run_suite(model_path=None, games_per_opponent=200, seed=20260918, progress=None, output_dir=None):
    if type(games_per_opponent) is not int or games_per_opponent<4 or games_per_opponent%4:
        raise ValueError('games_per_opponent must be a positive multiple of 4.')
    if type(seed) is not int or seed<0: raise ValueError('seed must be a nonnegative integer.')
    path,data,policy,initial=load_model(model_path)
    opponents=[('Random',None),('Initial model',initial),('Aggressive rules',RulesPolicy('aggressive')),('Trading rules',RulesPolicy('trading'))]
    config=dict(model_sha256=hashlib.sha256(path.read_bytes()).hexdigest(), environment=fingerprint(), benchmark_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),games_per_opponent=games_per_opponent,seed=seed)
    folder=Path(output_dir or ROOT/'runs')/('benchmark_'+hashlib.sha256(json.dumps(config,sort_keys=True).encode()).hexdigest()[:12]); folder.mkdir(parents=True,exist_ok=True)
    output=folder/'results.json'
    state=json.loads(output.read_text()) if output.exists() else dict(config=config,model=str(path),trained_games=data['trained_games'],matches={},summaries={})
    total=len(opponents)*games_per_opponent
    for name,opponent in opponents:
        results=state['matches'].setdefault(name,[])
        for i in range(len(results),games_per_opponent):
            block=i//4; slot=i%4
            # Independent block seeds, same schedule across opponents for comparison.
            decks=population(supported_pool(),per_profile=2,seed=seed+80000000+block)
            pair=random.Random(seed+block).sample(decks,2)
            if slot>=2: pair=pair[::-1]
            result=match(policy,opponent,pair,seed+90000000+block,slot%2)
            results.append(result); save_json(output,state)
            if progress: progress(sum(len(x) for x in state['matches'].values()),total,name)
        n=len(results); wins=sum(r['reward']==1 for r in results); draws=sum(r['reward']==0 for r in results)
        # Independent blocks; four games inside a block may be correlated.
        # Bonferroni adjustment covers all four reported win-rate intervals jointly.
        radius=math.sqrt(math.log(2*len(opponents)/.05)/(2*(n//4)))
        state['summaries'][name]=dict(games=n,wins=wins,losses=n-wins-draws,draws=draws,win_rate=wins/n,score=(wins+.5*draws)/n,interval=[max(0,wins/n-radius),min(1,wins/n+radius)],first_win_rate=sum(r['reward']==1 and r['first']==0 for r in results)/(n/2),second_win_rate=sum(r['reward']==1 and r['first']==1 for r in results)/(n/2),turn_limit_games=sum(r['reason']=='turn_limit' for r in results))
        save_json(output,state)
    if progress: progress(total,total,'Complete')
    return state,output


def show_results(state):
    from IPython.display import HTML,display
    from html import escape
    rows=[]
    for name,s in state['summaries'].items():
        lo,hi=s['interval']
        rows.append(f'<tr><td>{escape(name)}</td><td>{s["wins"]}/{s["games"]}</td><td>{s["draws"]}</td><td>{s["win_rate"]:.1%}</td><td>{lo:.0%}–{hi:.0%}</td><td>{s["first_win_rate"]:.1%}</td><td>{s["second_win_rate"]:.1%}</td></tr>')
    display(HTML('<table><tr><th>Opponent</th><th>Wins</th><th>Draws</th><th>Win rate</th><th>Conservative bounds</th><th>Going first</th><th>Going second</th></tr>'+''.join(rows)+'</table>'))
    print('95% simultaneous bounds across four opponents, accounting for four-game blocks. Wide bounds mean more games are needed.')
    print('Rule-based opponents are challengers, not verified expert players. These results measure this 33-card simulator, not Standard.')

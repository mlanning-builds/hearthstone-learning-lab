"""Small linear softmax policy trained with episodic REINFORCE.

No third-party numerical dependency, expert moves, rollout search, or pretrained
weights. Features describe visible state/action facts; all preferences are learned.
"""
import math
import random
from engine.game import Action
from engine.cards import registry

KINDS = ('end', 'play', 'attack', 'power', 'mulligan')
CONTEXT = ('bias', 'mana', 'own_health', 'enemy_health', 'own_board', 'enemy_board',
           'own_attack', 'enemy_attack', 'hand_count', 'corpses', 'deck_count',
           'blood', 'frost', 'unholy')
PROPERTIES = ('cost', 'source_attack', 'source_health', 'source_is_hero',
              'target_enemy_hero', 'target_own_hero', 'target_enemy_minion', 'target_own_minion',
              'target_attack', 'target_health', 'target_missing_health', 'target_shield',
              'target_taunt', 'source_shield', 'source_poisonous', 'source_lifesteal',
              'source_rush', 'position', 'mulligan_count', 'mulligan_cost',
              'enemy_hero_attack', 'own_hero_attack', 'enemy_minion_attack', 'own_minion_attack',
              'enemy_minion_health', 'own_minion_health', 'source_target_attack_product',
              'source_target_health_product')
CARD_IDS = tuple(sorted(registry()))
FEATURE_NAMES = tuple(f'{kind}:{name}' for kind in KINDS for name in CONTEXT) + \
                tuple(f'{kind}:{name}' for kind in KINDS for name in PROPERTIES) + \
                tuple(f'card:{cid}:{relation}' for cid in CARD_IDS
                      for relation in ('played','enemy_hero','own_hero','enemy_minion','own_minion'))
INDEX = {name:i for i,name in enumerate(FEATURE_NAMES)}


def encode(observation, cards):
    """Only reads the observation and public card definitions, never Game."""
    viewer = observation['viewer']
    own = observation['players'][viewer]
    enemy = observation['players'][1-viewer]
    hand = {c['uid']:c for c in own['hand']}
    minions = {m['uid']:m for p in observation['players'] for m in p['board']}
    context = [1, own['mana']/10, own['health']/30, enemy['health']/30,
               len(own['board'])/7, len(enemy['board'])/7,
               sum(m['attack'] for m in own['board'])/30,
               sum(m['attack'] for m in enemy['board'])/30,
               own['hand_count']/10, min(own['corpses'],20)/20,
               own['deck_count']/30] + [n/3 for n in own['runes']]
    vectors=[]
    for action in observation['legal_actions']:
        kind=action['kind']; pairs=[]
        def add(name,value):
            if value: pairs.append((INDEX[name],float(value)))
        for name,value in zip(CONTEXT,context): add(kind+':'+name,value)
        properties={}
        source=action['source']; target=action['target']
        card_id=None; attack=health=0; keywords=()
        if kind=='play':
            card=hand[source]; card_id=card['card_id']; data=cards[card_id]
            attack=data.get('attack',0)+card['attack_bonus']
            health=data.get('health',0)+card['health_bonus']
            keywords=data.get('mechanics',[])
            properties['cost']=data['cost']/10
        elif kind=='attack':
            if source<0:
                attack=own['weapon']['attack']; health=own['health']; keywords=('LIFESTEAL',)
                properties['source_is_hero']=1
            else:
                m=minions[source]; attack=m['attack']; health=m['health']; keywords=m['keywords']
        properties.update(source_attack=attack/10,source_health=health/10)
        for feature,key in [('source_shield','DIVINE_SHIELD'),('source_poisonous','POISONOUS'),
                            ('source_lifesteal','LIFESTEAL'),('source_rush','RUSH')]:
            properties[feature]=int(key in keywords)
        relation=None
        if target<0:
            relation='own_hero' if -target-1==viewer else 'enemy_hero'
            target_player=own if relation=='own_hero' else enemy
            properties['target_health']=target_player['health']/30
            properties['target_missing_health']=(30-target_player['health'])/30
            properties[relation+'_attack']=attack/10
        elif target>0:
            m=minions[target]; relation='own_minion' if m['owner']==viewer else 'enemy_minion'
            properties.update(target_attack=m['attack']/10,target_health=m['health']/10,
                              target_missing_health=(m['max_health']-m['health'])/10,
                              target_shield=int('DIVINE_SHIELD' in m['keywords']),
                              target_taunt=int('TAUNT' in m['keywords']))
            properties[relation+'_attack']=m['attack']/10
            properties[relation+'_health']=m['health']/10
            properties['source_target_attack_product']=attack*m['attack']/100
            properties['source_target_health_product']=attack*m['health']/100
        if relation:
            properties['target_'+relation]=1
        if action['position']>=0: properties['position']=action['position']/7
        if kind=='mulligan':
            properties['mulligan_count']=len(action['choices'])/4
            properties['mulligan_cost']=sum(cards[hand[uid]['card_id']]['cost'] for uid in action['choices'])/40
        for name,value in properties.items(): add(kind+':'+name,value)
        if card_id:
            add('card:'+card_id+':played',1)
            if relation: add('card:'+card_id+':'+relation,1)
        vectors.append(pairs)
    return vectors


def probabilities(weights,vectors):
    scores=[sum(weights[i]*x for i,x in vector) for vector in vectors]
    maximum=max(scores)
    values=[math.exp(s-maximum) for s in scores]
    total=sum(values)
    return [v/total for v in values]


def log_gradient(vectors,probs,selected,entropy=0.0):
    """Analytic log pi(a|s) gradient plus entropy bonus gradient."""
    gradient=[0.0]*len(FEATURE_NAMES)
    h=-sum(p*math.log(p) for p in probs if p>0)
    for vector,p in zip(vectors,probs):
        coefficient=-p
        if entropy and p>0: coefficient-=entropy*p*(math.log(p)+h)
        for i,x in vector: gradient[i]+=coefficient*x
    for i,x in vectors[selected]: gradient[i]+=x
    return gradient


class Policy:
    VERSION='linear-softmax-reinforce-v1'

    def __init__(self,seed=42,weights=None):
        rng=random.Random(seed)
        self.weights=list(weights) if weights is not None else [rng.gauss(0,0.01) for _ in FEATURE_NAMES]
        if len(self.weights)!=len(FEATURE_NAMES) or not all(math.isfinite(v) for v in self.weights):
            raise ValueError('Invalid policy weights.')
        self.cards=registry()

    def distribution(self,observation):
        vectors=encode(observation,self.cards)
        return vectors,probabilities(self.weights,vectors)

    def choose(self,observation,rng,learn=False):
        vectors,probs=self.distribution(observation)
        threshold=rng.random(); cumulative=0.0; selected=len(probs)-1
        for i,p in enumerate(probs):
            cumulative+=p
            if threshold<cumulative:
                selected=i; break
        data=dict(observation['legal_actions'][selected]); data['choices']=tuple(data['choices'])
        gradient=log_gradient(vectors,probs,selected) if learn else None
        # Entropy regularizer is separate: it must NOT be multiplied by return.
        entropy_gradient=None
        if learn:
            with_entropy=log_gradient(vectors,probs,selected,entropy=1.0)
            entropy_gradient=[a-b for a,b in zip(with_entropy,gradient)]
        return Action(**data),gradient,entropy_gradient

    def export(self):
        return dict(version=self.VERSION,features=list(FEATURE_NAMES),weights=list(self.weights))

    @classmethod
    def restore(cls,data):
        if data['version']!=cls.VERSION or data['features']!=list(FEATURE_NAMES):
            raise ValueError('Policy format or feature schema changed.')
        return cls(weights=data['weights'])


class Adam:
    def __init__(self,size):
        self.m=[0.0]*size; self.v=[0.0]*size; self.steps=0

    def update(self,policy,gradient,rate):
        if not all(math.isfinite(x) for x in gradient):
            raise ValueError('Non-finite gradient; refusing to update.')
        norm=math.sqrt(sum(x*x for x in gradient)); scale=min(1.0,5.0/max(norm,1e-12))
        self.steps+=1
        for i,g in enumerate(gradient):
            g*=scale
            self.m[i]=0.9*self.m[i]+0.1*g
            self.v[i]=0.999*self.v[i]+0.001*g*g
            mhat=self.m[i]/(1-0.9**self.steps); vhat=self.v[i]/(1-0.999**self.steps)
            policy.weights[i]+=rate*mhat/(math.sqrt(vhat)+1e-8)

    def export(self): return dict(m=self.m.copy(),v=self.v.copy(),steps=self.steps)

    @classmethod
    def restore(cls,data):
        obj=cls(len(FEATURE_NAMES)); obj.m=list(data['m']); obj.v=list(data['v']); obj.steps=data['steps']
        if len(obj.m)!=len(FEATURE_NAMES) or len(obj.v)!=len(FEATURE_NAMES):
            raise ValueError('Optimizer schema changed.')
        if any(not math.isfinite(v) for v in obj.m+obj.v) or any(v<0 for v in obj.v):
            raise ValueError('Invalid optimizer values.')
        return obj

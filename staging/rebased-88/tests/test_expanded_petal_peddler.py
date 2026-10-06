import unittest
from expanded import Game,Action,random_deck

class PetalPeddlerTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('DRUID',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        for p in self.g.players:p.hand=[];p.deck=['CORE_CS2_029']*10;p.mana=p.max_mana=10
    def test_only_another_friendly_dragon(self):
        source=self.g._summon(0,'EDR_889');dragon=self.g._summon(0,'TLC_888')
        other=self.g._summon(0,'CS3_025');enemy=self.g._summon(1,'TLC_888')
        before=[(m.attack,m.health) for m in (source,dragon,other,enemy)]
        self.g.step(Action('end'))
        self.assertEqual([(m.attack,m.health) for m in (source,dragon,other,enemy)],
                         [before[0],(before[1][0]+1,before[1][1]+1),before[2],before[3]])
    def test_lone_source_does_not_buff_itself(self):
        source=self.g._summon(0,'EDR_889');self.g.step(Action('end'))
        self.assertEqual((source.attack,source.health),(1,4))
    def test_silence_and_opponent_turn_do_not_trigger(self):
        source=self.g._summon(0,'EDR_889');dragon=self.g._summon(0,'TLC_888');before=dragon.attack
        self.g._silence(source);self.g.step(Action('end'));self.assertEqual(dragon.attack,before)
        self.g._summon(0,'EDR_889');self.g.step(Action('end'));self.assertEqual(dragon.attack,before)
    def test_all_tribe_is_eligible(self):
        self.g._summon(0,'EDR_889');m=self.g._summon(0,'DINO_435');before=(m.attack,m.health)
        self.g.step(Action('end'));self.assertEqual((m.attack,m.health),(before[0]+1,before[1]+1))
    def test_multiple_peddlers_buff_each_other(self):
        a=self.g._summon(0,'EDR_889');b=self.g._summon(0,'EDR_889');self.g.step(Action('end'))
        self.assertEqual([(m.attack,m.health) for m in (a,b)],[(2,5),(2,5)])
    def test_exactly_one_eligible_target_per_trigger(self):
        self.g._summon(0,'EDR_889');ms=[self.g._summon(0,'TLC_888') for _ in range(3)]
        before=[m.attack for m in ms];self.g.step(Action('end'))
        self.assertEqual(sorted(m.attack-a for m,a in zip(ms,before)),[0,0,1])

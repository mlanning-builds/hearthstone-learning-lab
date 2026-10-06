import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class SpecterTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('PRIEST',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p=self.g.players[0];self.p.hand=[];self.p.mana=self.p.max_mana=10
    def play(self,target=0):
        c=Card(self.g._new_id(),'CAP_804');self.p.hand.append(c)
        self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==target))
    def test_grants_reborn_without_copy(self):
        m=self.g._summon(0,'CORE_EX1_506');self.play(m.uid)
        self.assertIn('REBORN',m.keywords);self.assertEqual(len(self.p.minions),2)
    def test_existing_reborn_copies_modified_state(self):
        m=self.g._summon(0,'CORE_RLK_745');self.g._buff(m,2,2);m.health-=1;self.play(m.uid)
        copies=[x for x in self.p.minions if x.card_id==m.card_id]
        self.assertEqual(len(copies),2)
        self.assertEqual([(x.attack,x.health,x.max_health) for x in copies],[(4,5,6)]*2)
        self.assertTrue(all('REBORN' in x.keywords for x in copies))
    def test_empty_board_allows_untargeted_play(self):
        self.play();self.assertEqual(len(self.p.minions),1)
    def test_granted_reborn_triggers_normally(self):
        m=self.g._summon(0,'CORE_EX1_506');self.play(m.uid);m.health=0;self.g._settle()
        reborn=next(x for x in self.p.minions if x.card_id=='CORE_EX1_506')
        self.assertEqual(reborn.health,1);self.assertNotIn('REBORN',reborn.keywords)
    def test_full_board_prevents_copy(self):
        m=self.g._summon(0,'CORE_RLK_745')
        for _ in range(5):self.g._summon(0,'CORE_EX1_506')
        self.play(m.uid);self.assertEqual(len(self.p.minions),7)
    def test_copy_does_not_replay_battlecry(self):
        m=self.g._summon(0,'TIME_703');m.keywords.add('REBORN');self.p.health=5;self.play(m.uid)
        copies=[x for x in self.p.minions if x.card_id=='TIME_703']
        self.assertEqual(len(copies),2);self.assertEqual([x.attack for x in copies],[5,5])

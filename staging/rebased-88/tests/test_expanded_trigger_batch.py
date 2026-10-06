import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class TriggerBatchTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('WARRIOR',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        for p in self.g.players:p.hand=[];p.deck=['CORE_CS2_029']*30;p.mana=p.max_mana=10
    def play(self,cid,target=0,attack=0):
        c=Card(self.g._new_id(),cid);c.attack_bonus=attack;self.p.hand.append(c)
        self.g.step(Action('play',c.uid,target,len(self.p.board) if self.g.cards[cid]['type']=='MINION' else -1))
    def test_crater_copies_hand_buff_without_repeating_kindred(self):
        self.p.previous_tribes={'MURLOC'};self.play('DINO_435',attack=2)
        self.assertEqual(len(self.p.minions),2)
        self.assertEqual([m.attack for m in self.p.minions],[5,5])
        self.assertNotEqual(self.p.minions[0].uid,self.p.minions[1].uid)
    def test_crater_does_not_match_previous_spell_school(self):
        self.p.previous_schools={'FIRE'};self.play('DINO_435')
        self.assertEqual(len(self.p.minions),1)
    def test_broll_summons_companion_after_spell(self):
        self.g._summon(0,'EDR_853');self.play('CORE_CS2_029',self.g.hero_id(1))
        self.assertEqual(self.q.health,24)
        self.assertEqual(len(self.p.minions),2)
        self.assertIn(self.p.minions[-1].card_id,{'NEW1_032','NEW1_033','NEW1_034'})
    def test_dead_broll_does_not_trigger_from_killing_spell(self):
        m=self.g._summon(0,'EDR_853');self.play('CORE_CS2_029',m.uid)
        self.assertEqual(self.p.minions,[])
    def test_tower_creates_two_expiring_ghouls(self):
        m=self.g._summon(0,'JAIL_440');self.g._damage(m.uid,1);self.g._settle()
        self.assertEqual([x.card_id for x in self.p.minions],[ 'JAIL_440','HERO_11bpt','HERO_11bpt'])
        self.assertTrue(all(x.expires for x in self.p.minions[1:]))
        self.g.step(Action('end'));self.assertEqual(len(self.p.minions),1)
    def test_tower_divine_shield_and_silence_prevent_trigger(self):
        m=self.g._summon(0,'JAIL_440');m.keywords.add('DIVINE_SHIELD')
        self.g._damage(m.uid,1);self.g._settle();self.assertEqual(len(self.p.minions),1)
        self.g._silence(m);self.g._damage(m.uid,1);self.g._settle()
        self.assertEqual(len(self.p.minions),1)

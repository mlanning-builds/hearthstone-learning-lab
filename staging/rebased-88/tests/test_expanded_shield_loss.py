import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class ShieldLossTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('PALADIN',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        for p in self.g.players:p.hand=[];p.deck=['CORE_CS2_029']*10;p.mana=p.max_mana=10
        self.source=self.g._summon(0,'CORE_SW_047')
    def card(self,cid='CS3_025',owner=0):
        c=Card(self.g._new_id(),cid);self.g.players[owner].hand.append(c);return c
    def hit(self,m,amount=1):
        self.g._damage(m.uid,amount);self.g._settle()
    def test_own_shield_buffs_minion_not_spell(self):
        m=self.card();s=self.card('CORE_CS2_029');self.hit(self.source)
        self.assertEqual((m.attack_bonus,m.health_bonus,s.attack_bonus),(5,5,0));self.assertEqual(self.source.health,5)
    def test_other_friendly_shield_and_opponent_turn(self):
        c=self.card();m=self.g._summon(0,'CS3_025');m.keywords.add('DIVINE_SHIELD')
        self.g.step(Action('end'));self.hit(m);self.assertEqual(c.attack_bonus,5)
    def test_enemy_shield_does_not_trigger(self):
        c=self.card();m=self.g._summon(1,'CS3_025');m.keywords.add('DIVINE_SHIELD');self.hit(m)
        self.assertEqual(c.attack_bonus,0)
    def test_immune_and_zero_damage_leave_shield_and_no_buff(self):
        c=self.card();self.hit(self.source,0);self.source.keywords.add('IMMUNE');self.hit(self.source)
        self.assertIn('DIVINE_SHIELD',self.source.keywords);self.assertEqual(c.attack_bonus,0)
    def test_silence_does_not_trigger(self):
        c=self.card();self.g._silence(self.source);self.g._settle();self.assertEqual(c.attack_bonus,0)
        m=self.g._summon(0,'CS3_025');m.keywords.add('DIVINE_SHIELD');self.hit(m);self.assertEqual(c.attack_bonus,0)
    def test_two_sources_and_restored_shield(self):
        c=self.card();self.g._summon(0,'CORE_SW_047');self.hit(self.source)
        self.assertEqual(c.attack_bonus,10);self.source.keywords.add('DIVINE_SHIELD');self.hit(self.source)
        self.assertEqual(c.attack_bonus,20)
    def test_empty_or_spell_only_hand_is_noop(self):
        self.hit(self.source);self.source.keywords.add('DIVINE_SHIELD');c=self.card('CORE_CS2_029');self.hit(self.source)
        self.assertEqual(c.attack_bonus,0)
    def test_one_random_physical_card_and_bonus_survives_play(self):
        cs=[self.card() for _ in range(2)];self.hit(self.source)
        self.assertEqual(sorted(c.attack_bonus for c in cs),[0,5]);buffed=next(c for c in cs if c.attack_bonus)
        self.g.step(Action('play',buffed.uid,position=1));m=self.p.minions[1]
        self.assertEqual((m.attack,m.health),(8,11))

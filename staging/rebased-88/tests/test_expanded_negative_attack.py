import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class NegativeAttackTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('DRUID',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        for p in self.g.players:p.hand=[];p.deck=['CORE_CS2_029']*10;p.mana=p.max_mana=10
    def hand(self,owner,cid):
        c=Card(self.g._new_id(),cid);self.g.players[owner].hand.append(c);return c
    def kill(self,silence=False):
        m=self.g._summon(0,'EDR_495')
        if silence:self.g._silence(m)
        m.health=0;self.g._settle()
    def test_both_hands_minions_only_and_private(self):
        a=self.hand(0,'CORE_WON_351');b=self.hand(1,'CORE_WON_351');spell=self.hand(1,'CORE_CS2_029')
        self.kill();self.assertEqual((a.attack_bonus,b.attack_bonus,spell.attack_bonus),(-2,-2,0))
        self.assertNotIn('hand',self.g.observe(0)['players'][1])
    def test_empty_and_silenced(self):
        self.kill();a=self.hand(0,'CORE_WON_351');self.kill(silence=True);self.assertEqual(a.attack_bonus,0)
    def test_one_physical_copy_per_hand(self):
        cards=[self.hand(0,'CORE_WON_351') for _ in range(3)]
        self.kill();self.assertEqual(sorted(c.attack_bonus for c in cards),[-2,0,0])
    def test_play_retains_deficit_and_later_buff_pays_it_off(self):
        c=self.hand(0,'CORE_WON_351');self.kill()
        self.g.step(Action('play',c.uid,position=0));m=self.p.minions[0]
        self.assertEqual((m.attack,m.attack_deficit),(0,-1));self.g._buff(m,1,0)
        self.assertEqual((m.attack,m.attack_deficit),(0,0));self.g._buff(m,1,0);self.assertEqual(m.attack,1)
    def test_aura_add_remove_preserves_deficit(self):
        m=self.g._summon(0,'CORE_WON_351',attack_bonus=-3)
        aura=self.g._summon(0,'CORE_CS2_122');self.assertEqual((m.attack,m.attack_deficit),(0,-1))
        self.g._silence(aura);self.assertEqual((m.attack,m.attack_deficit),(0,-2))
        self.g._silence(m);self.assertEqual((m.attack,m.attack_deficit),(1,0))
    def test_copy_preserves_signed_attack_without_source_aura(self):
        m=self.g._summon(0,'CORE_WON_351',attack_bonus=-3);self.g._summon(0,'CORE_CS2_122')
        clone=self.g._summon(1,m.card_id,copy_from=m)
        self.assertEqual((clone.attack,clone.attack_deficit),(0,-2))
    def test_zero_attack_defender_deals_no_damage_or_healing(self):
        m=self.g._summon(1,'CORE_WON_351',attack_bonus=-3)
        attacker=self.g._summon(0,'CS3_025');attacker.summoned_turn=-1
        self.g.step(Action('attack',attacker.uid,m.uid));self.assertEqual(attacker.health,6)
    def test_temporary_buff_expires_back_to_deficit(self):
        m=self.g._summon(0,'CORE_WON_351',attack_bonus=-3)
        self.g._effect(('temporary_attack_buff',3),dict(owner=0,source=None,target=m.uid,bonus=0))
        self.assertEqual(m.attack,1);self.g.step(Action('end'))
        self.assertEqual((m.attack,m.attack_deficit),(0,-2))
    def test_setting_stats_clears_previous_deficit(self):
        m=self.g._summon(0,'CORE_WON_351',attack_bonus=-3)
        self.g._effect(('set_target_stats',2,3),dict(owner=0,source=None,target=m.uid,bonus=0))
        self.assertEqual((m.attack,m.attack_deficit),(2,0));self.g._buff(m,1,0);self.assertEqual(m.attack,3)

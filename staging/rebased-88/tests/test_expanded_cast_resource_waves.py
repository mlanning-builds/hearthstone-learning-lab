"""Resource-spending casts and resumable multi-wave board damage."""
import unittest
from unittest.mock import patch
from expanded import Game,Action,random_deck

class CastResourceWaveTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('MAGE',31),random_deck('ROGUE',53)],seed=71)
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:
            p.hand=[];p.board=[];p.deck=['CORE_CS2_029']*30;p.health=30;p.mana=p.max_mana=10
        return g
    def cast(self,g,cid):
        g._start_play_effects([('cast_fixed_spell',cid,'random')],dict(owner=0,source=None,target=0,bonus=0,lifesteal=False))
    def enemy(self,g):
        m=g._summon(1,'CS3_020');m.health=m.max_health=20;return m
    def interrupt_first_wave(self,g,waves):
        dispatch=g._dispatch_effect
        def effect(op,ctx):
            dispatch(op,ctx)
            if op[0]=='area_damage':
                waves.append(op[2])
                if len(waves)==1:g._effect(('choose_fixed_summon',('AT_037t',)),dict(owner=0,source=None))
        return patch.object(g,'_dispatch_effect',side_effect=effect)
    def test_descending_damage_waits_between_waves(self):
        g=self.game();m=self.enemy(g);waves=[]
        with self.interrupt_first_wave(g,waves):
            self.cast(g,'CATA_491');self.assertEqual(waves,[3]);self.assertEqual(m.health,17)
            self.assertIsNotNone(g.pending_choice);g.step(g.legal_actions()[0])
            self.assertEqual(waves,[3,2,1]);self.assertEqual(m.health,14)
        self.assertIsNone(g.pending_frame)
    def test_armor_is_spent_once_before_interrupted_waves(self):
        g=self.game();m=self.enemy(g);g.players[0].armor=10;waves=[]
        with self.interrupt_first_wave(g,waves):
            self.cast(g,'TLC_601');self.assertEqual(g.players[0].armor,5)
            self.assertEqual(m.health,19);g._gain_armor(0,3)
            g.step(g.legal_actions()[0])
            self.assertEqual(waves,[1]*5);self.assertEqual(m.health,15)
            self.assertEqual(g.players[0].armor,8)
    def test_zero_armor_produces_no_damage(self):
        g=self.game();m=self.enemy(g);g.players[0].armor=0;self.cast(g,'TLC_601')
        self.assertEqual(m.health,20)
    def test_partial_armor_limits_wave_count(self):
        g=self.game();m=self.enemy(g);g.players[0].armor=2;self.cast(g,'TLC_601')
        self.assertEqual(m.health,18);self.assertEqual(g.players[0].armor,0)
    def test_spell_damage_applies_each_wave(self):
        g=self.game();m=self.enemy(g);bonus=g._summon(0,'END_022');bonus.health=bonus.max_health=30;bonus.health-=1
        self.cast(g,'CATA_491');self.assertEqual(m.health,8)
    def test_deathrattle_summon_can_be_hit_by_next_wave(self):
        g=self.game();m=g._summon(1,'CORE_EX1_110');m.health=3;self.cast(g,'CATA_491')
        baine=next(m for m in g.players[1].minions if m.card_id=='TOKEN_BAINE')
        self.assertEqual(baine.health,2)
    def test_army_spends_corpses_only_for_available_slots(self):
        g=self.game();g.players[0].corpses=10
        for _ in range(6):g._summon(0,'AT_037t')
        self.cast(g,'RLK_060');self.assertEqual(g.players[0].corpses,9);self.assertEqual(len(g.players[0].board),7)
    def test_grave_strength_spends_threshold_once(self):
        g=self.game();m=g._summon(0,'AT_037t');g.players[0].corpses=5
        self.cast(g,'RLK_707');self.assertEqual(m.attack,4);self.assertEqual(g.players[0].corpses,0)
    def test_blood_tap_below_threshold_retains_corpses(self):
        g=self.game();c=g._add(0,'CS3_020');g.players[0].corpses=1
        self.cast(g,'CORE_RLK_712');self.assertEqual((c.attack_bonus,c.health_bonus),(1,1));self.assertEqual(g.players[0].corpses,1)
    def test_tomb_guardians_grant_reborn_and_spend_four(self):
        g=self.game();g.players[0].corpses=4;self.cast(g,'CORE_RLK_118')
        self.assertEqual(len(g.players[0].minions),2)
        self.assertTrue(all('REBORN' in m.keywords for m in g.players[0].minions))
        self.assertEqual(g.players[0].corpses,0)
    def test_mossbinding_pays_effect_mana_even_though_cast_is_free(self):
        g=self.game();g.players[0].mana=3;self.cast(g,'CATA_135')
        self.assertEqual(g.players[0].mana,0)
        self.assertTrue(g.players[0].minions)
        for m in g.players[0].minions:
            self.assertEqual(m.attack,g.cards[m.card_id]['attack']+3)
    def test_asphyxiate_destroys_highest_attack(self):
        g=self.game();a=g._summon(1,'AT_037t');b=self.enemy(g);b.attack=8
        self.cast(g,'CORE_RLK_087');self.assertIn(a,g.players[1].minions);self.assertNotIn(b,g.players[1].minions)

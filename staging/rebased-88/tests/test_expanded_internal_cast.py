"""Fixed internal spell casts use separate attribution and resumable frames."""
import unittest
from unittest.mock import patch
from copy import deepcopy
from expanded import Game,Action,random_deck
from expanded.game import Card
from expanded.cards import RULES
from engine.cards import UnsupportedCard

class InternalCastTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('ROGUE',31),random_deck('MAGE',53)],seed=71,record=True)
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:
            p.hand=[];p.board=[];p.deck=['CORE_CS2_029']*30;p.mana=p.max_mana=10;p.health=30;p.armor=0
        g.events=[]
        return g
    def play(self,g,cid):
        c=g._add(g.current,cid);g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid))
        return next((m for m in g.players[g.current].minions if m.card_id==cid),None)
    def cast(self,g,cid='CS2_029',policy='enemies',source=None,tail=()):
        g._start_play_effects([('cast_fixed_spell',cid,policy)]+list(tail),dict(owner=0,source=source,target=0,bonus=0,lifesteal=False));g._settle()
    def casts(self,g):return [e for e in g.events if e['event']=='internal_spell_cast']
    def die(self,g,cid='JAIL_974',owner=0):
        m=g._summon(owner,cid);m.health=0;g._settle();return m
    def test_opu_battlecry_casts_once_without_combo(self):
        g=self.game();enemy=g._summon(1,'CS3_020');before=enemy.health;self.play(g,'TLC_522')
        self.assertEqual(enemy.health,before-1);self.assertEqual(len(g.players[0].hand),1);self.assertEqual(len(self.casts(g)),1)
    def test_opu_combo_casts_twice(self):
        g=self.game();self.play(g,'TOKEN_COIN');g.players[0].mana=10;self.play(g,'TLC_522')
        self.assertEqual(len(g.players[0].hand),2);self.assertEqual(len(self.casts(g)),2);self.assertEqual(g.players[0].mana,4)
    def test_opu_death_casts_once(self):
        g=self.game();self.die(g,'TLC_522');self.assertEqual(len(g.players[0].hand),1);self.assertEqual(len(self.casts(g)),1)
    def test_silenced_opu_has_no_death_cast(self):
        g=self.game();m=g._summon(0,'TLC_522');g._silence(m);m.health=0;g._settle();self.assertFalse(self.casts(g))
    def test_no_hand_play_spell_counters_or_triggers(self):
        g=self.game();anton=g._summon(0,'CORE_EX1_559');g._summon(0,'CORE_NEW1_020');enemy=g._summon(1,'CS3_020');before=enemy.health
        self.play(g,'TLC_522');p=g.players[0]
        self.assertEqual(p.cards_played,1);self.assertEqual(p.spells_turn,[]);self.assertEqual(len(p.hand),1);self.assertEqual(enemy.health,before-1)
    def test_counterspell_does_not_counter_minion_cast(self):
        g=self.game();g.players[1].secrets.append(Card(g._new_id(),'CORE_EX1_287'));self.play(g,'TLC_522')
        self.assertEqual(len(g.players[0].hand),1);self.assertEqual(len(g.players[1].secrets),1)
    def test_spell_damage_applies(self):
        g=self.game();m=g._summon(0,'END_022');m.health-=1;self.cast(g);self.assertEqual(g.players[1].health,22)
    def test_caster_keywords_not_inherited(self):
        g=self.game();source=g._summon(0,'TLC_522');source.keywords.update({'POISONOUS','LIFESTEAL'});g.players[0].health=10
        e=g._summon(1,'CS3_020');e.health=e.max_health=20
        with patch.object(g.rng,'choice',side_effect=lambda values:next(x for x in values if x>0)):self.cast(g,source=source)
        self.assertEqual(e.health,14);self.assertEqual(g.players[0].health,10)
    def test_fireball_enemy_policy_excludes_friendly_characters(self):
        g=self.game();g._summon(0,'EDR_851t');self.cast(g)
        self.assertEqual(self.casts(g)[0]['target'],g.hero_id(1));self.assertEqual(g.players[0].health,30)
    def test_fireball_fizzles_with_no_eligible_enemy(self):
        g=self.game();g.players[1].immune=True
        # Use the established hero immunity hook without assuming field layout.
        with patch.object(g,'_hero_immune',return_value=True):self.cast(g)
        self.assertEqual(g.players[1].health,30);self.assertFalse(self.casts(g));self.assertTrue(any(e['event']=='spell_fizzle' for e in g.events))
    def test_archmage_needs_four_other_deaths(self):
        g=self.game()
        for _ in range(4):self.die(g)
        self.assertEqual(g.players[1].health,30);self.assertFalse(self.casts(g))
        self.die(g);self.assertEqual(g.players[1].health,24)
    def test_opponent_archmage_deaths_do_not_count(self):
        g=self.game()
        for _ in range(4):self.die(g,owner=1)
        self.die(g);self.assertFalse(self.casts(g))
    def test_simultaneous_fifth_death_wave_qualifies_all(self):
        g=self.game()
        for _ in range(5):g._summon(0,'JAIL_974').health=0
        g._settle();self.assertEqual(len(self.casts(g)),5);self.assertTrue(g.terminal)
    def test_live_archmage_deathrattle_replay_counts_four_prior(self):
        g=self.game()
        for _ in range(4):self.die(g)
        m=g._summon(0,'JAIL_974')
        g._start_play_effects([('replay_friendly_deathrattle',)],dict(owner=0,source=None,target=m.uid,bonus=0,lifesteal=False));g._settle()
        self.assertEqual(g.players[1].health,24);self.assertIn(m,g.players[0].board)
    def test_parent_continues_after_nested_cast(self):
        g=self.game();self.cast(g,tail=(('armor',3),));self.assertEqual(g.players[0].armor,3);self.assertIsNone(g.pending_frame)
    def test_unsupported_internal_spell_fails_before_rng(self):
        g=self.game();state=g.rng.getstate()
        with self.assertRaises(UnsupportedCard):self.cast(g,'CORE_RLK_567')
        self.assertEqual(g.rng.getstate(),state)
    def test_parent_choice_waits_after_cast(self):
        g=self.game();self.cast(g,tail=(('choose_fixed_summon',('EDR_851t',)),('armor',3)))
        self.assertIsNotNone(g.pending_choice);self.assertEqual(g.players[0].armor,0);self.assertEqual(g.players[1].health,24)
        g.step(g.legal_actions()[0]);self.assertEqual(g.players[0].armor,3);self.assertEqual(len(self.casts(g)),1)
    def test_trigger_choice_within_cast_resumes_remaining_draw(self):
        g=self.game();e=g._summon(1,'CS3_020')
        original=g._deal_effect
        def damage(target,amount,ctx):
            dealt=original(target,amount,ctx)
            g._effect(('choose_fixed_summon',('EDR_851t',)),dict(owner=0,source=e,target=0,bonus=0,lifesteal=False))
            return dealt
        # A nested effect must suspend before its following draw.
        with patch.object(g,'_deal_effect',side_effect=damage):
            self.cast(g,'EX1_129','random')
        self.assertIsNotNone(g.pending_choice);self.assertEqual(len(g.players[0].hand),0)
        g.step(g.legal_actions()[0]);self.assertEqual(len(g.players[0].hand),1);self.assertIsNone(g.pending_frame)
    def test_opu_settles_deaths_between_battlecry_and_combo(self):
        g=self.game();self.play(g,'TOKEN_COIN');g.players[0].mana=10
        m=g._summon(1,'CORE_EX1_110');m.health=1
        self.play(g,'TLC_522')
        baine=next(m for m in g.players[1].minions if m.card_id=='TOKEN_BAINE')
        self.assertEqual(baine.health,g.cards['TOKEN_BAINE']['health']-1)
    def test_internal_random_target_excludes_elusive(self):
        g=self.game();m=g._summon(1,'CS3_020');m.keywords.add('ELUSIVE');self.cast(g)
        self.assertEqual(g.players[1].health,24);self.assertEqual(m.health,g.cards[m.card_id]['health'])
    def test_terminal_cast_stops_parent_effects(self):
        g=self.game();g.players[1].health=6;self.cast(g,tail=(('armor',3),))
        self.assertTrue(g.terminal);self.assertEqual(g.players[0].armor,0);self.assertIsNone(g.pending_frame)
    def test_failed_internal_cast_rolls_back_hand_play(self):
        g=self.game();c=g._add(0,'TLC_522');action=next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid)
        before=deepcopy(g.__dict__);original=g._cast_spell_effect
        def effect(op,ctx):
            if op[0]=='internal_spell_complete':raise ValueError('synthetic failure')
            return original(op,ctx)
        with patch.object(g,'_cast_spell_effect',side_effect=effect):
            with self.assertRaisesRegex(ValueError,'synthetic failure'):g.step(action)
        self.assertEqual(g.players,before['players']);self.assertEqual(g.rng.getstate(),before['rng'].getstate());self.assertEqual(g.events,before['events'])
    def test_no_mana_payment_for_fixed_spell(self):
        g=self.game();g.players[0].mana=0;self.cast(g);self.assertEqual(g.players[0].mana,0)

if __name__=='__main__':unittest.main()

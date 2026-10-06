"""Internal Secret placement, delayed effects and per-missile continuations."""
import unittest
from unittest.mock import patch
from expanded import Game,Action,random_deck
from expanded.game import Card
from expanded.cards import RULES
from expanded.secrets import SECRETS

class InternalStateSpellTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('MAGE',31),random_deck('ROGUE',53)],seed=71,record=True)
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:
            p.hand=[];p.board=[];p.deck=['CORE_CS2_029']*30;p.health=30;p.mana=p.max_mana=10
        return g
    def cast(self,g,cid):
        g._start_play_effects([('cast_fixed_spell',cid,'random')],dict(owner=0,source=None,target=0,bonus=0,lifesteal=False))
    def test_all_secrets_can_be_cast_internally(self):
        for cid in SECRETS:
            with self.subTest(card=cid):
                g=self.game();self.cast(g,cid)
                self.assertEqual([c.card_id for c in g.players[0].secrets],[cid])
                self.assertEqual(g.players[0].mana,10);self.assertEqual(g.players[0].cards_played,0)
    def test_duplicate_secret_fails_placement_but_cast_completes(self):
        g=self.game();self.cast(g,'CORE_EX1_287');original=g.players[0].secrets[0]
        self.cast(g,'CORE_EX1_287')
        self.assertEqual(g.players[0].secrets,[original]);self.assertIs(g.players[0].secrets[0],original)
        self.assertEqual(sum(e['event']=='internal_spell_complete' for e in g.events),2)
        self.assertTrue(any(e['event']=='secret_fizzle' and e['reason']=='duplicate' for e in g.events))
    def test_sixth_distinct_secret_does_not_replace_earlier_secrets(self):
        g=self.game();ids=list(SECRETS)
        for cid in ids[:6]:self.cast(g,cid)
        self.assertEqual([c.card_id for c in g.players[0].secrets],ids[:5])
    def test_quest_occupies_one_secret_slot(self):
        g=self.game();g.players[0].quest={'card_id':'TLC_446','progress':0}
        for cid in list(SECRETS)[:5]:self.cast(g,cid)
        self.assertEqual(len(g.players[0].secrets),4);self.assertEqual(g.players[0].quest['card_id'],'TLC_446')
    def test_internal_secret_stays_hidden_in_opponent_observation(self):
        g=self.game();self.cast(g,'CORE_EX1_287');view=g.observe(1)['players'][0]
        self.assertEqual(view['secret_count'],1);self.assertNotIn('secrets',view)
    def test_secret_zone_retains_cast_physical_identity(self):
        g=self.game();c=g._add(0,'CORE_EX1_287');c.rule_state={'marker':11}
        g._start_play_effects([('cast_zone_spell','hand',c.uid,'random')],dict(owner=0,source=None))
        self.assertIs(g.players[0].secrets[0],c);self.assertEqual(c.rule_state['marker'],11)
        self.assertNotIn(c,g.players[0].hand)
    def test_normal_secret_play_retains_identity_and_payment(self):
        g=self.game();c=g._add(0,'CORE_EX1_287')
        g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid))
        self.assertIs(g.players[0].secrets[0],c);self.assertEqual(g.players[0].mana,7)
    def test_automatically_placed_counterspell_triggers_normally(self):
        g=self.game();self.cast(g,'CORE_EX1_287');g.step(Action('end'))
        c=g._add(1,'CORE_CS2_029');g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==g.hero_id(0)))
        self.assertEqual(g.players[0].health,30);self.assertEqual(g.players[0].secrets,[])
    def test_delayed_sigil_fires_next_owner_start(self):
        g=self.game();self.cast(g,'CATA_528');g.step(Action('end'))
        self.assertEqual(g.players[0].minions,[]);g.step(Action('end'))
        self.assertEqual([m.card_id for m in g.players[0].minions],['CATA_528t'])
        self.assertFalse(g.players[0].scheduled_effects)
    def test_repeating_aura_counts_owner_turns(self):
        g=self.game();self.cast(g,'TIME_700')
        for count in range(1,4):
            g.step(Action('end'));self.assertEqual(len(g.players[0].minions),count)
            g.step(Action('end'))
        self.assertFalse(g.players[0].scheduled_effects)
    def test_delayed_missiles_use_damage_bonus_at_resolution(self):
        g=self.game();self.cast(g,'FIR_902');m=g._summon(0,'END_022');m.health-=1
        g.step(Action('end'));g.step(Action('end'))
        self.assertEqual(g.players[1].health,22)
    def test_unknown_scheduled_child_is_not_admitted(self):
        g=self.game()
        with patch.dict(RULES,{'CATA_528':('none',[('schedule_turn_effect','start',1,1,(('not_implemented',),))])}):
            self.assertFalse(g._supports_internal_spell('CATA_528'))
    def test_shuffled_draw_spells_are_not_cast_immediately(self):
        g=self.game();self.cast(g,'JAIL_386')
        self.assertEqual(g.players[0].armor,2)
        self.assertEqual(sum(g._card_data(c)['id']=='JAIL_386t' for c in g.players[0].deck),5)
    def test_zone_copy_choices_resolve_automatically(self):
        g=self.game();self.cast(g,'TIME_432')
        self.assertIsNone(g.pending_choice);self.assertEqual(len(g.players[0].hand),2)
        self.assertEqual(len(g.players[0].deck),30);self.assertEqual(len(g.players[1].deck),30)
        self.assertEqual(g.players[0].discoveries_this_turn,2)
    def test_next_discount_is_created_without_being_consumed(self):
        g=self.game();self.cast(g,'CORE_EX1_145');c=g._add(0,'CORE_CS2_029')
        self.assertEqual(g._cost(c,0),2);self.assertEqual(g.players[0].mana,10)
    def test_stat_setting_spell_resets_existing_damage(self):
        g=self.game();m=g._summon(1,'CS3_020');m.health=1
        with patch.object(g.rng,'choice',return_value=m.uid):self.cast(g,'DINO_403')
        self.assertEqual((m.attack,m.health,m.max_health),(8,8,8));self.assertIn('CHARGE',m.keywords)
    def test_missile_damage_bonus_adds_shots_not_damage_per_shot(self):
        g=self.game();m=g._summon(0,'END_022');m.health-=1;self.cast(g,'TIME_027')
        self.assertEqual(g.players[1].health,22)
    def test_missiles_stop_for_player_choice_before_remaining_hits(self):
        g=self.game();original=g._deal_effect;hits=[]
        def hit(target,amount,ctx):
            result=original(target,amount,ctx);hits.append(target)
            if len(hits)==1:g._effect(('choose_fixed_summon',('EDR_851t',)),dict(owner=0,source=None))
            return result
        with patch.object(g,'_deal_effect',side_effect=hit):
            self.cast(g,'TIME_027')
            self.assertEqual(len(hits),1);self.assertEqual(g.players[1].health,29)
            self.assertIsNotNone(g.pending_choice)
            self.assertFalse(any(g._card_data(c)['id']=='TIME_025t' for c in g.players[0].deck))
            g.step(g.legal_actions()[0]);self.assertEqual(len(hits),6)
        self.assertEqual(g.players[1].health,24)
        self.assertEqual(sum(g._card_data(c)['id']=='TIME_025t' for c in g.players[0].deck),2)
    def test_missiles_resolve_deathrattle_before_next_hit(self):
        g=self.game();m=g._summon(1,'CORE_EX1_110');m.health=1
        def target(values):return next((uid for uid in values if uid>0),values[0])
        with patch.object(g.rng,'choice',side_effect=target):self.cast(g,'TIME_027')
        self.assertFalse(g.players[1].minions)
        self.assertIn('TOKEN_BAINE',g.players[1].death_history)
        self.assertEqual(g.players[1].health,30)
    def test_missiles_stop_on_lethal_before_shuffle(self):
        g=self.game();g.players[1].health=1;self.cast(g,'TIME_027')
        self.assertTrue(g.terminal)
        self.assertFalse(any(g._card_data(c)['id']=='TIME_025t' for c in g.players[0].deck))

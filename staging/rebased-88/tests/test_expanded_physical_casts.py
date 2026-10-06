"""Physical spell casts and Choose One branches share existing effect frames."""
import unittest
from unittest.mock import patch
from copy import deepcopy
from expanded import Game,Action,random_deck
from expanded.game import Card
from expanded.cards import RULES,CHOICES
from engine.cards import UnsupportedCard

class PhysicalCastTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('DRUID',31),random_deck('MAGE',53)],seed=71,record=True)
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:
            p.hand=[];p.board=[];p.deck=['CORE_CS2_029']*30;p.mana=p.max_mana=10;p.health=30;p.armor=0
        return g
    def cast(self,g,op,source=None):
        g._start_play_effects([op,('armor',3)],dict(owner=0,source=source,target=0,bonus=0,lifesteal=False))
    def fixed(self,g,cid,source=None,policy='random'):
        self.cast(g,('cast_fixed_spell',cid,policy),source)
    def test_hand_cast_consumes_exact_copy_and_preserves_bonus(self):
        g=self.game();a=g._add(0,'CS2_029');b=g._add(0,'CS2_029');b.spell_damage_bonus=3
        self.cast(g,('cast_zone_spell','hand',b.uid,'enemies'))
        self.assertEqual(g.players[0].hand,[a]);self.assertEqual(g.players[1].health,21)
        self.assertEqual(g.players[0].mana,10);self.assertEqual(g.players[0].cards_played,0)
        self.assertEqual(g.players[0].spells_turn,[])
    def test_deck_cast_does_not_draw_or_discard(self):
        g=self.game();a=Card(g._new_id(),'CS2_029');a.spell_damage_bonus=2
        g.players[0].deck=['CORE_CS2_029',a,'CORE_EX1_129'];g.events=[]
        self.cast(g,('cast_zone_spell','deck',a.uid,'enemies'))
        self.assertEqual(g.players[0].deck,['CORE_CS2_029','CORE_EX1_129'])
        self.assertEqual(g.players[1].health,22);self.assertEqual(g.players[0].hand,[])
        self.assertFalse(any(e['event'] in ('draw','discard','play') for e in g.events))
    def test_same_physical_object_reaches_effects(self):
        g=self.game();a=g._add(0,'CS2_029');a.rule_state={'picklock_value':9};a._starting_owner=0
        seen=[];original=g._cast_spell_effect
        def observe(op,ctx):
            if op[0]=='internal_spell_begin':seen.append(op[1]['physical_card'])
            return original(op,ctx)
        with patch.dict(RULES,{'CS2_029':('character',[('held_picklock',)])}),patch.object(g,'_cast_spell_effect',side_effect=observe):
            self.cast(g,('cast_zone_spell','hand',a.uid,'enemies'))
        self.assertIs(seen[0],a);self.assertEqual(seen[0]._starting_owner,0);self.assertEqual(g.players[1].health,21)
    def test_detached_spell_preserves_damage_bonus(self):
        g=self.game();a=Card(g._new_id(),'CS2_029');a.spell_damage_bonus=4
        self.cast(g,('cast_physical_spell',a,'enemies'));self.assertEqual(g.players[1].health,20)
    def test_detached_path_rejects_card_still_in_zone(self):
        g=self.game();a=g._add(0,'CS2_029')
        with self.assertRaises(UnsupportedCard):self.cast(g,('cast_physical_spell',a,'enemies'))
        self.assertIn(a,g.players[0].hand)
    def test_missing_uid_does_not_consume_other_copy(self):
        g=self.game();a=g._add(0,'CS2_029');self.cast(g,('cast_zone_spell','hand',a.uid+1,'enemies'))
        self.assertEqual(g.players[0].hand,[a]);self.assertEqual(g.players[1].health,30)
    def test_unsupported_spell_rejected_before_removal(self):
        g=self.game();a=g._add(0,'CORE_RLK_567');state=g.rng.getstate()
        with self.assertRaises(UnsupportedCard):self.cast(g,('cast_zone_spell','hand',a.uid,'enemies'))
        self.assertIn(a,g.players[0].hand);self.assertEqual(g.rng.getstate(),state)
    def test_fizzled_zone_spell_is_consumed(self):
        g=self.game();a=g._add(0,'CS2_029')
        with patch.object(g,'_hero_immune',return_value=True):self.cast(g,('cast_zone_spell','hand',a.uid,'enemies'))
        self.assertNotIn(a,g.players[0].hand);self.assertEqual(g.players[1].health,30)
        self.assertTrue(any(e['event']=='spell_fizzle' for e in g.events))
    def test_enemies_policy_keeps_untargeted_spell(self):
        g=self.game();self.fixed(g,'EX1_129',policy='enemies');self.assertEqual(len(g.players[0].hand),1)
    def test_prefer_source_uses_eligible_source(self):
        g=self.game();m=g._summon(0,'CS3_020');m.health=m.max_health=20
        self.fixed(g,'CS2_029',m,'prefer_source');self.assertEqual(m.health,14)
    def test_prefer_source_falls_back_when_source_ineligible(self):
        g=self.game();m=g._summon(0,'CS3_020');m.keywords.add('ELUSIVE')
        with patch.object(g.rng,'choice',return_value=g.hero_id(1)):self.fixed(g,'CS2_029',m,'prefer_source')
        self.assertEqual(m.health,g.cards[m.card_id]['health']);self.assertEqual(g.players[1].health,24)
    def test_choose_one_selects_branch_before_its_target(self):
        g=self.game()
        with patch.object(g.rng,'randrange',return_value=1):self.fixed(g,'CORE_AT_037')
        self.assertEqual([m.card_id for m in g.players[0].minions],['AT_037t']*2)
        self.assertIsNone(g.pending_choice)
    def test_choose_one_damage_branch_uses_spell_damage(self):
        g=self.game();a=Card(g._new_id(),'CORE_AT_037');a.spell_damage_bonus=3
        with patch.object(g.rng,'randrange',return_value=0):self.cast(g,('cast_physical_spell',a,'enemies'))
        self.assertEqual(g.players[1].health,25)
    def test_invalid_branch_target_fizzles_without_reroll(self):
        g=self.game()
        with patch.object(g.rng,'randrange',return_value=1) as branch:self.fixed(g,'EDR_490')
        branch.assert_called_once_with(2);self.assertEqual(g.players[0].minions,[])
        self.assertTrue(any(e['event']=='spell_fizzle' for e in g.events))
    def test_fandral_power_summons_before_buffing(self):
        g=self.game();g._summon(0,'CORE_OG_044')
        with patch.object(g.rng,'randrange') as branch:self.fixed(g,'CORE_EX1_160')
        branch.assert_not_called();panther=next(m for m in g.players[0].minions if m.card_id=='EX1_160t')
        self.assertEqual((panther.attack,panther.health),(4,3))
    def test_fandral_wrath_applies_spell_damage_once(self):
        g=self.game();g._summon(0,'CORE_OG_044');e=g._summon(1,'CS3_020');e.health=e.max_health=20
        a=Card(g._new_id(),'CORE_EX1_154');a.spell_damage_bonus=2
        self.cast(g,('cast_physical_spell',a,'enemies'))
        self.assertEqual(e.health,14);self.assertEqual(len(g.players[0].hand),1)
    def test_silenced_fandral_does_not_combine(self):
        g=self.game();m=g._summon(0,'CORE_OG_044');g._silence(m)
        with patch.object(g.rng,'randrange',return_value=0):self.fixed(g,'CORE_EX1_160')
        self.assertEqual(len(g.players[0].minions),1)
    def test_opponent_fandral_does_not_combine(self):
        g=self.game();g._summon(1,'CORE_OG_044')
        with patch.object(g.rng,'randrange',return_value=1):self.fixed(g,'CORE_EX1_160')
        self.assertEqual(g.players[0].minions[0].attack,3)
    def test_morbid_combined_without_corpses_still_summons(self):
        g=self.game();g._summon(0,'CORE_OG_044');g.players[0].corpses=0;self.fixed(g,'EDR_813')
        self.assertEqual(sum(m.card_id=='EDR_813at' for m in g.players[0].minions),2)
    def test_morbid_damage_spends_corpses(self):
        g=self.game();e=g._summon(1,'CS3_020');e.health=e.max_health=20;g.players[0].corpses=2
        with patch.object(g.rng,'randrange',return_value=1):self.fixed(g,'EDR_813',policy='enemies')
        self.assertEqual(e.health,16);self.assertEqual(g.players[0].corpses,0)
    def test_all_declared_spell_branches_execute(self):
        probe=self.game()
        for cid,branches in CHOICES.items():
            if probe.cards[cid]['type']!='SPELL':continue
            for index in range(len(branches)):
                with self.subTest(card=cid,branch=index):
                    g=self.game();m=g._summon(1,'CS3_020');m.health=10;m.max_health=20;g.players[0].corpses=5
                    with patch.object(g.rng,'randrange',return_value=index):self.fixed(g,cid)
                    casts=[e for e in g.events if e['event']=='internal_spell_cast']
                    self.assertEqual(len(casts),1);self.assertEqual(casts[0]['branch'],index)
                    self.assertIsNone(g.pending_frame);self.assertIsNone(g.pending_choice)
    def test_failure_rolls_back_consumption_and_rng(self):
        g=self.game();a=g._add(0,'CORE_AT_037');trigger=g._add(0,'TLC_522')
        action=next(a for a in g.legal_actions() if a.kind=='play' and a.source==trigger.uid)
        original=g._cast_spell_effect;before=deepcopy(g.__dict__)
        def fail(op,ctx):
            if op[0]=='internal_spell_complete':raise ValueError('injected')
            return original(op,ctx)
        with patch.dict(RULES,{'TLC_522':('none',[('cast_zone_spell','hand',a.uid,'random')])}),patch.object(g,'_cast_spell_effect',side_effect=fail):
            with self.assertRaisesRegex(ValueError,'injected'):g.step(action)
        self.assertEqual(g.players,before['players']);self.assertEqual(g.rng.getstate(),before['rng'].getstate())

    def test_held_upgrade_is_used_when_cast_from_hand(self):
        g=self.game();a=g._add(0,'FIR_916');a.rule_state={'held_turn_ends':2}
        e=g._summon(1,'CS3_020');e.health=e.max_health=20
        self.cast(g,('cast_zone_spell','hand',a.uid,'random'))
        self.assertEqual(e.health,17)
    def test_regular_fireball_alias_uses_shared_admission(self):
        g=self.game();self.fixed(g,'CORE_CS2_029',policy='enemies')
        self.assertEqual(g.players[1].health,24)
    def test_unknown_operations_are_not_silently_admitted(self):
        g=self.game()
        with patch.dict(RULES,{'CORE_CS2_029':('character',[('future_unimplemented_effect',)])}):
            self.assertFalse(g._supports_internal_spell('CORE_CS2_029'))
            with self.assertRaises(UnsupportedCard):self.fixed(g,'CORE_CS2_029')
    def test_unplayable_empty_shadow_not_inferred_as_vanilla_spell(self):
        g=self.game();self.assertFalse(g._supports_internal_spell('CORE_RLK_567'))
    def test_all_admitted_spell_paths_complete_or_end_game(self):
        probe=self.game();ids=[cid for cid in probe.cards if probe._supports_internal_spell(cid)]
        self.assertGreater(len(ids),150)
        for cid in ids:
            with self.subTest(card=cid):
                g=self.game();a=g._summon(0,'CS3_020');b=g._summon(1,'CS3_020')
                for m in (a,b):m.health=15;m.max_health=20
                g.players[0].corpses=10
                if cid=='EDR_259e1':
                    token=Card(g._new_id(),cid);token.stored_spell=Card(g._new_id(),'CORE_EX1_606');token.aura_duration=3
                    self.cast(g,('cast_physical_spell',token,'random'))
                else:self.fixed(g,cid)
                self.assertTrue(g.terminal or g.pending_frame is None)
                self.assertIsNone(g.pending_choice)
                self.assertEqual(g.players[0].cards_played,0)

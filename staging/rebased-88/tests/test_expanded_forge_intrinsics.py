"""Composites retain explicit intrinsic behavior across entry and lifecycle."""
from copy import deepcopy
import gzip,json
import unittest
from unittest.mock import patch
import test_expanded_generation as fixtures
from expanded import Action
from expanded import cards
from expanded.minion_forge import ForgePart
from engine.game import Card
from engine.cards import UnsupportedCard


class ForgeIntrinsicTests(unittest.TestCase):
    def setUp(self):
        self.game=fixtures.GenerationTests().game()
        with gzip.open('data/standard/all_cards.json.gz','rt') as stream:
            token=next(c for c in json.load(stream) if c['id']=='CATA_470t1')
        self.game.cards['CATA_470t1']=token
        change=patch.dict(cards.RULES,{'CATA_470t1':('none',[])})
        change.start();self.addCleanup(change.stop)

    def craft(self,intrinsics,keywords=(),operations=()):
        first=ForgePart('CORE_NEW1_023',operations=operations,keywords=keywords,source='explicit synthetic fixture',intrinsics=intrinsics)
        second=ForgePart('EDR_851t',source='explicit synthetic fixture')
        self.game.forge_contracts={('dragon',1):(first,),('dragon',2):(second,)}
        self.game._forge_offer(0,'dragon',0)
        self.game._resolve_choice(0,resume=False);self.game._resolve_choice(0,resume=False)
        return self.game.players[0].hand[-1]

    def play(self,card):
        self.game.step(next(a for a in self.game.legal_actions() if a.kind=='play' and a.source==card.uid))
        return self.game.players[0].minions[-1]

    def test_spell_damage_conditional_attack_and_silence(self):
        minion=self.play(self.craft((('spell_damage',1),('damaged_spell_damage',2),('damaged_attack',2))))
        attack=minion.attack
        self.assertEqual(self.game._spell_damage(0),1)
        self.game._damage(minion.uid,1);self.game._refresh_auras()
        self.assertEqual(self.game._spell_damage(0),3);self.assertEqual(minion.attack,attack+2)
        self.game._silence(minion)
        self.assertEqual(self.game._spell_damage(0),0);self.assertEqual(minion.attack,attack)

    def test_cost_floor_and_enemy_taunt_are_continuous(self):
        minion=self.play(self.craft((('cost_floor',2),('enemy_taunt',True))))
        enemy=self.game._summon(1,'EDR_851t')
        card=Card(self.game._new_id(),'CORE_CS2_029');card.set_cost=0
        self.assertEqual(self.game._cost(card,0),2)
        self.assertIn('TAUNT',self.game._effective_keywords(enemy))
        self.game._silence(minion)
        self.assertEqual(self.game._cost(card,0),0)
        self.assertNotIn('TAUNT',self.game._effective_keywords(enemy))

    def test_trigger_uses_composite_source_and_disappears_after_silence(self):
        minion=self.play(self.craft((('trigger',('spell_cast',(('buff_self',1,0),))),)))
        attack=minion.attack
        self.game._queue_event('spell_cast',owner=0,card_id='CORE_CS2_029',cost=4)
        self.game._settle(allow_event_choices=True)
        self.assertEqual(minion.attack,attack+1)
        self.game._silence(minion);attack=minion.attack
        self.game._queue_event('spell_cast',owner=0,card_id='CORE_CS2_029',cost=4)
        self.game._settle(allow_event_choices=True)
        self.assertEqual(minion.attack,attack)

    def test_turn_trigger_and_draw_suppression(self):
        self.play(self.craft((('end_effects',(('armor',2),)),('suppress_draw',True))))
        self.game.step(Action('end'))
        self.assertEqual(self.game.players[0].armor,2)
        before=len(self.game.players[0].hand)
        self.game.step(Action('end'))
        self.assertEqual(len(self.game.players[0].hand),before)

    def test_overload_and_intrinsic_cost_on_physical_recipe(self):
        card=self.craft((('overload',2),('cost_rule','hero_healed')))
        self.assertGreater(self.game._cost(card,0),0)
        self.game.players[0].hero_healed_turn=True
        self.assertEqual(self.game._cost(card,0),0)
        self.play(card)
        self.assertEqual(self.game.players[0].overload_next,2)
        self.assertEqual(self.game.players[0].overloaded_total,2)

    def test_clone_keeps_independent_composite_properties(self):
        minion=self.play(self.craft((('spell_damage',2),)))
        clone=deepcopy(self.game)
        self.game._silence(minion)
        self.assertEqual(self.game._spell_damage(0),0)
        self.assertEqual(clone._spell_damage(0),2)

    def test_reborn_restores_recipe_but_not_temporary_enchantments(self):
        card=self.craft((('spell_damage',2),),keywords=('REBORN',))
        minion=self.play(card);base_attack=minion.attack;base_health=minion.max_health
        self.game._buff(minion,5,5)
        minion.health=0;self.game._settle(allow_event_choices=True)
        reborn=self.game.players[0].minions[-1]
        self.assertNotEqual(reborn.uid,minion.uid)
        self.assertEqual((reborn.attack,reborn.health,reborn.max_health),(base_attack,1,base_health))
        self.assertEqual(self.game._spell_damage(0),2)
        self.assertNotIn('REBORN',self.game._effective_keywords(reborn))

    def test_invalid_intrinsic_payload_fails_before_rng(self):
        for value in ((('spell_damage',True),),(('cost_rule','unknown'),),(('trigger',('invented_event',(('draw',1),))),),(('trigger',('spell_cast',(('draw',True),))),)):
            with self.subTest(value=value):
                before=self.game.rng.getstate()
                with self.assertRaises(UnsupportedCard):self.craft(value)
                self.assertEqual(self.game.rng.getstate(),before)
                self.assertIsNone(self.game.pending_choice)

    def test_expiring_composite_resolves_end_effect_before_expiration(self):
        minion=self.play(self.craft((('end_effects',(('armor',2),)),)))
        minion.expires=True
        self.game.step(Action('end'))
        self.assertEqual(self.game.players[0].armor,2)
        self.assertNotIn(minion,self.game.players[0].board)

    def test_hand_mechanics_reflect_explicit_composite_properties(self):
        card=self.craft((('spell_damage',1),('overload',2)),keywords=('TAUNT','RUSH'),operations=(('armor',1),))
        self.assertTrue({'TAUNT','RUSH','BATTLECRY','SPELLPOWER','OVERLOAD'}<=self.game._card_mechanics(card))

    def test_observed_recipes_cover_manifest_without_activating_game(self):
        from pathlib import Path
        from expanded.nefarius_parts import observed_contracts,DRAGONS,UNDEAD
        manifest=json.loads((Path(__file__).resolve().parents[3]/'data/review/nefarius-components.json').read_text())
        self.assertEqual(list(DRAGONS),manifest['stages']['dragon'])
        self.assertEqual(list(UNDEAD),manifest['stages']['undead'])
        contracts=observed_contracts()
        self.game.forge_contracts=contracts
        self.assertEqual(len(self.game._forge_pool('dragon',1,0)),19)
        self.assertEqual(len(self.game._forge_pool('dragon',2,0)),20)
        self.assertFalse(manifest['approved_for_runtime'])

    def test_every_affordable_observed_pair_constructs_full_recipe(self):
        from expanded.nefarius_parts import observed_contracts
        contracts=observed_contracts();pairs=0
        for first in contracts[('dragon',1)]:
            for second in contracts[('dragon',2)]:
                a,b=self.game.cards[first.card_id],self.game.cards[second.card_id]
                if a['cost']+b['cost']>10:continue
                choice=dict(kind='forge_part',forge_kind='dragon',owner=0,discount=3,first=first,parts=[second])
                self.game.players[0].hand=[]
                self.assertTrue(self.game._forge_choice(choice,dict(card_id=second.card_id)))
                card=self.game.players[0].hand[-1]
                self.assertEqual(card.base_stat_override,(a['attack']+b['attack'],a['health']+b['health']))
                self.assertEqual(card.rule_state['forge_intrinsics'],first.intrinsics+second.intrinsics)
                self.assertEqual(card.rule_state['crafted_ops'],first.operations+second.operations)
                self.assertEqual(card.rule_state['forge_death'],first.death_operations+second.death_operations)
                pairs+=1
        self.assertEqual(pairs,361)

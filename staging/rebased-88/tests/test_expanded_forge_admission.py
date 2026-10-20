"""Construction eligibility is checked before sampling a first component."""
import unittest
import test_expanded_choice_continuation as fixtures
from expanded.minion_forge import ForgePart
from engine.cards import UnsupportedCard


class ForgeAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.game = fixtures.ChoiceContinuationTests().game()
        # Explicit synthetic complete fixture pools; not production membership.
        for cid,cost in (('forge_cheap',2),('forge_expensive',9),('forge_second',3)):
            self.game.cards[cid] = dict(id=cid,type='MINION',cost=cost,attack=1,health=1)
        self.cheap = ForgePart('forge_cheap',source='synthetic fixture')
        self.expensive = ForgePart('forge_expensive',source='synthetic fixture')
        self.second = ForgePart('forge_second',source='synthetic fixture')
        self.game.forge_contracts = {('dragon',1):(self.cheap,self.expensive),('dragon',2):(self.second,)}

    def test_first_offer_excludes_only_unaffordable_completions(self):
        self.game._forge_offer(0,'dragon',3)
        self.assertEqual(self.game.pending_choice['parts'],[self.cheap])
        self.game._resolve_choice(0,resume=False)
        self.assertEqual(self.game.pending_choice['parts'],[self.second])

    def test_discount_does_not_make_over_ten_base_cost_eligible(self):
        self.game.forge_contracts[('dragon',1)] = (self.expensive,)
        rng = self.game.rng.getstate()
        with self.assertRaisesRegex(UnsupportedCard,'no legal completion'):
            self.game._forge_offer(0,'dragon',3)
        self.assertEqual(self.game.rng.getstate(),rng)
        self.assertIsNone(self.game.pending_choice)

    def test_malformed_component_fails_before_sampling(self):
        bad = ForgePart('forge_cheap',operations=(('when_state','ready',('draw',True)),),source='synthetic fixture')
        self.game.forge_contracts[('dragon',1)] = (bad,)
        rng = self.game.rng.getstate()
        with self.assertRaisesRegex(UnsupportedCard,'forge.*operand type'):
            self.game._forge_offer(0,'dragon',0)
        self.assertEqual(self.game.rng.getstate(),rng)
        self.assertIsNone(self.game.pending_choice)

    def reject_before_offer(self,part):
        self.game.forge_contracts[('dragon',1)]=(part,)
        rng=self.game.rng.getstate()
        with self.assertRaises(UnsupportedCard):self.game._forge_offer(0,'dragon',0)
        self.assertEqual(self.game.rng.getstate(),rng)
        self.assertIsNone(self.game.pending_choice)

    def test_unknown_direct_and_death_effects_fail_before_sampling(self):
        for field in ('operations','death_operations'):
            with self.subTest(field=field):
                self.reject_before_offer(ForgePart('forge_cheap',source='synthetic fixture',**{field:(('invented_effect',),)}))

    def test_unknown_trigger_and_end_effects_fail_before_sampling(self):
        for intrinsic in (('trigger',('spell_cast',(('invented_effect',),))),('end_effects',(('invented_effect',),))):
            with self.subTest(intrinsic=intrinsic):
                self.reject_before_offer(ForgePart('forge_cheap',source='synthetic fixture',intrinsics=(intrinsic,)))

    def test_nested_kindred_effects_fail_before_sampling(self):
        for nested in (('invented_effect',),('copy_self_right',True)):
            with self.subTest(nested=nested):
                self.reject_before_offer(ForgePart('forge_cheap',source='synthetic fixture',operations=(('kindred',(nested,)),)))

    def test_malformed_generation_modifiers_fail_before_sampling(self):
        from expanded.generation_cards import pool
        for modifiers in ((('set_cost',True),),(('cost_delta',1),('cost_delta',2)),(('unknown_modifier',1),)):
            with self.subTest(modifiers=modifiers):
                self.reject_before_offer(ForgePart('forge_cheap',source='synthetic fixture',operations=(('generate_random',pool(card_type='MINION'),1,'hand',modifiers),)))

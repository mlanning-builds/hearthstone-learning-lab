"""Minimal engine-only reproductions; failure artifacts lack complete replay actions."""
import unittest
from unittest.mock import patch
from expanded import Action
from engine.cards import UnsupportedCard
from expanded.herald import SOLDIERS
import test_expanded_generation as fixtures


class TrialEngineFailureTests(unittest.TestCase):
    def game(self):
        return fixtures.GenerationTests().game()

    def repeated_ooze(self, cid, seed):
        g=self.game();g.rng.seed(seed)
        victim=g._summon(0,cid);a,h=victim.attack,victim.health
        card=g._add(0,'TLC_252')
        # Xavius can grant the doubled Battlecry gift to the actual Ooze.
        g._dark_attach(0,card,'EDR_100t7')
        g.step(next(x for x in g.legal_actions() if x.kind=='play' and x.source==card.uid and x.target==victim.uid))
        bones=[c for c in g.players[0].hand if c.card_id=='TLC_829t']
        self.assertEqual(len(bones),1)
        self.assertEqual((bones[0].rule_state['buff_attack'],bones[0].rule_state['buff_health']),(a,h))
        self.assertIsNone(g._force_live(victim.uid))
        self.assertTrue(any(e['event']=='effect_fizzled' for e in g.events))
        g.assert_invariants()

    def test_carrier_whelp_diagnostic_repeated_ooze_on_xavius(self):
        self.repeated_ooze('EDR_856',1000000051)

    def test_rogue_dagger_diagnostic_repeated_ooze_on_smuggler(self):
        self.repeated_ooze('JAIL_998',1000000033)

    def test_ooze_departed_target_does_not_create_bones_or_retarget(self):
        for departure in ('death','bounce','shuffle','replacement'):
            with self.subTest(departure=departure):
                g=self.game();m=g._summon(0,'JAIL_998');uid=m.uid
                g.players[0].board.remove(m)
                other=g._summon(0,'EDR_856')
                g._start_play_effects((('b60_bones',),),dict(owner=0,source=None,target=uid,bonus=0,lifesteal=False))
                self.assertFalse(g.players[0].hand);self.assertGreater(other.health,0)

    def test_ooze_transformation_retaining_uid_uses_current_stats(self):
        g=self.game();m=g._summon(0,'JAIL_998')
        # Identity retained: the live entity's current stats, not an old snapshot.
        m.card_id='EDR_856';m.attack=4;m.health=m.max_health=6
        g._start_play_effects((('b60_bones',),),dict(owner=0,source=None,target=m.uid,bonus=0,lifesteal=False))
        self.assertEqual(g.players[0].hand[-1].rule_state['buff_health'],6)

    def test_offclass_multiclass_herald_has_known_source_and_still_rejects(self):
        g=self.game();g.players[0].hero_class='DRUID';c=g._add(0,'CATA_497')
        before=g.observe(0);seen=[];original=g._herald
        def capture(owner,keyword=None,source_card_id=None):
            seen.append(source_card_id)
            return original(owner,keyword,source_card_id)
        with patch.object(g,'_herald',side_effect=capture):
            with self.assertRaisesRegex(UnsupportedCard,'source_card_id=CATA_497'):
                g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid))
        self.assertEqual(seen,['CATA_497']);self.assertEqual(g.observe(0),before)

    def test_offclass_single_class_herald_keeps_real_source(self):
        g=self.game();g.players[0].hero_class='DRUID';c=g._add(0,'CATA_160')
        g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid))
        self.assertIn(SOLDIERS['WARRIOR'],[m.card_id for m in g.players[0].minions])

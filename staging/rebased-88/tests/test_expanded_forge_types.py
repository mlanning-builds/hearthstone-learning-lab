"""Compiled Nefarius identity participates in ordinary tribe interactions."""
from copy import deepcopy
import unittest
from unittest.mock import patch
import test_expanded_forge_intrinsics as intrinsic_fixtures
from expanded.selectors import has_tribe,TRIBES
from expanded.minion_forge import ForgePart


class ForgeTypeTests(unittest.TestCase):
    def setUp(self):
        self.fixture=intrinsic_fixtures.ForgeIntrinsicTests('test_clone_keeps_independent_composite_properties')
        self.fixture.setUp();self.addCleanup(self.fixture.doCleanups)
        self.game=self.fixture.game

    def craft(self,all_types=True,reborn=False):
        cid='DINO_435' if all_types else 'CORE_NEW1_023'
        first=ForgePart(cid,keywords=('REBORN',) if reborn else (),source='explicit identity fixture')
        second=ForgePart('EDR_851t',source='explicit identity fixture')
        choice=dict(kind='forge_part',forge_kind='dragon',owner=0,discount=0,first=first,parts=[second])
        self.game._forge_choice(choice,dict(card_id=second.card_id))
        return self.game.players[0].hand[-1]

    def test_all_types_in_hand_without_catalog_mutation(self):
        before=deepcopy(self.game.cards['CATA_470t1']);card=self.craft()
        for tribe in TRIBES:self.assertTrue(self.game._matches_filter(card,(('tribe','eq',tribe),)))
        self.assertEqual(self.game.cards['CATA_470t1'],before)
        self.assertFalse(has_tribe(self.game.cards['CATA_470t1'],'MURLOC'))

    def test_regular_creation_has_only_printed_undead_dragon(self):
        card=self.craft(False)
        self.assertEqual(set(self.game._card_data(card)['races']),{'UNDEAD','DRAGON'})
        self.assertFalse(has_tribe(self.game._card_data(card),'BEAST'))

    def test_targeting_and_silence_keep_compiled_types(self):
        m=self.fixture.play(self.craft());self.game._silence(m)
        self.assertTrue(has_tribe(self.game._card_data(m),'MURLOC'))
        self.assertIn(m.uid,self.game._targets_for('CATA_470t1',0,mode_override='friendly_beast'))
        self.assertIn(m.uid,self.game._targets_for('CATA_470t1',0,mode_override='friendly_undead'))

    def test_copies_and_fresh_replay_preserve_types(self):
        card=self.craft();copied=self.game._copy_card(card)
        m=self.fixture.play(card);self.game._silence(m)
        replay=self.game._fresh_replay_card(m)
        for value in (copied,replay):self.assertTrue(has_tribe(self.game._card_data(value),'PIRATE'))
        fresh=self.game._summon(0,m.card_id,entry_source=m,entry_origin='resummon')
        self.assertTrue(has_tribe(self.game._card_data(fresh),'PIRATE'))

    def test_reborn_preserves_all_identity(self):
        m=self.fixture.play(self.craft(reborn=True));m.health=0;self.game._settle(allow_event_choices=True)
        fresh=next(x for x in self.game.players[0].minions if x.card_id==m.card_id)
        self.assertNotEqual(fresh.uid,m.uid)
        self.assertTrue(has_tribe(self.game._card_data(fresh),'ELEMENTAL'))

    def test_tribal_damage_and_group_assignment_use_physical_identity(self):
        m=self.fixture.play(self.craft());self.game._summon(0,'EDR_480')
        self.assertEqual(self.game._outgoing_tribal_damage(m,3),6)
        self.assertEqual(self.game._distinct_type_group([m],1),[m])

    def test_play_and_death_events_snapshot_all_types(self):
        events=[];original=self.game._queue_event
        def capture(kind,**data):events.append((kind,deepcopy(data)));return original(kind,**data)
        with patch.object(self.game,'_queue_event',capture):
            m=self.fixture.play(self.craft());m.health=0;self.game._settle(allow_event_choices=True)
        for kind in ('minion_played','minion_died'):
            event=next(data for name,data in events if name==kind and data.get('source')==m.uid)
            self.assertEqual(event['printed_tribes'],('ALL',))
            self.assertTrue(has_tribe(self.game._event_card_data(event),'TOTEM'))
        self.assertIn('ALL',self.game.players[0].played_tribes)

    def test_summon_listener_sees_all_type_creation(self):
        card=self.craft();listener=self.game._summon(0,'EDR_851t')
        self.fixture.play(card);m=next(x for x in self.game.players[0].minions if x.card_id==card.card_id)
        event=dict(owner=0,source=m.uid,card_id=m.card_id,printed_tribes=('ALL',))
        self.assertTrue(self.game._summon_trigger_matches(('summon','friendly','DEMON'),'minion_summoned',event,listener))

    def test_transform_replaces_compiled_identity(self):
        m=self.fixture.play(self.craft());new=self.game._transform(m,'EDR_851t')
        self.assertFalse(has_tribe(self.game._card_data(new),'MURLOC'))

    def test_tribal_draw_and_discount_use_physical_definition(self):
        card=self.craft();p=self.game.players[0];p.hand.remove(card);p.deck=[card]
        self.assertTrue(self.game._discount_matches(dict(selector='PIRATE'),card))
        drawn=self.game._draw(0,lambda data:has_tribe(data,'TOTEM'))
        self.assertIs(drawn,card)

    def test_all_type_kindred_matches_previous_beast(self):
        card=self.craft();self.game.players[0].previous_tribes={'BEAST'}
        self.assertTrue(self.game._kindred(card,0))

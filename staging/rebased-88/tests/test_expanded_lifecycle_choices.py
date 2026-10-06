"""Prepared user-run death/turn continuation scenarios, using synthetic rules."""
import copy
import unittest
from unittest.mock import patch
from expanded import Game, Action, random_deck
from expanded.game import Card
from expanded.cards import DEATH_EFFECTS,START_EFFECTS,END_EFFECTS,RULES
from engine.cards import UnsupportedCard


class LifecycleChoiceTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('MAGE',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        for p in self.g.players:
            p.hand=[];p.deck=['CORE_CS2_029','CORE_CS2_023','CORE_EX1_506'];p.mana=10
        self.cid='Core_CS2_200'

    def patched(self,table,values):
        p=patch.dict(table,values);p.start();self.addCleanup(p.stop)

    def choose(self,g=None): (g or self.g).step(Action('choose',choices=(0,)))

    def death_choice(self,ops=None,reborn=False):
        self.patched(DEATH_EFFECTS,{self.cid:ops or [('armor',2),('discover_deck',),('armor',5)]})
        m=self.g._summon(0,self.cid)
        if reborn:m.keywords.add('REBORN')
        m.health=0;self.g._settle()
        return m

    def test_death_choice_resumes_without_repeating_corpse_or_effect(self):
        m=self.death_choice();corpses=self.p.corpses
        self.assertNotIn(m,self.p.board);self.assertEqual(self.p.armor,2)
        self.assertIsNotNone(self.g._death_frame)
        self.choose()
        self.assertEqual(self.p.armor,7);self.assertEqual(self.p.corpses,corpses)
        self.assertIsNone(self.g._death_frame)
        self.assertEqual(sum(e['event']=='death' and e.get('entity')==m.uid for e in self.g.events),1)

    def test_reborn_waits_for_deathrattle_choice(self):
        self.death_choice(reborn=True)
        self.assertEqual(self.p.board,[])
        self.choose()
        self.assertEqual(len(self.p.board),1)
        self.assertEqual(self.p.minions[0].health,1)
        self.assertNotIn('REBORN',self.p.minions[0].keywords)

    def test_multiple_deathrattles_wait_in_order(self):
        self.patched(DEATH_EFFECTS,{self.cid:[('discover_deck',),('armor',2)]})
        a=self.g._summon(0,self.cid);b=self.g._summon(0,self.cid)
        a.health=b.health=0;self.g._settle()
        self.assertEqual(self.p.board,[])
        self.choose();self.assertEqual(self.p.armor,2)
        self.assertIsNotNone(self.g.pending_choice)
        self.choose();self.assertEqual(self.p.armor,4)
        self.assertIsNone(self.g._death_frame)

    def test_full_board_after_deathrattle_blocks_reborn(self):
        self.death_choice([('discover_deck',),('summon','CS2_101t',7)],reborn=True)
        self.choose()
        self.assertEqual(len(self.p.board),7)
        self.assertTrue(all(m.card_id=='CS2_101t' for m in self.p.board))

    def test_death_frame_copy_replays_deterministically(self):
        self.death_choice(reborn=True);clone=copy.deepcopy(self.g)
        self.choose();self.choose(clone)
        self.assertEqual(self.g.observe(0),clone.observe(0))
        self.assertEqual(self.g.rng.getstate(),clone.rng.getstate())

    def test_failed_death_resumption_rolls_back(self):
        self.death_choice([('discover_deck',),('armor',3),('unsupported',)])
        before=copy.deepcopy(self.g.__dict__)
        with self.assertRaises(UnsupportedCard):self.choose()
        self.assertEqual(self.g._death_frame,before['_death_frame'])
        self.assertEqual(self.g.players,before['players'])
        self.assertEqual(self.g.pending_choice,before['pending_choice'])
        self.assertFalse(self.g._settling)

    def test_lethal_deathrattle_clears_continuations(self):
        self.death_choice([('discover_deck',),('damage_own_hero',100),('armor',9)],reborn=True)
        self.choose()
        self.assertTrue(self.g.terminal);self.assertEqual(self.p.board,[])
        self.assertIsNone(self.g._death_frame);self.assertIsNone(self.g._turn_frame)
        self.assertIsNone(self.g.pending_choice)

    def test_start_choice_delays_normal_draw_and_does_not_repeat_mana(self):
        self.patched(START_EFFECTS,{self.cid:('owner',[('discover_deck',),('armor',4)])})
        self.g._summon(1,self.cid)
        self.g.step(Action('end'))
        self.assertEqual(self.g.current,1);mana=self.q.mana;turn=self.g.turn
        self.assertEqual(self.q.hand,[]);self.assertEqual(len(self.q.deck),3)
        self.choose()
        self.assertEqual(len(self.q.hand),2);self.assertEqual(len(self.q.deck),1)
        self.assertEqual(self.q.armor,4);self.assertEqual(self.q.mana,mana)
        self.assertEqual(self.g.turn,turn);self.assertIsNone(self.g._turn_frame)

    def test_end_choice_delays_switch_cleanup_and_next_draw(self):
        self.patched(END_EFFECTS,{self.cid:[('discover_deck',),('armor',4)]})
        self.g._summon(0,self.cid);self.p.temporary_attack=2
        self.g.step(Action('end'))
        self.assertEqual(self.g.current,0);self.assertEqual(self.p.temporary_attack,2)
        self.assertEqual(self.q.hand,[])
        self.choose()
        self.assertEqual(self.g.current,1);self.assertEqual(self.p.temporary_attack,0)
        self.assertEqual(self.p.armor,4);self.assertEqual(len(self.q.hand),1)
        self.assertIsNone(self.g._turn_frame)

    def test_two_end_choices_do_not_switch_early(self):
        self.patched(END_EFFECTS,{self.cid:[('discover_deck',),('discover_deck',)]})
        self.g._summon(0,self.cid);self.g.step(Action('end'))
        self.choose();self.assertEqual(self.g.current,0)
        self.choose();self.assertEqual(self.g.current,1)
        self.assertEqual(len(self.p.hand),2);self.assertEqual(len(self.q.hand),1)

    def test_end_turn_death_choice_resumes_turn(self):
        self.patched(END_EFFECTS,{self.cid:[('damage_self',100)]})
        self.patched(DEATH_EFFECTS,{self.cid:[('discover_deck',),('armor',3)]})
        self.g._summon(0,self.cid);self.g.step(Action('end'))
        self.assertIsNotNone(self.g._death_frame);self.assertIsNotNone(self.g._turn_frame)
        self.assertEqual(self.g.current,0)
        self.choose()
        self.assertEqual(self.p.armor,3);self.assertEqual(self.g.current,1)
        self.assertIsNone(self.g._death_frame);self.assertIsNone(self.g._turn_frame)

    def test_end_snapshot_does_not_add_new_sources(self):
        self.patched(END_EFFECTS,{self.cid:[('summon',self.cid,1),('armor',2)]})
        self.g._summon(0,self.cid);self.g.step(Action('end'))
        self.assertEqual(len(self.p.board),2);self.assertEqual(self.p.armor,2)

    def test_lethal_start_prevents_normal_draw(self):
        self.patched(START_EFFECTS,{self.cid:('owner',[('discover_deck',),('damage_own_hero',100)])})
        self.g._summon(1,self.cid);self.g.step(Action('end'));self.choose()
        self.assertTrue(self.g.terminal);self.assertEqual(len(self.q.hand),1)
        self.assertIsNone(self.g._turn_frame)

    def test_failed_end_choice_restores_turn_and_choice(self):
        self.patched(END_EFFECTS,{self.cid:[('discover_deck',),('unsupported',)]})
        self.g._summon(0,self.cid);self.g.step(Action('end'))
        before=copy.deepcopy(self.g.__dict__)
        with self.assertRaises(UnsupportedCard):self.choose()
        self.assertEqual(self.g._turn_frame,before['_turn_frame'])
        self.assertEqual(self.g.pending_choice,before['pending_choice'])
        self.assertEqual(self.g.current,0)

    def test_choice_frames_are_private(self):
        self.death_choice();other=self.g.observe(1)
        self.assertNotIn('_death_frame',other);self.assertNotIn('_turn_frame',other)
        self.assertNotIn('options',other['pending_choice'])

    def test_card_continues_after_death_choice(self):
        self.patched(DEATH_EFFECTS,{self.cid:[('discover_deck',),('armor',3)]})
        self.patched(RULES,{'CORE_DS1_184':('none',[('area_damage','all_minions',100),('armor',7)])})
        self.g._summon(0,self.cid)
        card=Card(self.g._new_id(),'CORE_DS1_184');self.p.hand.append(card)
        self.g.step(Action('play',card.uid));self.assertEqual(self.p.armor,0)
        self.choose();self.assertEqual(self.p.armor,10)
        self.assertIsNone(self.g.pending_frame);self.assertIsNone(self.g.pending_play)

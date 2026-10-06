"""Physical selection, vanilla absorption and deck spell consumer boundaries."""
import unittest
from copy import deepcopy
from expanded import Game,Action,random_deck
from engine.game import Card
from engine.cards import UnsupportedCard

class SpellConsumerTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('SHAMAN',31),random_deck('ROGUE',53)],seed=71)
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:
            p.hand=[];p.board=[];p.deck=[];p.health=30;p.mana=p.max_mana=10;p.armor=0
        return g
    def play(self,g,cid):
        c=g._add(0,cid)
        action=next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid)
        g.step(action)
        return next((m for m in g.players[0].minions if m.card_id==cid),None)
    def choose(self,g,uid):
        index=next(i for i,o in enumerate(g.pending_choice['options']) if o['uid']==uid)
        g.step(Action('choose',choices=(index,)))
    def test_cloudstrider_empty_hand_has_no_choice(self):
        g=self.game();m=self.play(g,'CATA_563');self.assertIsNone(g.pending_choice)
        m.health=0;g._settle();self.assertEqual([p.health for p in g.players],[30,30])
    def test_absorption_uses_current_cost_and_only_spells(self):
        g=self.game();spell=g._add(0,'CORE_CS2_029');spell.cost_delta=2
        minion=g._add(0,'AT_037t');cheap=g._add(0,'CORE_CS2_029');cheap.set_cost=1
        self.play(g,'CATA_563');self.assertEqual([o['uid'] for o in g.pending_choice['options']],[cheap.uid])
        self.choose(g,cheap.uid);self.assertIn(spell,g.players[0].hand);self.assertIn(minion,g.players[0].hand)
    def test_absorption_removes_exact_copy_without_discard(self):
        g=self.game();a=g._add(0,'CORE_CS2_029');b=g._add(0,'CORE_CS2_029');m=self.play(g,'CATA_563')
        self.choose(g,b.uid);self.assertIn(a,g.players[0].hand);self.assertNotIn(b,g.players[0].hand)
        self.assertFalse(g.players[0].discard_history);self.assertEqual(g.players[0].mana,7)
        self.assertEqual(m.rule_state['absorbed_spell_id'],'CORE_CS2_029')
    def test_absorbed_spell_drops_attached_spell_damage(self):
        g=self.game();c=g._add(0,'CORE_CS2_029');c.spell_damage_bonus=5;m=self.play(g,'CATA_563');self.choose(g,c.uid)
        m.health=0;g._settle();self.assertEqual(sum(p.health for p in g.players),54)
    def test_silence_removes_absorbed_identity_and_death_effect(self):
        g=self.game();c=g._add(0,'CORE_CS2_029');m=self.play(g,'CATA_563');self.choose(g,c.uid)
        g._silence(m);m.health=0;g._settle();self.assertEqual(sum(p.health for p in g.players),60)
    def test_board_copy_keeps_absorbed_identity(self):
        g=self.game();c=g._add(0,'CORE_CS2_029');m=self.play(g,'CATA_563');self.choose(g,c.uid)
        clone=g._summon(0,m.card_id,copy_from=m);g._silence(m)
        self.assertEqual(clone.rule_state['absorbed_spell_id'],'CORE_CS2_029')
    def test_bounce_does_not_keep_absorbed_enchantment(self):
        g=self.game();c=g._add(0,'CORE_CS2_029');m=self.play(g,'CATA_563');self.choose(g,c.uid)
        g._bounce(m);returned=g.players[0].hand[-1]
        self.assertNotIn('absorbed_spell_id',getattr(returned,'rule_state',{}))
    def test_absorbed_identity_is_owner_visible_only_and_detached(self):
        g=self.game();c=g._add(0,'CORE_CS2_029');m=self.play(g,'CATA_563')
        self.assertNotIn('options',g.observe(1)['pending_choice']);self.choose(g,c.uid)
        own=g.observe(0)['players'][0]['board'][0];enemy=g.observe(1)['players'][0]['board'][0]
        self.assertEqual(own['rule_state']['absorbed_spell_id'],'CORE_CS2_029')
        self.assertNotIn('absorbed_spell_id',enemy['rule_state']);own['rule_state'].clear()
        self.assertIn('absorbed_spell_id',m.rule_state)
    def test_treasuregill_empty_deck_does_not_fatigue(self):
        g=self.game();m=self.play(g,'TLC_438');self.assertIsNotNone(m);self.assertEqual(g.players[0].fatigue,0)
    def test_deck_cast_prefers_source_even_when_spell_kills_it(self):
        g=self.game();c=Card(g._new_id(),'CORE_CS2_024');g.players[0].deck=[c]
        self.assertIsNone(self.play(g,'TLC_438'));self.assertFalse(g.players[0].deck)
        self.assertEqual(sum(p.health for p in g.players),60);self.assertFalse(g.players[0].hand)
    def test_deck_cost_filter_uses_physical_cost(self):
        g=self.game();c=Card(g._new_id(),'CORE_CS2_029');c.set_cost=2;g.players[0].deck=[c,'CORE_CS2_029','CS3_020']
        self.play(g,'TLC_438');self.assertEqual(g.players[0].deck,['CORE_CS2_029','CS3_020'])
    def test_deck_cast_preserves_spell_damage_bonus(self):
        g=self.game();c=Card(g._new_id(),'TIME_600');c.set_cost=2;c.spell_damage_bonus=3;g.players[0].deck=[c]
        source=g._summon(0,'TLC_438');source.health=source.max_health=20
        g._start_play_effects([('cast_deck_spell',2,'prefer_source')],dict(owner=0,source=source,target=0,bonus=0,lifesteal=False))
        self.assertEqual(source.health,14)
    def test_nonmatching_spell_is_not_removed(self):
        g=self.game();g.players[0].deck=['CORE_CS2_029'];m=self.play(g,'TLC_438')
        self.assertIsNotNone(m);self.assertEqual(g.players[0].deck,['CORE_CS2_029'])
    def test_unsupported_selected_spell_rolls_back_instead_of_pool_filtering(self):
        g=self.game();g.players[0].deck=['CORE_RLK_567'];c=g._add(0,'TLC_438')
        action=next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid)
        before=g.observe(0)
        with self.assertRaises(UnsupportedCard):g.step(action)
        self.assertEqual(g.observe(0),before)

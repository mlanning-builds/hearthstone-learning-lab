import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class FrozenCopyTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('WARRIOR',31),random_deck('MAGE',53)],seed=71)
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:p.hand=[];p.deck=['CORE_CS2_029']*20;p.mana=p.max_mana=10
        return g
    def test_frozen_copy_cannot_attack_even_with_rush(self):
        g=self.game();source=g._summon(0,'CS3_025');g._freeze(source.uid);enemy=g._summon(1,'CS3_025')
        copy=g._summon(0,source.card_id,copy_from=source)
        self.assertGreaterEqual(copy.frozen_until,0)
        self.assertFalse(any(a.kind=='attack' and a.source==copy.uid for a in g.legal_actions()))
    def test_nablya_granting_rush_does_not_remove_frozen(self):
        g=self.game();source=g._summon(0,'DINO_132');source.health=4;g._freeze(source.uid);g._summon(1,'CS3_025')
        c=Card(g._new_id(),'TLC_624');g.players[0].hand=[c];g.step(Action('play',c.uid,position=1));copy=g.players[0].minions[-1]
        self.assertIn('RUSH',copy.keywords);self.assertGreaterEqual(copy.frozen_until,0)
        self.assertFalse(any(a.kind=='attack' and a.source==copy.uid for a in g.legal_actions()))
    def test_silencing_copy_does_not_thaw_original(self):
        g=self.game();source=g._summon(0,'CS3_025');g._freeze(source.uid);copy=g._summon(0,source.card_id,copy_from=source)
        g._silence(copy);self.assertEqual(copy.frozen_until,-1);self.assertGreaterEqual(source.frozen_until,0)
    def test_unfrozen_source_produces_unfrozen_copy(self):
        g=self.game();source=g._summon(0,'CS3_025');copy=g._summon(0,source.card_id,copy_from=source)
        self.assertEqual(copy.frozen_until,-1)
    def test_frozen_state_visible_for_both_viewers(self):
        g=self.game();source=g._summon(0,'CS3_025');g._freeze(source.uid);copy=g._summon(0,source.card_id,copy_from=source)
        for viewer in (0,1):
            entity=next(m for m in g.observe(viewer)['players'][0]['board'] if m['uid']==copy.uid)
            self.assertGreaterEqual(entity['frozen_until'],0)

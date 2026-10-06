"""Outcast spell bodies resolve without treating an internal cast as a hand play."""
import unittest
from expanded import Game,Action,random_deck
from engine.game import Card

class CastOutcastTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('DEMONHUNTER',31),random_deck('ROGUE',53)],seed=71)
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:
            p.hand=[];p.board=[];p.deck=['CORE_CS2_029']*20;p.health=30;p.mana=p.max_mana=10
        return g
    def cast(self,g,cid,mode):
        c=Card(g._new_id(),cid)
        if mode=='fixed':op=('cast_fixed_spell',cid,'random')
        elif mode=='detached':op=('cast_physical_spell',c,'random')
        else:
            getattr(g.players[0],mode).append(c);op=('cast_zone_spell',mode,c.uid,'random')
        g._start_play_effects([op],dict(owner=0,source=None,target=0,bonus=0,lifesteal=False,outcast=True))
    def test_spectral_sight_draws_only_base_card_for_each_cast_origin(self):
        for mode in ('fixed','detached','hand','deck'):
            with self.subTest(mode=mode):
                g=self.game();self.cast(g,'CORE_BT_491',mode)
                self.assertEqual(len(g.players[0].hand),1);self.assertEqual(g.players[0].mana,10)
    def test_flash_flood_hits_edges_once_for_each_origin(self):
        for mode in ('fixed','detached','hand','deck'):
            with self.subTest(mode=mode):
                g=self.game();minions=[g._summon(1,'CS3_020') for _ in range(3)]
                for m in minions:m.health=m.max_health=20
                self.cast(g,'CATA_533',mode);self.assertEqual([m.health for m in minions],[15,20,15])
    def test_feasting_raptors_do_not_gain_outcast_enchantment(self):
        for mode in ('fixed','detached','hand','deck'):
            with self.subTest(mode=mode):
                g=self.game();self.cast(g,'DINO_136',mode)
                self.assertEqual(len(g.players[0].minions),3)
                self.assertTrue(all(not any(e['keyword']=='IMMUNE_WHILE_ATTACKING' for e in m.temporary_keywords) for m in g.players[0].minions))
    def test_real_edge_play_still_draws_two(self):
        g=self.game();c=g._add(0,'CORE_BT_491')
        g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid))
        self.assertEqual(len(g.players[0].hand),2)
    def test_real_middle_play_draws_one(self):
        g=self.game();g._add(0,'TOKEN_COIN');c=g._add(0,'CORE_BT_491');g._add(0,'TOKEN_COIN')
        g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid))
        self.assertEqual(len(g.players[0].hand),3)
    def test_unknown_outcast_child_is_rejected_even_when_inactive(self):
        g=self.game();self.assertFalse(g._supports_internal_operations([('outcast_operation',('unknown_effect',))]))

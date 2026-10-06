"""Production-path checks: no registry patches or synthetic generation pools."""
from copy import deepcopy
import unittest
from expanded import Game, Action
from expanded.cards import COLLECTIBLE_IDS, TOKEN_IDS, registry
from expanded.decks import Deck, eligible, validate
from expanded.fabled_decks import BUNDLES
from expanded.evolving_locations import TIMELINES

ADMITTED={'CORE_DAL_575','TIME_044','TIME_810'}

class ClosedAdmissionTests(unittest.TestCase):
    def deck(self,hero,root=None):
        records=registry()
        ids=[cid for cid in sorted(COLLECTIBLE_IDS)
             if cid not in BUNDLES and cid!=root and eligible(records[cid],hero,(0,0,0))]
        d=Deck(hero,tuple(([root] if root else [])+ids[:29 if root else 30]))
        self.assertEqual(validate(d),[])
        return d

    def game(self,hero,root):
        g=Game([self.deck(hero,root),self.deck('WARRIOR')],seed=71)
        g.step(Action('mulligan'));g.step(Action('mulligan'));g.current=0
        for p in g.players:
            p.hand=[];p.board=[];p.mana=p.max_mana=10;p.health=30;p.armor=0
        return g

    def play(self,g,cid,target=0):
        c=g._add(0,cid)
        a=next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==target)
        g.step(a)
        return c

    def test_closed_collectibles_and_all_location_stages_have_pinned_metadata(self):
        records=registry()
        self.assertTrue(ADMITTED<=COLLECTIBLE_IDS)
        for root in ('TIME_044','TIME_810'):
            self.assertTrue(set(TIMELINES[root][1:])<=TOKEN_IDS)
            self.assertTrue(set(TIMELINES[root])<=records.keys())

    def test_dependency_report_traverses_every_future_location_stage(self):
        from expanded.dependencies import current_dependency_report
        report=current_dependency_report()
        self.assertFalse(report['missing_ids'])
        self.assertIn('evolving_advance',report['checked_operations'])
        from expanded.dependencies import dependency_report
        report=dependency_report({'TIME_044':[('evolving_advance','TIME_044t1')],
                                  'TIME_044t1':[('evolving_advance','TIME_044t2')]},
                                 {'TIME_044','TIME_044t1'},['TIME_044'])
        self.assertEqual(report['missing_paths'],[dict(root='TIME_044',missing='TIME_044t2',
                         path=['TIME_044','TIME_044t1','TIME_044t2'])])

    def test_khadgar_paid_battlecry_summons_twice(self):
        g=self.game('MAGE','CORE_DAL_575');self.play(g,'CORE_DAL_575')
        self.play(g,'CORE_EX1_506')
        self.assertEqual([m.card_id for m in g.players[0].minions].count('TOKEN_SCOUT'),2)

    def test_khadgar_hero_power_is_not_doubled(self):
        g=self.game('MAGE','CORE_DAL_575');self.play(g,'CORE_DAL_575')
        g.players[0].hero_class='PALADIN';g.players[0].power_used=False
        g.step(next(a for a in g.legal_actions() if a.kind=='power'))
        self.assertEqual([m.card_id for m in g.players[0].minions].count('CS2_101t'),1)

    def test_multiple_khadgars_respect_board_capacity(self):
        g=self.game('MAGE','CORE_DAL_575')
        g._summon(0,'CORE_DAL_575');g._summon(0,'CORE_DAL_575')
        self.play(g,'CORE_EX1_506')
        self.assertEqual(len(g.players[0].board),7)
        self.assertEqual([m.card_id for m in g.players[0].minions].count('TOKEN_SCOUT'),4)

    def test_khadgar_silence_removes_multiplier(self):
        g=self.game('MAGE','CORE_DAL_575');self.play(g,'CORE_DAL_575')
        g._silence(g.players[0].minions[0]);self.play(g,'CORE_EX1_506')
        self.assertEqual([m.card_id for m in g.players[0].minions].count('TOKEN_SCOUT'),1)

    def test_paid_gnomeregan_completes_all_stages_in_ordinary_registry(self):
        g=self.game('PALADIN','TIME_044');self.play(g,'TIME_044')
        loc=g.players[0].locations[0];uid=loc.uid;m=g._summon(0,'NEW1_034')
        for n in range(3):
            loc.ready_turn=g.turn
            g.step(next(a for a in g.legal_actions() if a.kind=='activate' and a.source==uid and a.target==m.uid))
            if n<2:self.assertEqual(loc.card_id,TIMELINES['TIME_044'][n+1])
        self.assertNotIn(loc,g.players[0].board)
        self.assertEqual((m.attack,m.max_health),(10,5))
        self.assertIn('DIVINE_SHIELD',m.keywords)
        m.health=0;g._settle();self.assertEqual(g.players[1].health,26)

    def test_paid_silvermoon_can_advance_on_empty_board_and_replay_clone(self):
        g=self.game('HUNTER','TIME_810');self.play(g,'TIME_810');loc=g.players[0].locations[0]
        g.step(next(a for a in g.legal_actions() if a.kind=='activate' and a.source==loc.uid))
        self.assertEqual(loc.card_id,'TIME_810t1');self.assertEqual(loc.durability,2)
        g._summon(1,'NEW1_034');loc.ready_turn=g.turn;clone=deepcopy(g)
        a=next(a for a in g.legal_actions() if a.kind=='activate' and a.source==loc.uid)
        g.step(a);clone.step(a)
        self.assertEqual(g.observe(0),clone.observe(0));self.assertEqual(g.players[1].health,27)
        self.assertEqual(loc.card_id,'TIME_810t2')

    def test_gnomeregan_cooldown_survives_identity_transition(self):
        g=self.game('PALADIN','TIME_044');self.play(g,'TIME_044');loc=g.players[0].locations[0]
        m=g._summon(0,'NEW1_034')
        g.step(next(a for a in g.legal_actions() if a.kind=='activate' and a.target==m.uid))
        self.assertFalse(any(a.kind=='activate' and a.source==loc.uid for a in g.legal_actions()))

if __name__=='__main__':unittest.main()

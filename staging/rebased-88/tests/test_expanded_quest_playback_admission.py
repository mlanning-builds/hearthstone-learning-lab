"""Paid production-registry paths for compound quests and card playback."""
import unittest
import test_expanded_generation as fixtures
from expanded import cards,Action
from expanded.imbue_consumers import WILD_POOL,WILD_GODS

class QuestPlaybackAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.g=fixtures.GenerationTests().game()
        self.p,self.q=self.g.players

    def play(self,cid,target=0):
        self.p.mana=self.p.max_mana=10
        c=self.g._add(0,cid);cost=self.g._cost(c,0)
        self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==target))
        if self.g.current==0:self.assertEqual(self.p.mana,10-cost)
        self.g.assert_invariants()
        return c

    def test_equilibrium_progresses_with_real_holy_and_shadow_spells(self):
        self.play('TLC_817')
        for _ in range(4):self.play('CS1_130',self.g._summon(1,'CS2_182').uid)
        self.assertEqual([c.card_id for c in self.p.hand],['TLC_817t3'])
        for _ in range(4):self.play('EX1_309',self.g._summon(1,'CS2_182').uid)
        self.assertIsNone(self.p.quest)
        self.assertEqual([c.card_id for c in self.p.hand],['TLC_817t5'])
        self.play('TLC_817t5')
        self.assertEqual([m.card_id for m in self.p.minions],['TLC_817t5']*2)

    def test_forbidden_sequence_real_discover_cards_deliver_one_weapon(self):
        self.play('TLC_460')
        for i in range(8):
            self.play('TLC_442');self.g.step(Action('choose',choices=(0,)))
            if i<7:self.p.hand=[]
        self.assertIsNone(self.p.quest)
        self.assertEqual(sum(c.card_id=='TLC_460t' for c in self.p.hand),1)

    def test_origin_stone_real_deck_discover_plays_unchosen_cards(self):
        self.play('TLC_460t');self.p.deck=['CORE_EX1_162','TOKEN_COIN','CORE_CS2_029']
        self.play('TLC_515');options=self.g.pending_choice['options'];pick=next(i for i,o in enumerate(options) if o['card_id']=='CORE_CS2_029')
        self.g.step(Action('choose',choices=(pick,)))
        self.assertEqual(self.p.weapon['durability'],7)
        self.assertIn('CORE_EX1_162',[m.card_id for m in self.p.minions])
        self.assertIn('CORE_CS2_029',[c.card_id for c in self.p.hand])

    def test_ruby_registered_replaces_next_heal_and_then_is_consumed(self):
        self.play('CATA_301')
        self.assertNotEqual(getattr(self.p,'ruby_until',-1),self.g.turn)
        self.g.step(next(a for a in self.g.legal_actions() if a.kind=='activate'))
        target=self.g._summon(1,'CS2_182')
        self.play('TRL_128',target.uid);self.assertEqual(target.health,2)
        self.play('TRL_128',target.uid);self.assertEqual(target.health,5)

    def test_ohnahra_registered_end_consumes_top_three_without_drawing(self):
        self.play('EDR_031');self.p.deck=['CORE_EX1_162']*4
        self.g.step(Action('end'))
        self.assertEqual(len(self.p.deck),1)
        self.assertEqual(sum(m.card_id=='CORE_EX1_162' for m in self.p.minions),3)

    def test_slice_registered_replays_duplicate_spells_then_ends_turn(self):
        self.play('CORE_CS2_029',self.g.hero_id(1));self.play('CORE_CS2_029',self.g.hero_id(1))
        self.play('JAIL_500');self.assertEqual(self.q.health,6);self.assertEqual(self.g.current,1)
        self.assertEqual(len(self.p.played_history),3)

    def test_wild_god_production_pool_is_complete_for_both_controllers(self):
        for owner in (0,1):
            self.assertEqual(set(self.g._generation_candidates(WILD_POOL,owner)),WILD_GODS)
        self.assertEqual(len(WILD_GODS),11)

    def test_malorne_paid_production_discover_uses_all_wild_gods_and_cost_one(self):
        self.p.imbue_count=4;self.play('EDR_888')
        options=self.g.pending_choice['options'];self.assertEqual(len(options),3)
        self.assertTrue({o['card_id'] for o in options}<=WILD_GODS)
        cid=options[0]['card_id'];self.g.step(Action('choose',choices=(0,)))
        self.assertEqual(self.p.hand[-1].card_id,cid);self.assertEqual(self.g._cost(self.p.hand[-1],0),1)

    def test_dreamweaver_battlecry_uses_lifesteal_without_spell_damage(self):
        self.p.imbue_count=2;self.p.health=20;self.g._summon(0,'TID_708t');m=self.g._summon(1,'CS2_182')
        self.play('EDR_860',m.uid);self.assertEqual(m.health,1);self.assertEqual(self.p.health,24)

    def test_picker_threshold_draws_two_and_never_imbues(self):
        self.p.imbue_count=2;before=len(self.p.deck);self.play('FIR_921')
        self.assertEqual(len(self.p.deck),before-2);self.assertEqual(self.p.imbue_count,2)

if __name__=='__main__':unittest.main()

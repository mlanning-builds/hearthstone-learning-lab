"""Kindred and history regression scenarios for the rebased candidate."""
import unittest
from expanded import Game, Action, random_deck
from expanded.game import Card


class KindredHistoryTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('WARRIOR',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        for p in self.g.players:p.hand=[];p.deck=['CORE_CS2_029']*30;p.mana=p.max_mana=10

    def give(self,cid,owner=0):
        c=Card(self.g._new_id(),cid);self.g.players[owner].hand.append(c);return c

    def play(self,cid,target=0):
        c=self.give(cid);d=self.g.cards[cid]
        self.g.step(Action('play',c.uid,target,len(self.p.board) if d['type']=='MINION' else -1))
        return c

    def cycle(self):
        self.g.step(Action('end'));self.g.step(Action('end'))

    def kill(self,cid,owner=0):
        m=self.g._summon(owner,cid);m.health=0;self.g._settle();return m

    def test_kindred_requires_previous_own_turn_not_current_turn(self):
        self.play('DINO_130t')
        self.assertFalse(self.g._kindred('TLC_366',0))
        self.cycle();self.assertTrue(self.g._kindred('TLC_366',0))
        self.cycle();self.assertFalse(self.g._kindred('TLC_366',0))

    def test_summons_do_not_activate_kindred_but_dual_types_do(self):
        self.g._summon(0,'DINO_130');self.cycle()
        self.assertFalse(self.g._kindred('TLC_366',0))
        self.play('DINO_404');self.cycle()
        self.assertTrue(self.g._kindred('TLC_429',0))
        self.assertTrue(self.g._kindred('TLC_226',0))
        self.assertFalse(self.g._kindred('TLC_366',0))

    def test_countered_spell_does_not_enter_school_or_play_history(self):
        self.q.secrets.append(Card(self.g._new_id(),'CORE_EX1_287'))
        self.play('CORE_CS2_029',-2);self.cycle()
        self.assertNotIn('FIRE',self.p.previous_schools)
        self.assertEqual(self.p.played_history,[])

    def test_kindred_spell_school_is_separate_from_minion_type(self):
        self.play('CORE_CS2_024',-2);self.cycle()
        self.assertTrue(self.g._kindred('TLC_440',0))
        self.assertFalse(self.g._kindred('TLC_816',0))
        self.assertFalse(self.g._kindred('TLC_226',0))

    def test_kindred_discounts_control_payment_for_three_card_types(self):
        self.p.previous_tribes={'BEAST','DRAGON'};self.p.previous_schools={'HOLY'}
        for cid,expected in [('TLC_366',4),('TLC_600',5),('TLC_816',2)]:
            with self.subTest(cid=cid):self.assertEqual(self.g._cost(self.give(cid),0),expected)
        self.play('TLC_600',-2)
        self.assertEqual((self.p.mana,self.p.armor,self.q.health),(5,5,25))

    def test_firegill_grants_rush_to_others_only_when_kindred(self):
        old=self.g._summon(0,'Core_CS2_200');self.p.previous_tribes={'MURLOC'}
        self.play('DINO_404');source=self.p.minions[-1]
        self.assertIn('RUSH',old.keywords);self.assertNotIn('RUSH',source.keywords)

    def test_kindred_edges_ignore_locations(self):
        self.p.previous_tribes={'BEAST'}
        a=self.g._summon(1,'Core_CS2_200');self.g._place_location(1,'CORE_REV_990')
        middle=self.g._summon(1,'Core_CS2_200');b=self.g._summon(1,'Core_CS2_200')
        self.play('DINO_138')
        self.assertEqual((a.health,middle.health,b.health),(1,7,1))

    def test_chillspine_freezes_same_targets_that_take_damage(self):
        self.p.previous_tribes={'BEAST'}
        a=self.g._summon(1,'Core_CS2_200');b=self.g._summon(1,'Core_CS2_200')
        self.play('DINO_413')
        self.assertEqual((a.health,b.health),(5,5))
        self.assertGreaterEqual(a.frozen_until,0);self.assertGreaterEqual(b.frozen_until,0)

    def test_bookkeeper_copies_without_repeating_kindred(self):
        self.p.previous_tribes={'ELEMENTAL'};self.play('TLC_226')
        self.assertEqual([m.card_id for m in self.p.minions],['TLC_226']*2)
        self.p.minions[0].health=0;self.g._settle();self.assertEqual(len(self.p.hand),1)

    def test_hybridization_draws_each_cost_once_and_discounts(self):
        self.p.previous_schools={'NATURE'}
        self.p.deck=['TLC_249','DINO_130','TLC_233','EDR_492','CORE_CS2_029']
        self.play('TLC_236')
        self.assertEqual(sorted(self.g._cost(c,0) for c in self.p.hand),[0,1,2,3])
        self.assertEqual(self.p.deck,['CORE_CS2_029'])

    def test_steamfin_and_spitters_use_exact_tokens(self):
        self.p.previous_tribes={'MURLOC'};self.p.previous_schools={'SHADOW'}
        self.play('TLC_429');self.play('TLC_519')
        steam=[m for m in self.p.minions if m.card_id=='TLC_429t']
        spiders=[m for m in self.p.minions if m.card_id=='TLC_519t']
        self.assertEqual((len(steam),len(spiders)),(2,2))
        self.assertTrue(all('RUSH' in m.keywords for m in steam))
        self.assertTrue(all({'POISONOUS','STEALTH'}<=m.keywords for m in spiders))

    def test_cryosleep_kindred_draws_two(self):
        self.p.previous_schools={'FROST'};self.play('TLC_440',-2)
        self.assertEqual(self.q.health,26);self.assertEqual(len(self.p.hand),2)

    def test_caustic_fumes_settles_destroy_then_area_damage(self):
        self.p.previous_schools={'FEL'}
        egg=self.g._summon(1,'DINO_130');own=self.g._summon(0,'Core_CS2_200')
        self.play('TLC_447',egg.uid)
        self.assertEqual(own.health,5)
        self.assertEqual((self.q.minions[0].card_id,self.q.minions[0].health),('DINO_130t',2))

    def test_kodo_chooses_low_or_high_attack_by_kindred(self):
        low=self.g._summon(1,'DINO_130t');high=self.g._summon(1,'Core_CS2_200')
        self.play('TLC_454');self.assertNotIn(low,self.q.board);self.assertIn(high,self.q.board)
        self.p.mana=10;self.p.previous_tribes={'BEAST'}
        self.play('TLC_454');self.assertNotIn(high,self.q.board)

    def test_razidir_kindred_discards_only_opponent_card(self):
        self.p.previous_tribes={'DEMON'}
        own=self.give('TOKEN_COIN');enemy=self.give('CORE_CS2_029',1)
        self.play('TLC_463')
        self.assertIn(own,self.p.hand);self.assertNotIn(enemy,self.q.hand)

    def test_slagclaw_triggers_cinders_without_killing_them(self):
        self.p.previous_tribes={'ELEMENTAL'};self.play('TLC_482')
        self.assertEqual(self.q.health,26)
        self.assertEqual(sum(m.card_id=='TLC_249' for m in self.p.minions),2)

    def test_matriarch_uses_hand_buffed_attack(self):
        self.p.previous_tribes={'BEAST'};target=self.g._summon(1,'Core_CS2_200')
        c=self.give('TLC_825');c.attack_bonus=2
        expected=self.g.cards[c.card_id]['attack']+2
        self.g.step(Action('play',c.uid,target.uid,0))
        self.assertEqual(target.health,7-expected)

    def test_devilsaur_gains_destroyed_stats_only_with_kindred(self):
        self.p.previous_tribes={'BEAST'};target=self.g._summon(1,'Core_CS2_200');target.health=3
        self.play('TLC_829',target.uid);m=self.p.minions[-1];d=self.g.cards[m.card_id]
        self.assertEqual((m.attack,m.health),(d['attack']+6,d['health']+3))
        self.assertNotIn(target,self.q.board)

    def test_queen_attack_expires_after_turn(self):
        self.p.previous_tribes={'BEAST'};self.play('TLC_903')
        self.assertEqual(self.p.temporary_attack,5)
        self.g.step(Action('end'));self.assertEqual(self.p.temporary_attack,0)

    def test_dread_raptor_draws_matching_card_and_sets_cost_zero(self):
        self.p.previous_tribes={'BEAST'};self.p.deck=['DINO_130','Core_CS2_200','CORE_CS2_029']
        self.play('TLC_432')
        self.assertEqual([c.card_id for c in self.p.hand],['DINO_130'])
        self.assertEqual(self.g._cost(self.p.hand[0],0),0)

    def test_resurrection_uses_highest_eligible_friendly_death(self):
        self.kill('Core_CS2_200');self.kill('RLK_708');self.kill('FIR_778',1)
        self.play('CORE_CATA_002')
        self.assertEqual(self.p.minions[-1].card_id,'Core_CS2_200')
        self.p.mana=10;self.play('TIME_616')
        self.assertEqual(self.p.minions[-1].card_id,'RLK_708')

    def test_resuscitate_uses_cost_groups_and_grants_reborn(self):
        self.kill('TLC_249');self.kill('DINO_130');self.kill('TLC_233')
        self.p.board=[];self.play('TLC_818')
        self.assertEqual([m.card_id for m in self.p.minions],['TLC_249','DINO_130','TLC_233'])
        self.assertTrue(all('REBORN' in m.keywords for m in self.p.minions))

    def test_felhunter_resurrection_makes_two_base_copies(self):
        self.kill('DINO_130');self.p.board=[]
        self.kill('EDR_891')
        self.assertEqual([m.card_id for m in self.p.minions],['DINO_130']*2)
        self.assertTrue(all(m.health==2 for m in self.p.minions))

    def test_felbat_excludes_its_own_card(self):
        self.kill('EDR_892');self.assertEqual(self.p.board,[])
        self.kill('EDR_891');self.p.board=[];self.kill('EDR_892')
        self.assertEqual([m.card_id for m in self.p.minions],['EDR_891']*2)

    def test_kragwa_returns_only_previous_own_turn_spells(self):
        self.play('TOKEN_COIN');self.play('CORE_CS2_029',-2);self.cycle()
        self.p.hand=[];self.play('CORE_TRL_345')
        self.assertEqual([c.card_id for c in self.p.hand],['TOKEN_COIN','CORE_CS2_029'])

    def test_tolvir_repeats_played_one_cost_minions_without_battlecry(self):
        self.play('TLC_249');self.play('CORE_CS2_189',-2)
        self.p.board=[];before=self.q.health
        self.play('CATA_560')
        self.assertEqual([m.card_id for m in self.p.minions],['TLC_249','CORE_CS2_189'])
        self.assertEqual(self.q.health,before)

    def test_second_triumph_changes_from_targeted_to_area(self):
        target=self.g._summon(1,'Core_CS2_200')
        self.play('CATA_557',target.uid);self.assertEqual((target.health,self.q.health),(4,30))
        self.play('CATA_557');self.assertEqual((target.health,self.q.health),(1,27))

    def test_last_paid_cost_and_enemy_board_count_reduce_cost(self):
        self.play('CORE_CS2_029',-2)
        giant=self.give('CATA_616');self.assertEqual(self.g._cost(giant,0),5)
        for _ in range(3):self.g._summon(1,'Core_CS2_200')
        self.assertEqual(self.g._cost(self.give('TIME_715'),0),2)

    def test_fel_spell_history_reduces_felfisher(self):
        self.play('TLC_447',self.g._summon(1,'Core_CS2_200').uid)
        self.assertEqual(self.p.fel_spells_cast,1)
        self.assertEqual(self.g._cost(self.give('CATA_529'),0),5)

    def test_friendly_attacks_reduce_draw_spell_cost(self):
        m=self.g._summon(0,'Core_CS2_200');m.summoned_turn=-1
        self.g.step(Action('attack',m.uid,-2))
        self.assertEqual(self.g._cost(self.give('CATA_568'),0),8)

    def test_mograine_effect_survives_silence_and_death_and_stacks(self):
        self.play('CORE_RLK_706');first=self.p.minions[-1]
        self.g._silence(first);first.health=0;self.g._settle()
        self.p.mana=10;self.play('CORE_RLK_706');self.g.step(Action('end'))
        self.assertEqual(self.q.health,24)

    def test_spell_damage_copy_requires_actual_damage_this_turn(self):
        self.play('CORE_CS2_029',-2);self.play('CATA_483')
        self.assertEqual([m.card_id for m in self.p.minions],['CATA_483']*2)
        self.cycle();self.p.board=[];self.play('CATA_483')
        self.assertEqual(len(self.p.minions),1)

    def test_aessina_uses_friendly_death_history(self):
        self.p.death_history=['Core_CS2_200']*20
        self.play('EDR_430');self.assertEqual(self.q.health,10)

    def test_public_history_excludes_unplayed_hand_contents(self):
        secret=self.give('FIR_778');self.play('TLC_249');self.kill('Core_CS2_200')
        view=self.g.observe(1)['players'][0]
        self.assertNotIn('hand',view)
        self.assertEqual(view['played_history'],[{'card_id':'TLC_249','cost':1}])
        self.assertNotIn(secret.card_id,view['death_history'])

    def test_permanent_end_damage_hits_only_enemy_hero(self):
        target=self.g._summon(1,'Core_CS2_200')
        self.p.permanent_end_damage=[2,3]
        health=target.health
        self.g.step(Action('end'))
        self.assertEqual(self.q.health,25)
        self.assertEqual(target.health,health)

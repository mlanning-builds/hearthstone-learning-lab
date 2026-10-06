"""Third 30-card batch: local rules and interactions, not training."""
import json
import unittest
from copy import deepcopy
from unittest.mock import patch
from expanded import Game,Action,random_deck
from expanded.game import Card
from expanded.persistent_cards import RULES

class PersistentBatchTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('PALADIN',31),random_deck('MAGE',53)],seed=71)
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:
            p.hand=[];p.board=[];p.deck=['CORE_CS2_029']*25;p.health=30;p.mana=p.max_mana=10;p.armor=0
        return g
    def put(self,g,cid,owner=0):
        c=Card(g._new_id(),cid);g.players[owner].hand.append(c);return c
    def play(self,g,cid,target=None):
        g.players[g.current].mana=10;c=self.put(g,cid,g.current)
        options=[a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid and (target is None or a.target==target)]
        self.assertTrue(options,(cid,target));g.step(options[0]);return c
    def choose(self,g,i=0):g.step(Action('choose',choices=(i,)))
    def cycle(self,g):g.step(Action('end'));g.step(Action('end'))
    def kill(self,g,m):m.health=0;g._settle(allow_event_choices=True)
    def test_thirty_new_cards(self):self.assertEqual(len(RULES),30)
    def test_battlemaster_buffs_current_and_future_recruits(self):
        g=self.game();old=g._summon(0,'CS2_101t');self.kill(g,g._summon(0,'MEND_800'))
        new=g._summon(0,'CS2_101t');self.assertEqual((old.attack,new.attack),(2,2));self.assertEqual(g.players[0].recruit_attack_bonus,1)
    def test_savior_own_shield_only(self):
        g=self.game();s=g._summon(0,'MEND_801');r=g._summon(0,'CS2_101t');r.keywords.add('DIVINE_SHIELD')
        g._damage(r.uid,1);g._settle();self.assertEqual(r.health,1)
        g._damage(s.uid,1);g._settle();self.assertEqual(r.health,2);self.assertEqual(g.players[0].recruit_health_bonus,1)
    def test_convalescence_two_shields(self):
        g=self.game();self.play(g,'MEND_802');self.assertEqual(len(g.players[0].minions),2)
        self.assertTrue(all('DIVINE_SHIELD' in m.keywords for m in g.players[0].minions))
    def test_blade_buffs_recruits_hand_deck_board(self):
        g=self.game();c=self.put(g,'CS2_101t');m=g._summon(0,'CS2_101t');g.players[0].deck=['CS2_101t'];self.play(g,'MEND_803')
        self.assertEqual((m.attack,m.health),(2,2));self.assertEqual(g._card_stat(c,'attack',0),2);self.assertEqual(g._card_stat(g.players[0].deck[0],'health',0),2)
    def test_arator_doubles_current_stats_and_taunt(self):
        g=self.game();r=g._summon(0,'CS2_101t');g._buff(r,2,3);self.play(g,'MEND_804')
        self.assertEqual((r.attack,r.health),(6,8));self.assertIn('TAUNT',r.keywords)
    def test_teamwork_summons_and_adds_four(self):
        g=self.game();self.play(g,'MEND_900');self.assertEqual(len(g.players[0].minions),4)
        self.assertEqual([c.card_id for c in g.players[0].hand],['CS2_101t']*4)
    def test_blaster_spell_specific_damage(self):
        g=self.game();spell=self.put(g,'CORE_CS2_029');self.play(g,'CATA_209');self.choose(g)
        self.assertEqual(spell.spell_damage_bonus,1);g.players[0].mana=10
        g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==spell.uid and a.target==g.hero_id(1)))
        self.assertEqual(g.players[1].health,23)
    def test_kalec_modifies_hand_and_deck_spells_only(self):
        g=self.game();spell=self.put(g,'CORE_CS2_029');m=self.put(g,'CS2_033');g.players[0].deck=['CORE_CS2_029','CS2_033'];self.play(g,'CATA_458')
        self.assertEqual(spell.spell_damage_bonus,1);self.assertFalse(hasattr(m,'spell_damage_bonus'));self.assertEqual(g.players[0].deck[0].spell_damage_bonus,1)
    def test_stellar_balance_complete_spell_chain(self):
        g=self.game();self.play(g,'EDR_874');self.assertEqual({c.card_id for c in g.players[0].hand},{'CS2_008','EX1_173'})
        for c in list(g.players[0].hand):
            g.players[0].mana=10;g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==g.hero_id(1)))
        self.assertEqual(g.players[1].health,22);self.assertEqual(len(g.players[0].hand),1)
    def test_thrasher_kindred_attached_spell_damage(self):
        for active in (False,True):
            g=self.game();g.players[0].previous_tribes={'ELEMENTAL'} if active else set();self.play(g,'TLC_223')
            c=g.players[0].hand[0];self.assertEqual(getattr(c,'spell_damage_bonus',0),2 if active else 0)
    def test_mother_radiates_by_position(self):
        g=self.game();cards=[self.put(g,'CORE_CS2_029') for _ in range(7)];self.play(g,'BE_036');self.choose(g,3)
        self.assertEqual([c.cost_delta for c in cards],[-2,-3,-4,-5,-4,-3,-2])
    def test_informant_copy_or_tax_rightmost(self):
        for i in (0,1):
            g=self.game();a=self.put(g,'CS2_033',1);b=self.put(g,'CORE_CS2_029',1);self.play(g,'TIME_036')
            self.assertTrue(g.observe(1)['pending_choice']['waiting']);self.choose(g,i)
            if i==0:self.assertEqual(g.players[0].hand[0].card_id,b.card_id)
            else:self.assertEqual(g._cost(b,1),6)
            self.assertEqual(g._cost(a,1),g.cards[a.card_id]['cost'])
    def test_volcoross_affordable_choices_and_payment(self):
        g=self.game();g.players[0].corpses=25;self.play(g,'FIR_951');self.assertEqual(len(g.pending_choice['options']),2);self.choose(g,1)
        m=g.players[0].minions[0];self.assertEqual((m.attack,m.health),(25,25));self.assertEqual(g.players[0].corpses,5)
    def test_siamat_two_distinct_choices(self):
        g=self.game();self.play(g,'CORE_ULD_178');self.choose(g,0)
        self.assertEqual(len(g.pending_choice['options']),3);self.assertNotIn('RUSH',[o['label'] for o in g.pending_choice['options']]);self.choose(g,0)
        self.assertTrue({'RUSH','TAUNT'}<=g.players[0].minions[0].keywords)
    def test_archdruid_inherits_current_turn_granted_effects(self):
        g=self.game();m=g._summon(0,'EDR_851t');self.play(g,'CORE_UNG_952',m.uid);self.kill(g,m)
        self.play(g,'EDR_491');d=next(m for m in g.players[0].minions if m.card_id=='EDR_491');self.kill(g,d)
        self.assertEqual(sum(m.card_id=='UNG_810' for m in g.players[0].minions),2)
    def test_khelos_all_five_deaths(self):
        g=self.game();g._summon(0,'DINO_410')
        for cid in ('DINO_410t2','DINO_410t3','DINO_410t4','DINO_410t5','DINO_410t'):
            self.kill(g,g.players[0].minions[0]);self.assertEqual(g.players[0].minions[0].card_id,cid)
        m=g.players[0].minions[0];self.assertEqual((m.attack,m.health),(20,20));self.assertIn('TAUNT',m.keywords)
    def test_bloodpetal_seedling_cycle(self):
        g=self.game();self.kill(g,g._summon(0,'TLC_234'));self.assertEqual(g.players[0].minions[0].card_id,'TLC_234t')
        self.kill(g,g.players[0].minions[0]);self.assertEqual(g.players[0].minions[0].card_id,'TLC_234')
    def test_cenarius_three_choices(self):
        g=self.game();self.play(g,'EDR_209');self.choose(g,1);self.choose(g,0);self.choose(g,1)
        ancients=[m for m in g.players[0].minions if m.card_id=='EDR_209t5'];self.assertEqual([(m.attack,m.health) for m in ancients],[(6,8),(5,5)])
    def test_carver_discount_each_own_turn(self):
        g=self.game();c=self.put(g,'CORE_CS2_029');self.play(g,'CATA_566');self.choose(g)
        self.assertEqual(g._cost(c,0),4);self.cycle(g);self.assertEqual(g._cost(c,0),3);self.cycle(g);self.assertEqual(g._cost(c,0),2)
    def test_aberration_combo_and_expiry(self):
        g=self.game();g.players[0].cards_played=1;self.play(g,'END_032');m=g.players[0].minions[0]
        self.assertEqual(g.players[0].overload_next,2);self.assertIn('IMMUNE',g._effective_keywords(m));g.step(Action('end'))
        self.assertNotIn('IMMUNE',g._effective_keywords(m));self.assertIn('WINDFURY',g._effective_keywords(m))
    def test_phoenix_discount_and_end_return(self):
        g=self.game();g.players[0].cards_played=2;c=self.put(g,'FIR_919');self.assertEqual(g._cost(c,0),2)
        g.players[0].hand.clear();self.kill(g,g._summon(0,'FIR_919'));self.assertFalse(g.players[0].hand);g.step(Action('end'))
        self.assertEqual(g.players[0].hand[0].card_id,'FIR_919')
    def test_firebolt_kill_lifesteal_and_end_return(self):
        g=self.game();g.players[0].health=20;m=g._summon(1,'EDR_851t');self.play(g,'END_025',m.uid)
        self.assertGreater(g.players[0].health,20);self.assertFalse(g.players[0].hand);g.step(Action('end'));self.assertEqual(g.players[0].hand[0].card_id,'END_025')
    def test_resistance_two_enemy_turns(self):
        g=self.game();c=self.put(g,'CORE_CS2_029',1);self.play(g,'TTN_851');g.step(Action('end'))
        self.assertEqual(g._cost(c,1),5);self.assertTrue(g._batch30_state('aura_active',0));self.cycle(g);self.assertEqual(g._cost(c,1),5)
        self.cycle(g);self.assertEqual(g._cost(c,1),4);self.assertFalse(g._batch30_state('aura_active',0))
    def test_bounty_locks_then_unlocks_drawn_cards(self):
        g=self.game();self.play(g,'EDR_234');c=g.players[0].hand[0]
        def playable():return any(a.kind=='play' and a.source==c.uid for a in g.legal_actions())
        self.assertFalse(playable());self.cycle(g);self.assertFalse(playable());self.cycle(g);self.assertTrue(playable())
    def test_daze_prevents_next_enemy_turn_play(self):
        g=self.game();m=g._summon(1,'CS2_033');self.play(g,'CATA_215',m.uid);c=g.players[1].hand[0];g.step(Action('end'))
        self.assertFalse(any(a.kind=='play' and a.source==c.uid for a in g.legal_actions()));self.cycle(g)
        self.assertTrue(any(a.kind=='play' and a.source==c.uid for a in g.legal_actions()))
    def test_ashamane_fills_from_deck_discounted(self):
        g=self.game();g.players[1].deck=['CORE_CS2_029'];self.play(g,'EDR_527');self.assertEqual(len(g.players[0].hand),10)
        self.assertTrue(all(c.card_id=='CORE_CS2_029' and g._cost(c,0)==1 for c in g.players[0].hand));self.assertEqual(g.players[1].deck,['CORE_CS2_029'])
    def test_security_reveal_threshold(self):
        for cid in ('EX1_173','CS2_008'):
            g=self.game();g.players[0].deck=[cid];m=g._summon(1,'CS2_033');self.play(g,'JAIL_379')
            self.assertEqual(m.health,1 if cid=='EX1_173' else 6);self.assertEqual(g.players[0].deck,[cid])
    def test_annihilation_bottom_three_only(self):
        g=self.game();g._summon(1,'CS2_033');g.players[0].deck=['JAIL_399t1','CS2_008','JAIL_399t1','JAIL_399t1'];self.play(g,'JAIL_510')
        self.assertFalse(g.players[1].board);self.assertEqual(len(g.players[0].minions),2);self.assertEqual(len(g.players[0].deck),2)
    def test_maluk_discards_and_banana_stays(self):
        g=self.game();self.put(g,'CS2_008');self.put(g,'CORE_CS2_029');self.play(g,'TIME_042')
        self.assertEqual(len(g.players[0].discard_history),2);c=g.players[0].hand[0];self.assertEqual(c.card_id,'TIME_042t')
        m=g.players[0].minions[0];before=m.attack
        for _ in range(2):g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==m.uid))
        self.assertEqual(m.attack,before+2);self.assertEqual(g.players[0].hand,[c])
    def test_leviathan_three_reselected_health_steals(self):
        g=self.game();enemy=g._summon(1,'CS2_033');g._buff(enemy,0,10);self.play(g,'CATA_699')
        for _ in range(3):self.choose(g)
        m=g.players[0].minions[0];self.assertEqual((enemy.health,m.health),(7,17))
    def test_recruit_copy_not_double_buffed_and_silence(self):
        g=self.game();self.play(g,'MEND_803');r=g._summon(0,'CS2_101t');clone=g._summon(0,r.card_id,copy_from=r)
        self.assertEqual((clone.attack,clone.health),(2,2));g._silence(r);self.assertEqual((r.attack,r.health),(1,1))
    def test_choice_rollback_and_private_state(self):
        g=self.game();self.put(g,'CS2_008',1);self.play(g,'TIME_036');before=deepcopy(g.__dict__)
        with patch.object(Game,'assert_invariants',side_effect=RuntimeError('injected')):
            with self.assertRaises(RuntimeError):self.choose(g)
        self.assertEqual(g.pending_choice,before['pending_choice']);self.assertEqual(g.rng.getstate(),before['rng'].getstate());json.dumps(g.observe(1))
    def test_phoenix_dying_enemy_turn_returns_at_enemy_end(self):
        g=self.game();g.step(Action('end'));self.kill(g,g._summon(0,'FIR_919'));g.step(Action('end'))
        self.assertIn('FIR_919',[c.card_id for c in g.players[0].hand])
    def test_full_board_teamwork_still_adds_cards(self):
        g=self.game()
        for _ in range(7):g._summon(0,'EDR_851t')
        self.play(g,'MEND_900');self.assertEqual(len(g.players[0].board),7);self.assertEqual(len(g.players[0].hand),4)

    def test_silenced_battlemaster_no_bonus(self):
        g=self.game();m=g._summon(0,'MEND_800');g._silence(m);self.kill(g,m);self.assertEqual(g.players[0].recruit_attack_bonus,0)
    def test_recruit_play_uses_persistent_bonus_once(self):
        g=self.game();self.play(g,'MEND_803');self.play(g,'CS2_101t');r=g.players[0].minions[0];self.assertEqual((r.attack,r.health),(2,2))
    def test_volcoross_no_affordable_option(self):
        g=self.game();g.players[0].corpses=9;self.play(g,'FIR_951');self.assertIsNone(g.pending_choice);self.assertEqual(g.players[0].corpses,9)
    def test_aberration_without_combo(self):
        g=self.game();self.play(g,'END_032');self.assertEqual(g.players[0].overload_next,0);self.assertNotIn('WINDFURY',g.players[0].minions[0].keywords)
    def test_firebolt_survival_does_not_return(self):
        g=self.game();m=g._summon(1,'CS2_033');self.play(g,'END_025',m.uid);g.step(Action('end'));self.assertFalse(g.players[0].hand)
    def test_spell_damage_is_not_global_and_survives_shuffle(self):
        g=self.game();a=self.put(g,'CORE_CS2_029');self.put(g,'CS2_033');self.play(g,'CATA_209');self.choose(g)
        self.assertEqual(g._spell_damage(0),0);g._shuffle_hand_card(0,a);self.assertEqual(a.spell_damage_bonus,1)
    def test_spell_damage_private_observation(self):
        g=self.game();self.put(g,'CS2_008');self.play(g,'CATA_209');self.choose(g)
        self.assertEqual(g.observe(0)['players'][0]['hand'][0]['spell_damage_bonus'],1);self.assertNotIn('hand',g.observe(1)['players'][0])
    def test_leviathan_reselects_after_target_death(self):
        g=self.game();g._summon(1,'EDR_851t');g._summon(1,'CS2_033');self.play(g,'CATA_699');self.choose(g)
        self.assertEqual(len(g.pending_choice['options']),1);self.choose(g);self.choose(g);self.assertFalse(g.players[1].board)
    def test_cenarius_combines_choices_with_fandral(self):
        g=self.game();f=g._summon(0,'CORE_OG_044');self.play(g,'EDR_209')
        self.assertIsNone(g.pending_choice);self.assertEqual(sum(m.card_id=='EDR_209t5' for m in g.players[0].minions),3)
        self.assertEqual(f.attack,g.cards[f.card_id]['attack']+3)
    def test_carver_source_silence_does_not_cancel_card_modifier(self):
        g=self.game();c=self.put(g,'CORE_CS2_029');self.play(g,'CATA_566');self.choose(g);g._silence(g.players[0].minions[0]);self.cycle(g);self.assertEqual(g._cost(c,0),3)
    def test_archdruid_does_not_inherit_prior_turn(self):
        g=self.game();self.kill(g,g._summon(0,'MEND_800'));self.cycle(g);self.play(g,'EDR_491')
        self.assertFalse(g.players[0].minions[0].attached_death_effects)

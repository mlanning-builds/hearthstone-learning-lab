"""User-run cross-system checks. Importing this file never starts games."""
import copy
import unittest
from expanded import Game, Action, random_deck
from expanded.game import Card
from expanded.cards import CHOICES, COLLECTIBLE_IDS, registry


class SharedSystemsTests(unittest.TestCase):
    def game(self, hero='MAGE', enemy='WARRIOR'):
        self.g=Game([random_deck(hero,31),random_deck(enemy,53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        self.p.hand=[];self.q.hand=[]
        self.p.mana=self.p.max_mana=10
        return self.g

    def give(self,cid):
        c=Card(self.g._new_id(),cid);self.p.hand.append(c);return c

    def play(self,cid,target=0,choice=None):
        c=self.give(cid)
        position=len(self.p.board) if self.g.cards[cid]['type']=='MINION' else -1
        choices=() if choice is None else (choice,)
        self.g.step(Action('play',c.uid,target,position,choices))
        return c

    def secret(self,cid,owner=1):
        self.g.players[owner].secrets.append(Card(self.g._new_id(),cid))

    def test_choose_one_exposes_distinct_legal_branches(self):
        self.game('DRUID');c=self.give('CORE_AT_037')
        options=[a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid]
        self.assertEqual({a.choices for a in options},{(0,),(1,)})
        self.g.step(next(a for a in options if a.choices==(1,)))
        self.assertEqual([m.card_id for m in self.p.board],['AT_037t','AT_037t'])

    def test_choose_one_requires_a_choice_and_leaves_state_unchanged(self):
        self.game('DRUID');c=self.give('CORE_AT_037')
        before=copy.deepcopy(self.g.players);rng=self.g.rng.getstate()
        with self.assertRaises(ValueError):self.g.step(Action('play',c.uid,-2))
        self.assertEqual(self.g.players,before);self.assertEqual(self.g.rng.getstate(),rng)

    def test_wrath_damage_draw_and_mana(self):
        self.game('DRUID');m=self.g._summon(1,'Core_CS2_200')
        self.play('CORE_EX1_154',m.uid,choice=1)
        self.assertEqual(m.health,self.g.cards[m.card_id]['health']-1)
        self.assertEqual(len(self.p.hand),1)
        self.assertEqual(self.p.mana,8)

    def test_fandral_wrath_is_one_hit_and_draws(self):
        self.game('DRUID');self.g._summon(0,'CORE_OG_044')
        m=self.g._summon(1,'Core_CS2_200');m.keywords.add('DIVINE_SHIELD')
        self.play('CORE_EX1_154',m.uid,choice=-1)
        self.assertEqual(m.health,m.max_health);self.assertNotIn('DIVINE_SHIELD',m.keywords)
        self.assertEqual(len(self.p.hand),1)

    def test_fandral_power_of_wild_buffs_summoned_panther(self):
        self.game('DRUID');self.g._summon(0,'CORE_OG_044')
        self.play('CORE_EX1_160',choice=-1)
        panther=self.p.board[-1]
        self.assertEqual((panther.card_id,panther.attack,panther.health),('EX1_160t',4,3))

    def test_tracking_pauses_play_and_keeps_choice_private(self):
        self.game('HUNTER')
        self.p.deck=['CORE_CS2_029','CORE_CS2_023','CORE_EX1_506']
        self.play('CORE_DS1_184')
        self.assertEqual(self.g.phase,'choice')
        self.assertTrue(all(a.kind=='choose' for a in self.g.legal_actions()))
        own=self.g.observe(0);other=self.g.observe(1)
        self.assertEqual(len(own['pending_choice']['options']),3)
        self.assertNotIn('index',own['pending_choice']['options'][0])
        self.assertNotIn('options',other['pending_choice'])
        self.assertEqual(other['legal_actions'],[])
        selected=own['pending_choice']['options'][0]['card_id']
        self.g.step(Action('choose',choices=(0,)))
        self.assertEqual(self.p.hand[0].card_id,selected)
        self.assertEqual(len(self.p.deck),2)
        self.assertEqual(self.g.phase,'play')

    def test_tracking_empty_deck_has_no_fatigue_or_empty_choice(self):
        self.game('HUNTER');self.p.deck=[]
        self.play('CORE_DS1_184')
        self.assertEqual(self.p.fatigue,0);self.assertIsNone(self.g.pending_choice)

    def test_trade_preserves_enchantments_without_playing(self):
        self.game();c=self.give('CORE_SW_066');c.attack_bonus=2;c.health_bonus=3;c.cost_delta=-1
        self.p.deck=['CORE_CS2_029']
        self.g.step(Action('trade',source=c.uid))
        self.assertEqual(self.p.cards_played,0);self.assertEqual(self.p.mana,9)
        self.assertEqual(self.p.hand[0].card_id,'CORE_CS2_029')
        self.assertEqual(self.p.deck,[c])
        self.g._draw(0)
        self.assertEqual((self.p.hand[-1].attack_bonus,self.p.hand[-1].health_bonus,self.p.hand[-1].cost_delta),(2,3,-1))

    def test_trade_requires_mana_and_a_nonempty_deck(self):
        self.game();c=self.give('CORE_SW_066');self.p.deck=[]
        self.assertNotIn(Action('trade',source=c.uid),self.g.legal_actions())
        self.p.deck=['CORE_CS2_029'];self.p.mana=0
        self.assertNotIn(Action('trade',source=c.uid),self.g.legal_actions())

    def test_stormwind_aura_does_not_stack_on_recalculation(self):
        self.game();m=self.g._summon(0,'Core_CS2_200')
        base=(m.attack,m.health);champ=self.g._summon(0,'CORE_CS2_222')
        for _ in range(3):self.g._refresh_auras()
        self.assertEqual((m.attack,m.health),(base[0]+1,base[1]+1))
        m.health-=2;champ.health=0;self.g._settle()
        self.assertEqual(m.attack,base[0]);self.assertEqual(m.max_health,base[1])
        self.assertEqual(m.health,base[1]-1)

    def test_adjacency_updates_after_minion_is_removed(self):
        self.game();left=self.g._summon(0,'Core_CS2_200')
        wolf=self.g._summon(0,'CORE_EX1_162')
        right=self.g._summon(0,'Core_CS2_200')
        distant=self.g._summon(0,'Core_CS2_200')
        self.assertEqual((left.attack,right.attack,distant.attack),(7,7,6))
        right.health=0;self.g._settle();self.assertEqual(distant.attack,7)

    def test_silencing_aura_provider_removes_buff_without_destroying_it(self):
        self.game();m=self.g._summon(0,'Core_CS2_200')
        leader=self.g._summon(0,'CORE_CS2_122')
        self.assertEqual(m.attack,7)
        self.play('CORE_SW_066',leader.uid)
        self.assertEqual(m.attack,6);self.assertIn(leader,self.p.board)

    def test_silencing_damaged_aura_recipient_does_not_heal(self):
        self.game();m=self.g._summon(0,'Core_CS2_200')
        self.g._summon(0,'CORE_CS2_222')
        m.health-=2
        before=(m.attack,m.health,m.max_health)
        self.play('CORE_SW_066',m.uid)
        self.assertEqual((m.attack,m.health,m.max_health),before)
        self.g._silence(m);self.g._refresh_auras()
        self.assertEqual((m.attack,m.health,m.max_health),before)

    def test_silence_removes_buff_but_preserves_two_external_auras(self):
        self.game();m=self.g._summon(0,'Core_CS2_200')
        base=self.g.cards[m.card_id]
        self.g._summon(0,'CORE_CS2_222');self.g._summon(0,'CORE_CS2_222')
        self.g._buff(m,3,4);m.health-=5
        self.g._silence(m)
        self.assertEqual((m.attack,m.health,m.max_health),
                         (base['attack']+2,base['health']+1,base['health']+2))
        self.assertEqual((m.aura_attack,m.aura_health),(2,2))

    def test_silencing_provider_preserves_other_providers_aura(self):
        self.game();first=self.g._summon(0,'CORE_CS2_222')
        second=self.g._summon(0,'CORE_CS2_222')
        first.health-=2;before=first.health
        self.g._silence(first)
        base=self.g.cards[first.card_id]
        self.assertEqual((first.attack,first.health,first.max_health),
                         (base['attack']+1,before,base['health']+1))
        self.assertEqual((second.attack,second.max_health),
                         (base['attack'],base['health']))

    def test_silence_health_reduction_restores_health_without_erasing_damage(self):
        self.game();m=self.g._summon(0,'Core_CS2_200')
        base=self.g.cards[m.card_id]
        self.g._buff(m,0,-2);m.health-=1
        self.g._silence(m)
        self.assertEqual((m.health,m.max_health),(base['health']-1,base['health']))

    def test_silence_removes_conditional_attack(self):
        self.game();m=self.g._summon(0,'CORE_EX1_414')
        m.health-=1;self.g._refresh_auras()
        self.assertGreater(m.aura_attack,0)
        self.g._silence(m)
        self.assertEqual(m.attack,self.g.cards[m.card_id]['attack'])
        self.assertEqual(m.aura_attack,0)

    def test_silence_does_not_revive_mortally_wounded_aura_recipient(self):
        self.game();m=self.g._summon(0,'Core_CS2_200')
        self.g._summon(0,'CORE_CS2_222');m.health=0
        self.g._silence(m)
        self.assertEqual(m.health,0)
        self.g._settle();self.assertNotIn(m,self.p.board)

    def test_silence_removes_deathrattle_reborn_and_spell_damage(self):
        self.game();m=self.g._summon(1,'CORE_EX1_012');m.keywords.add('REBORN')
        self.play('CORE_SW_066',m.uid)
        self.assertEqual(self.g._spell_damage(1),0)
        m.health=0;self.g._settle()
        self.assertEqual(len(self.q.hand),0);self.assertEqual(self.q.board,[])

    def test_hex_replaces_without_deathrattle_or_corpse(self):
        self.game('SHAMAN');m=self.g._summon(1,'CORE_EX1_110')
        self.play('CORE_EX1_246',m.uid)
        self.assertEqual([m.card_id for m in self.q.board],['hexfrog'])
        self.assertEqual(self.q.corpses,0)
        self.assertIn('TAUNT',self.q.board[0].keywords)

    def test_bounce_removes_buffs_without_triggering_death(self):
        self.game();m=self.g._summon(1,'CORE_EX1_110')
        self.g._buff(m,3,3)
        self.play('CATA_201')
        self.assertEqual(self.q.board,[]);self.assertEqual(self.q.corpses,0)
        self.assertEqual(self.q.hand[0].card_id,'CORE_EX1_110')
        self.assertEqual(self.q.hand[0].attack_bonus,0)

    def test_bounce_into_full_hand_kills_and_triggers_deathrattle(self):
        self.game();m=self.g._summon(1,'CORE_EX1_110')
        self.q.hand=[Card(self.g._new_id(),'CORE_CS2_029') for _ in range(10)]
        self.g._bounce(m);self.g._settle()
        self.assertEqual([m.card_id for m in self.q.board],['TOKEN_BAINE'])
        self.assertEqual(self.q.corpses,1)

    def test_damage_draw_trigger_includes_lethal_but_not_shield(self):
        self.game();m=self.g._summon(0,'CORE_EX1_007')
        m.keywords.add('DIVINE_SHIELD')
        self.g._damage(m.uid,1);self.g._settle();self.assertEqual(len(self.p.hand),0)
        self.g._damage(m.uid,99);self.g._settle();self.assertEqual(len(self.p.hand),1)

    def test_frothing_counts_each_damaged_minion_in_aoe(self):
        self.game();m=self.g._summon(0,'CORE_EX1_604')
        self.g._summon(1,'Core_CS2_200')
        attack=m.attack
        self.g._effect(('area_damage','all_minions',1),dict(owner=0,source=None,target=0,bonus=0))
        self.g._settle();self.assertEqual(m.attack,attack+2)

    def test_hero_attack_triggers_on_last_weapon_charge(self):
        self.game('ROGUE');m=self.g._summon(0,'CORE_GIL_534')
        attack,health=m.attack,m.health
        self.g._equip(0,'CS2_082');self.p.weapon['durability']=1
        self.g.step(Action('attack',-1,-2))
        self.assertIsNone(self.p.weapon)
        self.assertEqual((m.attack,m.health),(attack+1,health+1))

    def test_pyromancer_triggers_after_spell_and_can_die(self):
        self.game();m=self.g._summon(0,'CORE_NEW1_020');m.health=1
        enemy=self.g._summon(1,'Core_CS2_200')
        self.play('CORE_CS2_023')
        self.assertEqual(len(self.p.hand),2)
        self.assertNotIn(m,self.p.board);self.assertEqual(enemy.health,enemy.max_health-1)

    def test_spell_trigger_does_not_give_spell_damage_to_its_own_damage(self):
        self.game();self.g._summon(0,'CORE_NEW1_020');self.g._summon(0,'CORE_EX1_012')
        enemy=self.g._summon(1,'Core_CS2_200')
        self.play('CORE_CS2_023');self.assertEqual(enemy.health,enemy.max_health-1)

    def test_spell_cast_generates_fireball_and_not_a_random_spell(self):
        self.game();self.g._summon(0,'CORE_EX1_559')
        self.play('TOKEN_COIN')
        self.assertEqual([c.card_id for c in self.p.hand],['CORE_CS2_029'])

    def test_temporary_attack_expires_on_both_sides(self):
        self.game();m=self.g._summon(1,'Core_CS2_200')
        self.play('CORE_CS2_188',m.uid);self.assertEqual(m.attack,8)
        self.g.step(Action('end'));self.assertEqual(m.attack,6)

    def test_tar_creeper_and_damaged_attack_recalculate(self):
        self.game();tar=self.g._summon(0,'CORE_UNG_928')
        base=tar.attack;self.g.step(Action('end'))
        self.assertEqual(tar.attack,base+2)
        self.g.step(Action('end'));self.assertEqual(tar.attack,base)
        grom=self.g._summon(0,'CORE_EX1_414');base=grom.attack
        self.g._damage(grom.uid,1);self.g._settle();self.assertEqual(grom.attack,base+6)
        self.g._heal(grom.uid,1);self.g._settle();self.assertEqual(grom.attack,base)

    def test_micro_machine_triggers_on_each_players_turn(self):
        self.game();m=self.g._summon(0,'CORE_GVG_103');attack=m.attack
        self.g.step(Action('end'));self.assertEqual(m.attack,attack+1)
        self.g.step(Action('end'));self.assertEqual(m.attack,attack+2)

    def test_doomsayer_resolves_before_the_turn_draw(self):
        self.game();self.g._summon(0,'CORE_NEW1_021');self.g._summon(1,'Core_CS2_200')
        self.g.step(Action('end'))
        self.assertEqual(len(self.q.board),1)
        self.g.step(Action('end'))
        self.assertEqual(self.p.board,[]);self.assertEqual(self.q.board,[])

    def test_weapon_deathrattle_on_replacement(self):
        self.game('PALADIN');m=self.g._summon(0,'CORE_EX1_383')
        m.health=0;self.g._settle();self.assertEqual(self.p.weapon['card_id'],'EX1_383t')
        self.g._equip(0,'CORE_OG_031');self.g._equip(0,'CS2_082')
        self.assertEqual(self.p.board[-1].card_id,'OG_031a')

    def test_waggle_pick_discount_survives_return(self):
        self.game('ROGUE');m=self.g._summon(0,'Core_CS2_200')
        self.g._equip(0,'CORE_DAL_720');self.g._break_weapon(0);self.g._settle()
        self.assertEqual(self.p.board,[])
        self.assertEqual(self.g._cost(self.p.hand[0],0),self.g.cards[m.card_id]['cost']-2)

    def test_secret_identity_is_not_in_opponent_observation_or_play_log(self):
        self.game();self.play('CORE_EX1_287')
        own=self.g.observe(0);other=self.g.observe(1)
        self.assertEqual(own['players'][0]['secrets'],['CORE_EX1_287'])
        self.assertNotIn('secrets',other['players'][0])
        self.assertEqual(other['players'][0]['secret_count'],1)
        self.assertFalse(any(e.get('card')=='CORE_EX1_287' for e in other['events']))

    def test_counterspell_spends_mana_but_prevents_effect_and_after_cast(self):
        self.game();self.g._summon(0,'CORE_EX1_559')
        self.secret('CORE_EX1_287')
        self.play('CORE_CS2_029',-2)
        self.assertEqual(self.q.health,30);self.assertEqual(self.p.mana,6)
        self.assertEqual(self.p.hand,[]);self.assertEqual(self.q.secrets,[])

    def test_secret_duplicates_are_not_playable(self):
        self.game();self.secret('CORE_EX1_287',0);c=self.give('CORE_EX1_287')
        self.assertFalse(any(a.kind=='play' and a.source==c.uid for a in self.g.legal_actions()))

    def test_ice_barrier_absorbs_attack(self):
        self.game('ROGUE');self.g._equip(0,'CS2_082');self.secret('CORE_EX1_289')
        self.g.step(Action('attack',-1,-2))
        self.assertEqual((self.q.health,self.q.armor),(30,7))

    def test_freezing_trap_cancels_attack_and_increases_cost(self):
        self.game();m=self.g._summon(0,'CORE_CS2_179');m.summoned_turn=0
        self.secret('CORE_EX1_611');self.g.step(Action('attack',m.uid,-2))
        self.assertEqual(self.q.health,30);self.assertEqual(self.p.board,[])
        self.assertEqual(self.g._cost(self.p.hand[0],0),self.g.cards[m.card_id]['cost']+2)

    def test_explosive_trap_kills_attacker_before_combat(self):
        self.game();m=self.g._summon(0,'CORE_CS2_189');m.summoned_turn=0
        self.secret('CORE_EX1_610');self.g.step(Action('attack',m.uid,-2))
        self.assertEqual(self.q.health,30);self.assertNotIn(m,self.p.board)
        self.assertEqual(self.p.health,28)

    def test_pressure_plate_waits_until_spell_resolves(self):
        self.game('DRUID');self.secret('CORE_ULD_152')
        self.play('CORE_AT_037',choice=1)
        self.assertEqual(len(self.p.board),1);self.assertEqual(self.q.secrets,[])

    def test_rat_trap_counts_played_cards_but_not_trading(self):
        self.game();self.secret('CORE_GIL_577')
        c=self.give('CORE_SW_066');self.g.step(Action('trade',source=c.uid));self.p.hand=[]
        self.play('TOKEN_COIN');self.play('TOKEN_COIN')
        self.assertEqual(self.q.board,[])
        self.play('TOKEN_COIN')
        self.assertEqual(self.q.board[0].card_id,'GIL_577t')

    def test_preparation_applies_once_and_expires_at_turn_end(self):
        self.game('ROGUE');self.play('CORE_EX1_145')
        c=self.give('CORE_CS2_029');self.assertEqual(self.g._cost(c,0),2)
        self.g.step(Action('play',c.uid,-2));self.assertEqual(self.p.mana,8)
        c=self.give('CORE_CS2_029');self.assertEqual(self.g._cost(c,0),4)
        self.play('CORE_EX1_145');self.g.step(Action('end'));self.g.step(Action('end'))
        self.assertEqual(self.g._cost(c,0),4)

    def test_far_sight_discount_is_carried_by_the_drawn_card(self):
        self.game('SHAMAN');self.p.deck=['CORE_CS2_029']
        self.play('CORE_CS2_053')
        self.assertEqual(self.g._cost(self.p.hand[0],0),1)

    def test_felscreamer_discount_waits_for_demon(self):
        self.game('DEMONHUNTER');self.play('CORE_BT_416')
        c=self.give('CORE_EX1_310')
        self.assertEqual(self.g._cost(c,0),self.g.cards[c.card_id]['cost']-2)
        self.g.step(Action('end'));self.g.step(Action('end'))
        self.assertEqual(self.g._cost(c,0),self.g.cards[c.card_id]['cost']-2)

    def test_kayn_ignores_taunt_until_silenced(self):
        self.game('DEMONHUNTER')
        kayn=self.g._summon(0,'CORE_BT_187');enemy=self.g._summon(1,'CORE_CS2_179')
        self.assertIn(Action('attack',kayn.uid,-2),self.g.legal_actions())
        self.g._silence(kayn);self.g._settle()
        self.assertNotIn(Action('attack',kayn.uid,-2),self.g.legal_actions())

    def test_bladed_gauntlet_uses_armor_and_cannot_hit_hero(self):
        self.game('WARRIOR');self.p.armor=5;self.g._equip(0,'CORE_LOOT_044')
        enemy=self.g._summon(1,'Core_CS2_200')
        self.assertEqual(self.g._hero_attack(0),5)
        self.assertNotIn(Action('attack',-1,-2),self.g.legal_actions())
        self.g.step(Action('attack',-1,enemy.uid))
        self.assertEqual(enemy.health,enemy.max_health-5)

    def test_random_split_damage_gets_one_extra_missile_from_spell_damage(self):
        self.game('PRIEST');self.g._summon(0,'CORE_EX1_012');self.p.health=20
        enemy=self.g._summon(1,'Core_CS2_200')
        self.play('CORE_BAR_311')
        self.assertEqual(enemy.health,enemy.max_health-5);self.assertEqual(self.p.health,25)

    def test_full_health_random_healing_does_not_damage_or_loop(self):
        self.game('SHAMAN');self.play('CORE_LOOT_373')
        self.assertEqual(self.p.health,30)

    def test_initiation_summons_fresh_copy_after_kill(self):
        self.game('PRIEST');enemy=self.g._summon(1,'CORE_CS2_189')
        self.play('CORE_SCH_512',enemy.uid)
        self.assertEqual(self.q.board,[])
        self.assertEqual(self.p.board[0].card_id,'CORE_CS2_189')
        self.assertEqual(self.p.board[0].health,self.g.cards['CORE_CS2_189']['health'])

    def test_recruit_does_not_trigger_battlecry(self):
        self.game('DRUID');self.p.deck=['CORE_EX1_319']
        self.play('CORE_LOOT_309')
        self.assertEqual(self.p.board[0].card_id,'CORE_EX1_319')
        self.assertEqual((self.p.health,self.p.armor),(30,6))

    def test_dirty_rat_preserves_hand_buff_and_skips_battlecry(self):
        self.game();self.q.hand=[Card(self.g._new_id(),'CORE_EX1_319',2,3)]
        self.play('CORE_CFM_790')
        m=self.q.board[0];d=self.g.cards[m.card_id]
        self.assertEqual((m.attack,m.health),(d['attack']+2,d['health']+3))
        self.assertEqual(self.q.health,30)

    def test_tirion_silence_suppresses_weapon(self):
        self.game();m=self.g._summon(0,'CORE_EX1_383')
        self.g._silence(m);m.health=0;self.g._settle()
        self.assertIsNone(self.p.weapon)

    def test_unknown_full_pool_cards_still_rejected(self):
        cards=registry();self.assertNotIn('CORE_AV_107',COLLECTIBLE_IDS)
        self.assertNotIn('CORE_AV_107',cards)

    def test_choice_registry_is_explicit_and_all_options_have_labels(self):
        for cid,options in CHOICES.items():
            self.assertIn(cid,COLLECTIBLE_IDS)
            self.assertEqual(len(options),2)
            self.assertTrue(all(label for label,_,_ in options))

if __name__=='__main__':
    unittest.main()

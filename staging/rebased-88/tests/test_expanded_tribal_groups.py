"""Type matching, physical draws, damage auras and hand locks."""
import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card
from expanded.selectors import effective_tribes

class TribalGroupsTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('SHAMAN',31),random_deck('MAGE',53)],seed=71)
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:
            p.hand=[];p.board=[];p.deck=['CORE_CS2_029']*20;p.mana=p.max_mana=10;p.health=30;p.armor=0
        return g
    def play(self,g,cid,target=0):
        c=g._enter_hand(0,Card(g._new_id(),cid));g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==target))
    def typed(self,g,tribe):
        return next(cid for cid,d in g.cards.items() if d['type']=='MINION' and effective_tribes(d)=={tribe} and cid not in {'CAP_104','TLC_228','EDR_480'})
    def test_mug_buffs_only_one_of_duplicate_types(self):
        g=self.game();cid=self.typed(g,'BEAST');ms=[g._summon(0,cid) for _ in range(3)];stats=[m.attack for m in ms];self.play(g,'CORE_WON_141');self.assertEqual(sum(m.attack-before for m,before in zip(ms,stats)),1)
    def test_mug_up_to_three_different_types(self):
        g=self.game();ms=[g._summon(0,self.typed(g,t)) for t in ['BEAST','DEMON','MURLOC','DRAGON']];stats=[m.attack for m in ms];self.play(g,'CORE_WON_141');self.assertEqual(sum(m.attack-before for m,before in zip(ms,stats)),3)
    def test_mug_excludes_untyped(self):
        g=self.game();m=g._summon(0,'CORE_WON_141');before=m.attack;self.play(g,'CORE_WON_141');self.assertEqual(m.attack,before)
    def test_matching_reassigns_all_type_minion(self):
        g=self.game();all_cid=next(cid for cid,d in g.cards.items() if d.get('race')=='ALL');cards=[Card(100,all_cid),Card(101,self.typed(g,'BEAST'))]
        self.assertEqual(len(g._distinct_type_group(cards,2)),2)
    def test_matching_cannot_assign_three_pure_beasts(self):
        g=self.game();cards=[Card(i,self.typed(g,'BEAST')) for i in range(3)];self.assertEqual(len(g._distinct_type_group(cards,3)),1)
    def test_storyteller_buffs_each_represented_type(self):
        g=self.game();g._summon(0,'TLC_254');ms=[g._summon(0,self.typed(g,t)) for t in ['BEAST','DEMON','MURLOC','DRAGON']];stats=[m.attack for m in ms];g.step(Action('end'));self.assertEqual([m.attack-before for m,before in zip(ms,stats)],[1]*4)
    def test_storyteller_silence_disables(self):
        g=self.game();m=g._summon(0,'TLC_254');g._silence(m);b=g._summon(0,self.typed(g,'BEAST'));before=b.attack;g.step(Action('end'));self.assertEqual(b.attack,before)
    def test_esho_buffs_all_zones_except_self(self):
        g=self.game();cid=self.typed(g,'BEAST');g.players[0].deck=[cid];c=g._enter_hand(0,Card(g._new_id(),cid));m=g._summon(0,cid);a=m.attack;self.play(g,'TLC_110')
        self.assertEqual(m.attack,a+2);self.assertEqual(c.attack_bonus,2);self.assertEqual(g.players[0].deck[0].attack_bonus,2);esho=next(m for m in g.players[0].minions if m.card_id=='TLC_110');self.assertEqual(esho.attack,5)
    def test_esho_mixed_deck_does_not_buff(self):
        g=self.game();g.players[0].deck=[self.typed(g,'BEAST'),self.typed(g,'DEMON')];m=g._summon(0,'EDR_851t');a=m.attack;self.play(g,'TLC_110');self.assertEqual(m.attack,a)
    def test_esho_untyped_minion_fails_condition(self):
        g=self.game();g.players[0].deck=['CORE_WON_141'];m=g._summon(0,'EDR_851t');a=m.attack;self.play(g,'TLC_110');self.assertEqual(m.attack,a)
    def test_firehawk_draws_different_types_and_buffs_physical_cards(self):
        g=self.game();cards=[Card(g._new_id(),self.typed(g,t)) for t in ['BEAST','DEMON']];g.players[0].deck=cards[:];self.play(g,'TLC_222');self.assertEqual(len(g.players[0].hand),2)
        self.assertTrue(all(any(c is h for h in g.players[0].hand) for c in cards));self.assertTrue(all((c.attack_bonus,c.health_bonus)==(1,1) for c in cards))
    def test_firehawk_one_type_draws_only_one(self):
        g=self.game();cid=self.typed(g,'BEAST');g.players[0].deck=[cid,cid];self.play(g,'TLC_222');self.assertEqual(len(g.players[0].hand),1);self.assertEqual(len(g.players[0].deck),1)
    def test_firehawk_no_minions_no_fatigue(self):
        g=self.game();g.players[0].deck=[];self.play(g,'TLC_222');self.assertEqual(g.players[0].fatigue,0)
    def test_firehawk_summoned_when_drawn_gets_buff_on_board(self):
        g=self.game();g.players[0].deck=['EDR_260t','CORE_CS2_029'];self.play(g,'TLC_222');m=g.players[0].minions[0];self.assertEqual((m.attack,m.health),(5,6));self.assertEqual(len(g.players[0].hand),1)
    def test_renferal_locks_enemy_next_turn_then_expires(self):
        g=self.game();c=g._enter_hand(1,Card(g._new_id(),'TOKEN_COIN'));self.play(g,'EDR_526');g.step(Action('end'));self.assertFalse(any(a.source==c.uid for a in g.legal_actions()));g.step(Action('end'));g.step(Action('end'));self.assertTrue(any(a.source==c.uid for a in g.legal_actions()))
    def test_renferal_improves_with_prior_plays(self):
        g=self.game();g.players[0].played_history=[dict(card_id='EDR_526',cost=1)]*2
        for _ in range(5):g._add(1,'TOKEN_COIN')
        self.play(g,'EDR_526');self.assertEqual(sum(hasattr(c,'play_lock') for c in g.players[1].hand),3)
    def test_goldrinn_beast_combat_double(self):
        g=self.game();g._summon(0,'EDR_480');m=g._summon(0,self.typed(g,'BEAST'));g._force_attack(m.uid,g.hero_id(1));self.assertEqual(g.players[1].health,30-2*m.attack)
    def test_goldrinn_nonbeast_unchanged(self):
        g=self.game();g._summon(0,'EDR_480');m=g._summon(0,'EDR_851t');g._force_attack(m.uid,g.hero_id(1));self.assertEqual(g.players[1].health,29)
    def test_goldrinn_silence_disables_multiplier(self):
        g=self.game();a=g._summon(0,'EDR_480');g._silence(a);m=g._summon(0,self.typed(g,'BEAST'));g._force_attack(m.uid,g.hero_id(1));self.assertEqual(g.players[1].health,30-m.attack)
    def test_bralma_elemental_effect_damage(self):
        g=self.game();g._summon(0,'TLC_228');m=g._summon(0,self.typed(g,'ELEMENTAL'));g._deal_effect(g.hero_id(1),2,dict(owner=0,source=m,bonus=0));self.assertEqual(g.players[1].health,27)
    def test_engineer_pirate_damage_only_own_turn(self):
        g=self.game();g._summon(0,'CAP_104');m=g._summon(0,self.typed(g,'PIRATE'));self.assertEqual(g._outgoing_tribal_damage(m,2),3);g.current=1;self.assertEqual(g._outgoing_tribal_damage(m,2),2)
    def test_zero_damage_not_increased(self):
        g=self.game();g._summon(0,'TLC_228');m=g._summon(0,self.typed(g,'ELEMENTAL'));self.assertEqual(g._outgoing_tribal_damage(m,0),0)
    def test_damage_aura_lifesteal_uses_actual_damage(self):
        g=self.game();g._summon(0,'EDR_480');m=g._summon(0,self.typed(g,'BEAST'));m.keywords.add('LIFESTEAL');g.players[0].health=10;g._force_attack(m.uid,g.hero_id(1));self.assertEqual(g.players[0].health,min(30,10+2*m.attack))

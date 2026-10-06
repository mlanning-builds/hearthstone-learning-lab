import unittest
from unittest.mock import patch
from expanded import Game,Action,random_deck

class ShadowRoundsTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('WARLOCK',31),random_deck('MAGE',53)],seed=71,record=True)
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:p.hand=[];p.board=[];p.deck=['CORE_CS2_029']*20;p.mana=p.max_mana=10;p.health=30;p.armor=0
        g.events=[];return g
    def play(self,g,target):
        c=g._add(0,'JAIL_515');g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==target.uid))
    def casts(self,g):return [e for e in g.events if e['event']=='internal_spell_cast']
    def test_kills_all_two_health_minions(self):
        g=self.game();ms=[g._summon(1,'EDR_851t') for _ in range(3)];self.play(g,ms[0])
        self.assertFalse(g.players[1].minions);self.assertEqual(len(self.casts(g)),2);self.assertEqual(g.players[0].mana,8)
    def test_survivor_stops_chain(self):
        g=self.game();m=g._summon(1,'CS3_020');before=m.health;self.play(g,m)
        self.assertEqual(m.health,before-2);self.assertFalse(self.casts(g))
    def test_shield_loss_is_not_death(self):
        g=self.game();m=g._summon(1,'EDR_851t');m.keywords.add('DIVINE_SHIELD');self.play(g,m)
        self.assertIn(m,g.players[1].board);self.assertFalse(self.casts(g))
    def test_reborn_is_new_random_target(self):
        g=self.game();m=g._summon(1,'EDR_851t');m.keywords.add('REBORN');self.play(g,m)
        self.assertFalse(g.players[1].minions);self.assertEqual(len(self.casts(g)),1)
    def test_deathrattle_summon_is_available_to_recast(self):
        g=self.game();m=g._summon(1,'CORE_EX1_110');m.health=2;self.play(g,m)
        baine=g.players[1].minions[0];self.assertEqual(baine.card_id,'TOKEN_BAINE');self.assertEqual(baine.health,g.cards['TOKEN_BAINE']['health']-2)
    def test_countered_spell_never_starts_chain(self):
        from expanded.game import Card
        g=self.game();m=g._summon(1,'EDR_851t');g.players[1].secrets.append(Card(g._new_id(),'CORE_EX1_287'));self.play(g,m)
        self.assertIn(m,g.players[1].board);self.assertFalse(self.casts(g))
    def test_recasts_not_extra_hand_plays(self):
        g=self.game();ms=[g._summon(1,'EDR_851t') for _ in range(3)];self.play(g,ms[0])
        p=g.players[0];self.assertEqual(p.cards_played,1);self.assertEqual(p.spells_turn,['JAIL_515']);self.assertEqual(len(p.played_history),1)
    def test_spell_damage_applies_to_each_recast(self):
        g=self.game();s=g._summon(0,'END_022');s.health-=1
        ms=[g._summon(1,'CS3_020') for _ in range(2)]
        for m in ms:m.health=4
        self.play(g,ms[0]);self.assertFalse(g.players[1].minions)
    def test_chain_does_not_hit_hero_or_friendly(self):
        g=self.game();f=g._summon(0,'EDR_851t');m=g._summon(1,'EDR_851t');self.play(g,m)
        self.assertIn(f,g.players[0].board);self.assertEqual(g.players[1].health,30)
    def test_transformed_target_is_not_a_death(self):
        g=self.game();m=g._summon(1,'CS3_020');original=g._deal_effect
        def effect(target,amount,ctx):
            result=original(target,amount,ctx);g._transform(g._find(target),'EDR_851t');return result
        with patch.object(g,'_deal_effect',side_effect=effect):self.play(g,m)
        self.assertFalse(self.casts(g));self.assertEqual(len(g.players[1].minions),1)

if __name__=='__main__':unittest.main()

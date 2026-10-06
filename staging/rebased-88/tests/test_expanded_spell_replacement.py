import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class SpellReplacementTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('SHAMAN',31),random_deck('MAGE',53)],seed=71)
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:
            p.hand=[];p.board=[];p.deck=['CORE_CS2_029']*30;p.mana=p.max_mana=10;p.health=30;p.armor=0
        return g
    def hit(self,g,m,amount=2,owner=0,cid='TIME_218',**extra):
        ctx=dict(owner=owner,source=None,target=m.uid,bonus=0,lifesteal=False,spell=True,card_id=cid);ctx.update(extra)
        return g._deal_effect(m.uid,amount,ctx)
    def play(self,g,cid,target=0):
        c=g._enter_hand(g.current,Card(g._new_id(),cid))
        g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==target))
    def test_nature_spell_replaces_lethal_with_fixed_buff(self):
        g=self.game();m=g._summon(0,'TIME_214');self.assertEqual(self.hit(g,m,99),0)
        self.assertEqual((m.attack,m.health,m.max_health),(3,5,5))
    def test_repeated_hits_each_buff(self):
        g=self.game();m=g._summon(0,'TIME_214');self.hit(g,m);self.hit(g,m)
        self.assertEqual((m.attack,m.health),(5,6))
    def test_spell_damage_does_not_increase_buff(self):
        g=self.game();m=g._summon(0,'TIME_214');self.hit(g,m,2,bonus=10)
        self.assertEqual((m.attack,m.health),(3,5))
    def test_zero_damage_not_replaced(self):
        g=self.game();m=g._summon(0,'TIME_214');self.hit(g,m,0)
        self.assertEqual((m.attack,m.health),(1,4))
    def test_enemy_nature_spell_damages_normally(self):
        g=self.game();m=g._summon(0,'TIME_214');self.assertEqual(self.hit(g,m,2,owner=1),2)
        self.assertEqual((m.attack,m.health),(1,2))
    def test_non_nature_spell_damages_normally(self):
        g=self.game();m=g._summon(0,'TIME_214');self.hit(g,m,2,cid='CORE_CS2_029');self.assertEqual(m.health,2)
    def test_non_spell_nature_card_context_does_not_replace(self):
        g=self.game();m=g._summon(0,'TIME_214');self.hit(g,m,2,spell=False);self.assertEqual(m.health,2)
    def test_missing_card_provenance_does_not_infer_nature(self):
        g=self.game();m=g._summon(0,'TIME_214');self.hit(g,m,2,cid=None);self.assertEqual(m.health,2)
    def test_silence_removes_replacement(self):
        g=self.game();m=g._summon(0,'TIME_214');g._silence(m);self.hit(g,m,2);self.assertEqual(m.health,2)
    def test_divine_shield_not_consumed_by_replaced_hit(self):
        g=self.game();m=g._summon(0,'TIME_214');m.keywords.add('DIVINE_SHIELD');self.hit(g,m)
        self.assertIn('DIVINE_SHIELD',m.keywords);self.assertEqual(m.attack,3)
    def test_lifesteal_and_damage_counter_do_not_count_replacement(self):
        g=self.game();g.players[0].health=10;m=g._summon(0,'TIME_214');self.hit(g,m,lifesteal=True)
        self.assertEqual(g.players[0].health,10);self.assertEqual(g.players[0].spell_damage_turn,0)
    def test_buff_preserves_existing_damage(self):
        g=self.game();m=g._summon(0,'TIME_214');m.health=1;self.hit(g,m)
        self.assertEqual((m.health,m.max_health),(2,5))
    def test_actual_static_shock_buffs_and_gives_hero_attack(self):
        g=self.game();m=g._summon(0,'TIME_214');self.play(g,'TIME_218',m.uid)
        self.assertEqual((m.attack,m.health),(3,5));self.assertEqual(g.players[0].temporary_attack,1)
    def test_area_damage_replaces_only_friendly_flux(self):
        g=self.game();a=g._summon(0,'TIME_214');b=g._summon(1,'TIME_214');self.play(g,'TIME_215')
        self.assertEqual((a.attack,a.health),(3,5));self.assertEqual((b.attack,b.health),(1,3))
    def test_followup_if_survives_still_draws(self):
        g=self.game();m=g._summon(0,'TIME_214');self.play(g,'TIME_216',m.uid)
        self.assertEqual((m.attack,m.health),(3,5));self.assertEqual(len(g.players[0].hand),2)
    def test_combat_does_not_replace(self):
        g=self.game();m=g._summon(0,'TIME_214');e=g._summon(1,'EDR_851t');g._force_attack(e.uid,m.uid)
        self.assertEqual(m.attack,1);self.assertEqual(m.health,4-e.attack)

if __name__=='__main__':unittest.main()

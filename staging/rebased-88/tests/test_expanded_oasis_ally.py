import unittest
from unittest.mock import patch
from expanded import Game,Action,random_deck
from expanded.game import Card

class OasisAllyTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('WARRIOR',31),random_deck('MAGE',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        for p in self.g.players:p.hand=[];p.deck=['CORE_CS2_029']*10;p.mana=p.max_mana=10
        self.secret=Card(self.g._new_id(),'CORE_BAR_812');self.q.secrets.append(self.secret)
        self.a=self.g._summon(0,'CS3_025');self.a.summoned_turn=-1
        self.b=self.g._summon(1,'CS3_025')
    def test_summons_before_combat_without_redirecting(self):
        resolve=self.g._resolve_combat
        def checked(source,target,listeners):
            self.assertEqual(target,self.b.uid)
            self.assertEqual(self.q.minions[-1].card_id,'CS2_033')
            self.assertEqual(self.b.health,6)
            return resolve(source,target,listeners)
        with patch.object(self.g,'_resolve_combat',side_effect=checked):self.g.step(Action('attack',self.a.uid,self.b.uid))
        self.assertEqual(self.q.secrets,[]);self.assertEqual(self.b.health,3)
    def test_hero_attack_on_minion_triggers(self):
        self.g._equip(0,'CS2_082');self.g.step(Action('attack',-1,self.b.uid))
        self.assertEqual(self.q.minions[-1].card_id,'CS2_033');self.assertEqual(self.q.secrets,[])
    def test_attacking_hero_does_not_trigger(self):
        self.g.step(Action('attack',self.a.uid,-2));self.assertEqual(self.q.secrets,[self.secret])
    def test_full_board_keeps_secret_even_if_combat_frees_space(self):
        for _ in range(6):self.g._summon(1,'CS3_025')
        self.b.health=1;self.g.step(Action('attack',self.a.uid,self.b.uid))
        self.assertEqual(len(self.q.board),6);self.assertEqual(self.q.secrets,[self.secret])
    def test_own_turn_and_spell_damage_do_not_trigger(self):
        self.g.current=1;self.assertFalse(self.g._secret_event('attack',0,source=self.a.uid,target=self.b.uid))
        self.g.current=0;self.g._damage(self.b.uid,1);self.g._settle()
        self.assertEqual(self.q.secrets,[self.secret]);self.assertEqual(len(self.q.minions),1)
    def test_secret_identity_hidden_until_revealed(self):
        view=self.g.observe(0);self.assertNotIn('secrets',view['players'][1])
        self.g.step(Action('attack',self.a.uid,self.b.uid))
        self.assertTrue(any(e.get('event')=='secret_revealed' and e.get('card')=='CORE_BAR_812' for e in self.g.events))
    def test_prior_freezing_trap_cancels_before_oasis(self):
        self.q.secrets.insert(0,Card(self.g._new_id(),'CORE_EX1_611'))
        self.g.step(Action('attack',self.a.uid,self.b.uid))
        self.assertEqual(self.q.secrets,[self.secret]);self.assertEqual(len(self.q.minions),1)

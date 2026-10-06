import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class PreSpellTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('MAGE',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        for p in self.g.players:p.hand=[];p.deck=['CORE_CS2_029']*10;p.mana=p.max_mana=10
    def play(self,cid='CORE_CS2_029',target=-2):
        c=Card(self.g._new_id(),cid);self.g.players[self.g.current].hand.append(c);self.g.step(Action('play',c.uid,target))
    def test_cho_copies_before_spell_kills_it(self):
        m=self.g._summon(0,'CORE_EX1_100');self.play(target=m.uid)
        self.assertNotIn(m,self.p.minions);self.assertEqual([c.card_id for c in self.q.hand],['CORE_CS2_029'])
    def test_counterspell_still_allows_pre_spell_rewards(self):
        self.g._summon(0,'CORE_EX1_100');self.g._summon(0,'CORE_EX1_559')
        self.q.secrets.append(Card(self.g._new_id(),'CORE_EX1_287'));self.play()
        self.assertEqual((len(self.p.hand),len(self.q.hand),self.q.health),(1,1,30))
    def test_opponent_cast_copies_to_other_player_regardless_cho_owner(self):
        self.g._summon(1,'CORE_EX1_100');self.g.step(Action('end'));self.play(target=-1)
        self.assertEqual([c.card_id for c in self.p.hand],['CORE_CS2_029'])
    def test_silence_disables_cho(self):
        m=self.g._summon(0,'CORE_EX1_100');self.g._silence(m);self.play();self.assertEqual(self.q.hand,[])
    def test_full_hand_burns_copy(self):
        self.g._summon(0,'CORE_EX1_100');self.q.hand=[Card(self.g._new_id(),'CORE_CS2_029') for _ in range(10)]
        self.play();self.assertEqual(len(self.q.hand),10)
    def test_two_chos_do_not_recursively_copy_generated_cards(self):
        self.g._summon(0,'CORE_EX1_100');self.g._summon(1,'CORE_EX1_100');self.play('TOKEN_COIN',0)
        self.assertEqual([c.card_id for c in self.q.hand],['TOKEN_COIN','TOKEN_COIN'])
    def test_secret_copied_on_play_not_trigger(self):
        self.g._summon(0,'CORE_EX1_100');self.play('CORE_EX1_287',0)
        self.assertEqual([c.card_id for c in self.q.hand],['CORE_EX1_287']);self.assertEqual(len(self.p.secrets),1)

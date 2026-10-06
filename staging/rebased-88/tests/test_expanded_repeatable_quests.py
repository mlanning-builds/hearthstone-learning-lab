"""Repeatable summon Quest boundaries, including developer-described group timing."""
import copy
import unittest
from unittest.mock import patch
from expanded import Game,Action,random_deck
from expanded.cards import RULES,TRIGGERS
from expanded.features import SCHEMA,encode_decision

class RepeatableQuestTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('PALADIN',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        for p in self.g.players:p.hand=[];p.board=[];p.deck=[];p.mana=p.max_mana=10
    def play(self,cid):
        c=self.g._add(0,cid)
        self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid))
    def quest(self):self.play('TLC_426')
    def summon(self,owner=0):return self.g._summon(owner,'CORE_EX1_506')
    def clear(self):
        for m in self.p.minions:m.health=0
        self.g._settle()
    def complete(self):
        for _ in range(6):self.summon()

    def test_sixth_completes_without_buffing_existing_murlocs(self):
        self.quest();self.complete()
        self.assertEqual(self.p.murloc_summon_bonus,1)
        self.assertEqual(self.p.quest['progress'],0);self.assertEqual(self.p.quest['completions'],1)
        self.assertTrue(all((m.attack,m.health)==(2,1) for m in self.p.minions))
        seventh=self.summon();self.assertEqual((seventh.attack,seventh.health),(3,2))
        self.assertEqual(self.p.quest['progress'],1)

    def test_three_summons_cross_cycle_boundary_individually(self):
        self.quest()
        for _ in range(5):self.summon()
        self.clear()
        self.g._start_play_effects((('summon','CORE_EX1_506',3),),dict(owner=0,source=None,target=0,bonus=0,lifesteal=False))
        self.assertEqual([(m.attack,m.health) for m in self.p.minions],[(2,1),(3,2),(3,2)])
        self.assertEqual(self.p.quest['progress'],2)

    def test_second_cycle_stacks_only_for_future_summons(self):
        self.quest();self.complete();self.clear();self.complete()
        self.assertEqual(self.p.murloc_summon_bonus,2);self.assertEqual(self.p.quest['completions'],2)
        self.assertTrue(all((m.attack,m.health)==(3,2) for m in self.p.minions))
        m=self.summon();self.assertEqual((m.attack,m.health),(4,3))

    def test_completion_has_no_card_payment_or_hand_reward(self):
        self.quest();self.p.mana=0
        for _ in range(10):self.g._add(0,'TOKEN_COIN')
        self.complete();self.assertEqual((self.p.mana,len(self.p.hand),self.p.cards_played,self.p.quests_played),(0,10,1,1))

    def test_repeat_keeps_quest_slot_occupied(self):
        self.quest();self.complete();c=self.g._add(0,'TLC_239')
        self.assertFalse(any(a.kind=='play' and a.source==c.uid for a in self.g.legal_actions()))
        self.assertEqual(self.p.quest['card_id'],'TLC_426')

    def test_enemy_and_non_murloc_summons_do_not_count(self):
        self.quest();self.summon(1);self.g._summon(0,'EDR_851t')
        self.assertEqual(self.p.quest['progress'],0)

    def test_failed_full_board_summon_does_not_count(self):
        self.quest()
        for _ in range(7):self.g._summon(0,'EDR_851t')
        self.assertIsNone(self.summon());self.assertEqual(self.p.quest['progress'],0)

    def test_prior_summons_do_not_count_retroactively(self):
        self.summon();self.quest();self.assertEqual(self.p.quest['progress'],0)

    def test_record_disabled_still_progresses(self):
        self.g.record=False;self.quest();self.complete()
        self.assertEqual(self.p.murloc_summon_bonus,1)

    def test_silence_removes_enchantment_not_player_bonus(self):
        self.p.murloc_summon_bonus=2;m=self.summon()
        self.assertEqual((m.attack,m.health),(4,3))
        self.g._silence(m);self.assertEqual((m.attack,m.health),(2,1))
        self.assertEqual(self.p.murloc_summon_bonus,2)
        self.g._refresh_auras();self.assertEqual(m.attack,2)

    def test_copy_gets_its_own_summon_bonus(self):
        self.p.murloc_summon_bonus=1;m=self.summon()
        other=self.g._summon(0,m.card_id,copy_from=m)
        self.assertEqual((m.attack,m.health),(3,2));self.assertEqual((other.attack,other.health),(4,3))

    def test_reborn_bonus_applies_after_one_health_initialization(self):
        self.p.murloc_summon_bonus=2;m=self.summon();m.keywords.add('REBORN')
        m.health=0;self.g._settle();reborn=self.p.minions[0]
        self.assertEqual((reborn.attack,reborn.health,reborn.max_health),(4,3,3))
        self.assertNotIn('REBORN',reborn.keywords)

    def test_played_minion_publishes_only_once(self):
        self.quest()
        with patch.dict(RULES,{'CORE_EX1_506':('none',[])}):self.play('CORE_EX1_506')
        self.assertEqual(self.p.quest['progress'],1)
        self.g._publish_pending_summon(self.p.minions[0]);self.assertEqual(self.p.quest['progress'],1)

    def test_summon_listener_choice_resumes_group_without_recounting(self):
        self.g._summon(0,'CORE_EX1_509');self.quest();self.p.quest['progress']=5
        rule=(('summon','friendly','MURLOC'),[('discover_deck',)])
        self.p.deck=['CORE_CS2_029']*3
        with patch.dict(TRIGGERS,{'CORE_EX1_509':rule}):
            c=self.g._add(0,'CORE_DS1_184')
            with patch.dict(RULES,{'CORE_DS1_184':('none',[('summon','CORE_EX1_506',2)])}):
                self.g.step(Action('play',c.uid))
                self.assertEqual(self.p.quest['progress'],0);self.assertEqual(self.p.murloc_summon_bonus,1)
                self.g.step(Action('choose',choices=(0,)))
                self.assertEqual(self.p.quest['progress'],1)
                self.g.step(Action('choose',choices=(0,)))
        self.assertEqual(self.p.quest['progress'],1);self.assertEqual(self.p.murloc_summon_bonus,1)

    def test_completion_ignores_enemy_counterspell(self):
        self.quest();self.q.secrets=[self.g._add(1,'CORE_EX1_287')];self.q.hand=[]
        self.complete();self.assertEqual(len(self.q.secrets),1)
        self.assertEqual(self.p.murloc_summon_bonus,1)

    def test_public_progress_bonus_and_schema(self):
        self.quest();self.complete();view=self.g.observe(0)
        self.assertEqual(self.g.observe(1)['players'][0]['murloc_summon_bonus'],1)
        self.assertEqual(self.g.observe(1)['players'][0]['quest']['completions'],1)
        rows=encode_decision(dict(actor=0,observation=view,actions=view['legal_actions']))
        self.assertTrue(any('murloc_summon_bonus' in str(row) for row in rows));self.assertEqual(SCHEMA,'visible-action-features-v58')

    def test_copy_game_preserves_repeat_progress(self):
        self.quest();self.complete();other=copy.deepcopy(self.g)
        a=self.summon();b=other._summon(0,'CORE_EX1_506')
        self.assertEqual((a.attack,a.health),(b.attack,b.health))
        self.assertEqual(self.p.quest,other.players[0].quest)

    def test_sacred_cave_token_grants_persistent_bonus(self):
        self.play('TLC_426t');m=self.summon()
        self.assertEqual((m.attack,m.health),(3,2));self.assertIsNone(self.p.quest)

    def test_tyrannogill_developer_example(self):
        self.quest()
        for _ in range(4):self.summon()
        self.clear();self.play('TLC_240')
        self.assertEqual(self.p.quest['progress'],5)
        self.p.minions[0].health=0;self.g._settle()
        self.assertEqual([(m.attack,m.health) for m in self.p.minions],[(2,1),(3,2),(3,2)])
        self.assertEqual(self.p.quest['progress'],2)

    def test_failed_effect_rolls_back_completion_and_bonus(self):
        from engine.cards import UnsupportedCard
        self.quest();self.p.quest['progress']=5;c=self.g._add(0,'CORE_DS1_184')
        before=copy.deepcopy(self.g.__dict__)
        with patch.dict(RULES,{'CORE_DS1_184':('none',[('summon','CORE_EX1_506',2),('unknown_operation',)])}):
            with self.assertRaises(UnsupportedCard):self.g.step(Action('play',c.uid))
        self.assertEqual(self.g.players,before['players'])
        self.assertEqual(self.g.rng.getstate(),before['rng'].getstate())
        self.assertIsNone(self.g.pending_frame)

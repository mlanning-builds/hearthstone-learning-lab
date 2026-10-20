import unittest
import test_expanded_historical_death as fixtures
from expanded import cards
RECIPES={'AV_211': ('AV_211t', 1),
 'AV_309': ('AV_309t', 1),
 'BAR_072': ('BAR_072t', 1),
 'BAR_751': ('BAR_751t', 1),
 'BOT_066': ('BOT_066t', 1),
 'BOT_445': ('BOT_445t', 1),
 'BOT_537': ('BOT_537t', 1),
 'BOT_565': ('BOT_565t', 1),
 'BT_008': ('BT_008t', 1),
 'BT_155': ('BT_155t', 1),
 'BT_304': ('BT_304t', 1),
 'BT_703': ('BT_703t', 1),
 'BT_726': ('BT_726t', 1),
 'BT_728': ('BT_728t', 1),
 'BT_761': ('BT_761t', 1),
 'DAL_088': ('DAL_088t2', 1),
 'DAL_566': ('DAL_566t', 4),
 'DAL_743': ('DAL_743t', 1),
 'DMF_223': ('DMF_223t', 2),
 'DMF_533': ('DMF_533t', 2),
 'ETC_526': ('ETC_526t', 1),
 'KAR_005': ('KAR_005a', 1),
 'LOOT_153': ('LOOT_153t1', 7),
 'LOOT_233': ('LOOT_233t', 1),
 'OG_216': ('OG_216a', 2),
 'OG_241': ('OG_241a', 1),
 'OG_249': ('OG_249a', 1),
 'OG_272': ('OG_272t', 1),
 'REV_012': ('REV_012t', 1),
 'REV_356': ('REV_350t', 1),
 'REV_375': ('REV_375t', 1),
 'RLK_070': ('RLK_070t', 1),
 'RLK_554': ('RLK_554t', 1),
 'RLK_833': ('RLK_833t', 1),
 'SCH_340': ('SCH_340t', 1),
 'SW_455': ('SW_455t', 5),
 'TOY_914': ('TOY_914t', 2),
 'TRL_503': ('TRL_503t', 3),
 'TRL_531': ('TRL_531t', 1),
 'TTN_861': ('TTN_862t4', 2),
 'ULD_174': ('ULD_174t', 1),
 'UNG_010': ('UNG_201t', 3),
 'UNG_076': ('UNG_076t1', 2),
 'UNG_083': ('UNG_083t1', 1)}

class LinkedDeathTests(unittest.TestCase):
 def test_generated_dependencies_keep_standard_deck_membership_closed(self):
  from expanded.historical_generation import validate_past_candidates
  roots=set(RECIPES);children={child for child,n in RECIPES.values()}
  self.assertFalse((roots|children)&cards.COLLECTIBLE_IDS)
  self.assertTrue((roots|children)<=cards.PLAYABLE_TOKENS)
  records=cards.registry();validate_past_candidates(roots,records)

 def game(self):
  return fixtures.HistoricalDeathTests().game()
 def paid(self,g,cid):return fixtures.HistoricalDeathTests().paid(g,cid)
 def kill(self,g,m):m.health=0;g._settle();g.assert_invariants()
 def test_all_literal_death_children_have_printed_stats_and_fresh_uids(self):
  for cid,(child,n) in RECIPES.items():
   with self.subTest(cid=cid):
    g=self.game();m=self.paid(g,cid);self.kill(g,m);children=[x for x in g.players[0].minions if x.card_id==child];self.assertEqual(len(children),n)
    for x in children:self.assertEqual((x.attack,x.health,x.max_health),(g.cards[child]['attack'],g.cards[child]['health'],g.cards[child]['health']));self.assertNotEqual(x.uid,m.uid)
    self.assertEqual(len({x.uid for x in children}),n)
 def test_all_silenced_sources_have_no_printed_death_children(self):
  for cid in RECIPES:
   g=self.game();m=self.paid(g,cid);g._silence(m);self.kill(g,m);self.assertFalse(g.players[0].board)
 def test_full_board_only_retains_one_child_and_stops_at_capacity(self):
  for cid,(child,n) in RECIPES.items():
   g=self.game();m=self.paid(g,cid)
   for _ in range(6):g._summon(0,'CS2_182')
   self.kill(g,m);self.assertEqual(len(g.players[0].board),7);self.assertEqual(sum(x.card_id==child for x in g.players[0].minions),1)
 def test_children_occupy_source_position_between_surviving_neighbors(self):
  for cid,(child,n) in RECIPES.items():
   g=self.game();left=g._summon(0,'CS2_182');m=self.paid(g,cid);right=g._summon(0,'CS2_182');g.players[0].board[:]=[left,m,right];self.kill(g,m)
   ids=[x.card_id for x in g.players[0].minions if x.card_id!=cid];self.assertEqual(ids,['CS2_182']+[child]*min(n,5)+['CS2_182'])
 def test_summon_children_do_not_inherit_source_permanent_buffs(self):
  for cid,(child,n) in RECIPES.items():
   g=self.game();m=self.paid(g,cid);g._buff(m,5,7);self.kill(g,m)
   for x in g.players[0].minions:
    if x.card_id==child:self.assertEqual((x.attack,x.health),(g.cards[child]['attack'],g.cards[child]['health']))
 def test_impcaster_spell_damage_and_silence(self):
  g=self.game();m=self.paid(g,'BT_008');self.kill(g,m);child=g.players[0].minions[0];self.assertEqual(g._spell_damage(0),1);g._silence(child);self.assertEqual(g._spell_damage(0),0)
 def test_dreadlord_lifesteal_from_combat(self):
  g=self.game();m=self.paid(g,'BT_304');self.kill(g,m);g.players[0].health=20;child=g.players[0].minions[0];child.summoned_turn=g.turn-1;g.step(next(a for a in g.legal_actions() if a.kind=='attack' and a.source==child.uid and a.target==g.hero_id(1)));self.assertEqual(g.players[0].health,25)
 def test_blight_boar_charge_and_taunt_affect_legal_attacks(self):
  g=self.game();m=self.paid(g,'ETC_526');self.kill(g,m);child=g.players[0].minions[0]
  self.assertTrue(any(a.kind=='attack' and a.source==child.uid and a.target==g.hero_id(1) for a in g.legal_actions()))
  enemy=g._summon(1,'CS2_182');enemy.summoned_turn=g.turn-1;g.current=1
  attacks=[a for a in g.legal_actions() if a.kind=='attack' and a.source==enemy.uid]
  self.assertTrue(any(a.target==child.uid for a in attacks));self.assertFalse(any(a.target==g.hero_id(0) for a in attacks))
 def test_stealth_wolf_rejects_enemy_spell_target(self):
  g=self.game();m=self.paid(g,'AV_211');self.kill(g,m);child=g.players[0].minions[0];g.current=1;g.players[1].mana=10;c=g._add(1,'CS2_008')
  self.assertFalse(any(a.kind=='play' and a.source==c.uid and a.target==child.uid for a in g.legal_actions()))
 def test_harkener_reborn_can_die_again_and_summon_second_child(self):
  g=self.game();m=self.paid(g,'RLK_554');self.kill(g,m);reborn=next(x for x in g.players[0].minions if x.card_id=='RLK_554');self.assertEqual(reborn.health,1);self.assertNotIn('REBORN',reborn.keywords);self.kill(g,reborn);self.assertEqual([x.card_id for x in g.players[0].minions],['RLK_554t','RLK_554t'])

if __name__=="__main__":unittest.main()

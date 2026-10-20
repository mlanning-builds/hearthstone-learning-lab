"""Physical Magnetic play, attachment lifetime and inherited attack triggers."""
import unittest
from engine.cards import UnsupportedCard
from expanded import Action,cards
import test_expanded_generation as fixtures
class MagneticTests(unittest.TestCase):
 def game(self):return fixtures.GenerationTests().game()
 def play(self,g,cid,position):
  c=g._add(0,cid);g.players[0].mana=10
  g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid and a.position==position));return c
 def test_left_attach_and_right_body_are_distinct_legal_placements(self):
  for position,attached in ((0,True),(1,False)):
   g=self.game();host=g._summon(0,'GVG_058');before=(host.attack,host.max_health)
   self.play(g,'BOT_906',position)
   self.assertEqual(len(g.players[0].board),1 if attached else 2)
   self.assertEqual((host.attack,host.max_health),tuple(v+b for v,b in zip(before,(1,3))) if attached else before)
   self.assertEqual(g.players[0].cards_played,1)
 def test_full_board_only_allows_valid_attachment_positions(self):
  g=self.game();host=g._summon(0,'GVG_058')
  for _ in range(6):g._summon(0,'CORE_EX1_162')
  before=host.attack
  c=g._add(0,'BOT_906');actions=[a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid]
  self.assertEqual([a.position for a in actions],[0]);g.step(actions[0]);self.assertEqual(len(g.players[0].board),7);self.assertEqual(host.attack,before+1)
 def test_prosthetic_hand_can_attach_to_undead_and_grants_reborn(self):
  g=self.game();host=g._summon(0,'NX2_018');self.play(g,'DEEP_015',0)
  self.assertEqual(len(g.players[0].board),1);self.assertIn('REBORN',host.keywords)
  host.health=0;g._settle();reborn=g.players[0].minions[0];self.assertEqual(reborn.card_id,'NX2_018');self.assertEqual(reborn.health,1);self.assertNotIn('REBORN',reborn.keywords);self.assertFalse(reborn.rule_state.get('magnetic_parts'))
 def test_attack_readiness_damage_and_physical_hand_stats_are_preserved(self):
  g=self.game();host=g._summon(0,'GVG_058');host.summoned_turn=-1;host.keywords.discard('DIVINE_SHIELD');g._damage(host.uid,1);host.attacks=1
  c=g._add(0,'BOT_906');c.attack_bonus=2;c.health_bonus=4;uid=host.uid;sick=host.summoned_turn
  g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid and a.position==0))
  self.assertEqual((host.uid,host.summoned_turn,host.attacks),(uid,sick,1));self.assertEqual((host.attack,host.max_health,host.health),(5,9,8))
 def test_annoy_module_keywords_are_transferred_and_silence_removes_parts(self):
  g=self.game();host=g._summon(0,'TTN_906');self.play(g,'BOT_911',0)
  self.assertTrue({'DIVINE_SHIELD','TAUNT'}<=host.keywords);self.assertEqual(host.rule_state['magnetic_parts'][0]['card_id'],'BOT_911')
  g._silence(host);self.assertFalse(host.rule_state.get('magnetic_parts'));self.assertNotIn('TAUNT',host.keywords);self.assertEqual((host.attack,host.max_health),(1,3))
 def test_noble_attack_trigger_stacks_on_host_and_silence_clears_it(self):
  g=self.game();host=g._summon(0,'GVG_058');host.summoned_turn=-1
  self.play(g,'TTN_852',0);self.play(g,'TTN_852',0);target=g._add(0,'CORE_EX1_162');g.step(Action('attack',host.uid,-2))
  self.assertEqual((target.attack_bonus,target.health_bonus),(2,2));g._silence(host);host.attacks=0;g.step(Action('attack',host.uid,-2));self.assertEqual(target.attack_bonus,2)
 def test_new_attachment_trigger_works_on_a_previously_silenced_host(self):
  g=self.game();host=g._summon(0,'GVG_058');g._silence(host);host.summoned_turn=-1;self.play(g,'TTN_852',0);target=g._add(0,'CORE_EX1_162')
  g.step(Action('attack',host.uid,-2));self.assertEqual(target.attack_bonus,1)
 def test_standalone_noble_trigger_uses_its_printed_ability(self):
  g=self.game();self.play(g,'TTN_852',0);host=g.players[0].minions[0];host.summoned_turn=-1;target=g._add(0,'CORE_EX1_162');g.step(Action('attack',host.uid,-2));self.assertEqual(target.attack_bonus,1)
 def test_repairbot_returns_exact_base_identities_without_hand_enchantments(self):
  g=self.game();host=g._summon(0,'TTN_906');a=self.play(g,'BOT_906',0);self.play(g,'BOT_911',0);host.health=0;g._settle()
  self.assertEqual([c.card_id for c in g.players[0].hand],['BOT_906','BOT_911']);self.assertTrue(all(c.attack_bonus==c.health_bonus==0 for c in g.players[0].hand));self.assertNotEqual(g.players[0].hand[0].uid,a.uid)
 def test_silenced_repairbot_does_not_return_attachments(self):
  g=self.game();host=g._summon(0,'TTN_906');self.play(g,'BOT_906',0);g._silence(host);host.health=0;g._settle();self.assertFalse(g.players[0].hand)
 def test_board_copy_keeps_attached_triggers_bounce_resets_them(self):
  g=self.game();host=g._summon(0,'GVG_058');self.play(g,'TTN_852',0);copy=g._summon(0,host.card_id,copy_from=host,entry_origin='copy');copy.summoned_turn=-1;target=g._add(0,'CORE_EX1_162');g.step(Action('attack',copy.uid,-2));self.assertEqual(target.attack_bonus,1)
  g._bounce(copy);returned=g.players[0].hand[-1];self.assertEqual(returned.card_id,'GVG_058');self.assertFalse(getattr(returned,'rule_state',{}).get('magnetic_parts'))
 def test_attachment_does_not_publish_summon_or_trigger_explosive_runes(self):
  g=self.game();host=g._summon(0,'GVG_058');g._place_secret(1,'CORE_LOOT_101');g.events=[];self.play(g,'BOT_906',0)
  self.assertEqual(len(g.players[1].secrets),1);self.assertFalse(any(e['event']=='summon' and e.get('card')=='BOT_906' for e in g.events));self.assertEqual(g.players[0].played_history[-1]['card_id'],'BOT_906')
 def test_generated_only_registrations(self):
  ids={'BOT_906','BOT_911','DEEP_015','TTN_852','TTN_906'};self.assertTrue(ids<=cards.TOKEN_IDS&cards.PLAYABLE_TOKENS);self.assertFalse(ids&cards.COLLECTIBLE_IDS)

 def test_non_mech_and_dormant_hosts_keep_standalone_play(self):
  for cid,dormant in (("CORE_EX1_162",False),("GVG_058",True)):
   g=self.game();host=g._summon(0,cid);host.dormant=dormant
   self.play(g,"BOT_906",0);self.assertEqual(len(g.players[0].board),2);self.assertFalse(host.rule_state.get("magnetic_parts"))
 def test_empty_hand_attack_does_not_consume_randomness(self):
  g=self.game();host=g._summon(0,"GVG_058");host.summoned_turn=-1;self.play(g,"TTN_852",0)
  before=g.rng.getstate();g.step(Action("attack",host.uid,-2));self.assertEqual(g.rng.getstate(),before)
 def test_rejected_composite_attachment_rolls_back_payment_history_and_rng(self):
  g=self.game();host=g._summon(0,"GVG_058");c=g._add(0,"BOT_906");c.rule_state={"dark_gifts":["EDR_100t13"]}
  before=(g.players[0].mana,len(g.history),g.rng.getstate(),host.attack,host.max_health)
  action=next(a for a in g.legal_actions() if a.kind=="play" and a.source==c.uid and a.position==0)
  with self.assertRaises(UnsupportedCard):g.step(action)
  p=g.players[0];self.assertEqual((p.mana,len(g.history),g.rng.getstate(),p.minions[0].attack,p.minions[0].max_health),before);self.assertEqual(p.hand[-1].uid,c.uid)
 def test_repairbot_full_hand_does_not_replace_existing_cards(self):
  g=self.game();host=g._summon(0,"TTN_906");self.play(g,"BOT_906",0)
  held=[g._add(0,"CORE_EX1_162") for _ in range(10)];host.health=0;g._settle()
  self.assertEqual([c.uid for c in g.players[0].hand],[c.uid for c in held]);self.assertFalse(any(c.card_id=="BOT_906" for c in g.players[0].hand))

 def test_historical_keyword_and_vanilla_attachments_transfer_printed_stats(self):
  for cid in ("BOT_020","BOT_021","BOT_035","BOT_237","BOT_548","BOT_563"):
   with self.subTest(cid=cid):
    g=self.game();host=g._summon(0,"TTN_906");before=host.attack,host.max_health;d=g.cards[cid];self.play(g,cid,0)
    self.assertEqual((host.attack,host.max_health),(before[0]+d["attack"],before[1]+d["health"]));self.assertTrue((set(d.get("mechanics",()))-{"MAGNETIC","TRIGGER_VISUAL","BATTLECRY"})<=host.keywords)
 def test_absorbent_parasite_can_attach_to_a_beast(self):
  g=self.game();host=g._summon(0,"CS2_171");before=host.attack;self.play(g,"TTN_087",0)
  self.assertEqual(len(g.players[0].board),1);self.assertEqual(host.attack,before+3);self.assertIn("RUSH",host.keywords)
 def test_spider_bomb_attached_deathrattle_destroys_enemy(self):
  g=self.game();host=g._summon(0,"TTN_906");enemy=g._summon(1,"CORE_EX1_162");self.play(g,"BOT_251",0);host.health=0;g._settle()
  self.assertFalse(g.players[1].minions);self.assertEqual(g.players[0].hand[0].card_id,"BOT_251")
 def test_replicating_menace_uses_exact_three_microbots(self):
  for cid in ("BOT_312",):
   g=self.game();host=g._summon(0,"GVG_058");self.play(g,cid,0);host.health=0;g._settle()
   self.assertEqual([m.card_id for m in g.players[0].minions],["BOT_312t"]*3);self.assertTrue(all((m.attack,m.health)==(1,1) for m in g.players[0].minions))
 def test_coppertail_attached_and_standalone_attacks_add_coin(self):
  for attached in (False,True):
   g=self.game();host=g._summon(0,"GVG_058") if attached else None;self.play(g,"TTN_921",0)
   host=host or g.players[0].minions[0];host.summoned_turn=-1;g.step(Action("attack",host.uid,-2));self.assertEqual([c.card_id for c in g.players[0].hand],["TOKEN_COIN"])
 def test_silence_removes_attached_deathrattle(self):
  g=self.game();host=g._summon(0,"GVG_058");self.play(g,"BOT_312",0);g._silence(host);host.health=0;g._settle();self.assertFalse(g.players[0].minions)
 def test_board_copy_preserves_attached_deathrattle(self):
  g=self.game();host=g._summon(0,"GVG_058");self.play(g,"BOT_312",0);copy=g._summon(0,host.card_id,copy_from=host,entry_origin="copy");copy.health=0;g._settle()
  self.assertEqual([m.card_id for m in g.players[0].minions],["GVG_058"]+["BOT_312t"]*3)

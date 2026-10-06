import unittest
from copy import deepcopy
from expanded.features import encode_decision


def decision():
    action=dict(kind='play',source=10,target=-2,position=-1,choices=[])
    p=dict(health=30,armor=0,board=[],hand=[dict(uid=10,card_id='A',cost=2)])
    q=dict(health=20,armor=1,board=[])
    view=dict(viewer=0,phase='play',turn=2,players=[p,q],legal_actions=[action])
    return dict(actor=0,observation=view,actions=[action])

class FeatureTests(unittest.TestCase):
    def test_hidden_and_replay_information_is_ignored(self):
        d=decision();before=encode_decision(d)
        d['replay_only']={'decks':['SECRET']};d['rewards']=[1,-1]
        d['observation']['players'][1]['hand']=[{'uid':999,'card_id':'SECRET'}]
        d['observation']['events']=[{'card':'SECRET'}]
        self.assertEqual(before,encode_decision(d))
    def test_episode_entity_ids_are_not_features(self):
        d=decision();before=encode_decision(d)
        d['observation']['players'][0]['hand'][0]['uid']=999
        d['actions'][0]['source']=999
        self.assertEqual(before,encode_decision(d))
    def test_visible_card_and_target_health_change_features(self):
        d=decision();before=encode_decision(d)
        d['observation']['players'][0]['hand'][0]['card_id']='B'
        self.assertNotEqual(before,encode_decision(d))
        before=encode_decision(d);d['observation']['players'][1]['health']=1
        self.assertNotEqual(before,encode_decision(d))
    def test_no_mutation(self):
        d=decision();before=deepcopy(d);encode_decision(d);self.assertEqual(d,before)
    def test_reject_nonvisible_action_entity(self):
        d=decision();d['actions'][0]['target']=999
        with self.assertRaises(ValueError):encode_decision(d)
    def test_candidate_order_and_visible_choice_identity(self):
        d=decision();actions=[dict(kind='choose',choices=[i]) for i in (0,1)]
        d['actions']=actions;d['observation']['legal_actions']=actions
        d['observation']['pending_choice']={'options':[{'card_id':'A'},{'card_id':'B'}]}
        rows=encode_decision(d);self.assertNotEqual(rows[0],rows[1])
        actions.reverse();self.assertEqual(encode_decision(d),list(reversed(rows)))

    def test_public_rule_counters_and_history_counts_affect_features(self):
        from expanded.features import RULE_COUNTER_FIELDS
        for key in RULE_COUNTER_FIELDS:
            d=decision();d['observation']['players'][0]['rule_counters']={key:0}
            before=encode_decision(d);d['observation']['players'][0]['rule_counters'][key]=3
            self.assertNotEqual(before,encode_decision(d),key)
        for key in ('discard_history','death_history','shuffle_history'):
            d=decision();d['observation']['players'][1][key]=[];before=encode_decision(d)
            d['observation']['players'][1][key]=['public entry']
            self.assertNotEqual(before,encode_decision(d),key)
    def test_unknown_nested_counters_are_not_consumed(self):
        d=decision();d['observation']['players'][1]['rule_counters']={'fel_spells_cast':1}
        before=encode_decision(d)
        d['observation']['players'][1]['rule_counters']['hidden_hand']=['SECRET']
        self.assertEqual(before,encode_decision(d))
    def test_healing_prevention_and_expiry_are_distinguishable(self):
        d=decision();q=d['observation']['players'][1];q['healing_block_expiry_players']=[]
        before=encode_decision(d);q['healing_block_expiry_players']=[0]
        blocked=encode_decision(d);self.assertNotEqual(before,blocked)
        q['healing_block_expiry_players']=[1];self.assertNotEqual(blocked,encode_decision(d))
        q['healing_block_expiry_players']=[2]
        with self.assertRaises(ValueError):encode_decision(d)
    def test_expiry_players_are_relative_to_viewer(self):
        d=decision();d['observation']['players'][1]['healing_block_expiry_players']=[0]
        before=encode_decision(d)
        d['observation']['players'].reverse();d['observation']['players'][0]['healing_block_expiry_players']=[1]
        d['actor']=d['observation']['viewer']=1;d['actions'][0]['target']=-1
        self.assertEqual(before,encode_decision(d))

    def test_healing_block_is_attached_to_action_target(self):
        import json
        d=decision();d['observation']['players'][1]['healing_block_expiry_players']=[0]
        rows=encode_decision(d)
        self.assertEqual(rows[0][json.dumps(['target','healing_blocked'])],1.0)

    def test_equal_displayed_attack_distinct_underlying_deficits(self):
        d=decision();q=d['observation']['players'][1]
        q['board']=[dict(uid=22,card_id='MINION',attack=0,attack_deficit=0,health=3)]
        d['actions'][0]['target']=22
        before=encode_decision(d);q['board'][0]['attack_deficit']=-2
        after=encode_decision(d);self.assertNotEqual(before,after)
        import json
        self.assertEqual(after[0][json.dumps(['target','entity','attack_deficit'])],-2/3)
        q['board'][0]['uid']=88;d['actions'][0]['target']=88
        self.assertEqual(after,encode_decision(d))

    def test_power_modifiers_distinguish_equal_current_cost(self):
        d=decision();p=d['observation']['players'][0];p['hero_power_cost']=2
        p['next_power_cost_effects']=[];before=encode_decision(d)
        p['next_power_cost_effects']=[dict(kind='set',amount=0),dict(kind='add',amount=2)]
        after=encode_decision(d);self.assertNotEqual(before,after)
        p['next_power_cost_effects'][0]['hidden_hand']=['SECRET']
        self.assertEqual(after,encode_decision(d))

    def test_power_modifier_order_and_relative_seat(self):
        d=decision();p=d['observation']['players'][0]
        p['next_power_cost_effects']=[dict(kind='set',amount=0),dict(kind='add',amount=2)]
        before=encode_decision(d);p['next_power_cost_effects'].reverse()
        self.assertNotEqual(before,encode_decision(d));p['next_power_cost_effects'].reverse()
        d['observation']['players'].reverse();d['actor']=d['observation']['viewer']=1
        d['actions'][0]['target']=-1;self.assertEqual(before,encode_decision(d))

    def test_invalid_power_modifiers_are_rejected(self):
        for effect in (None,{},dict(kind='unknown',amount=2),dict(kind='add',amount=-1),dict(kind='set',amount=True)):
            d=decision();d['observation']['players'][0]['next_power_cost_effects']=[effect]
            with self.assertRaises(ValueError):encode_decision(d)

    def test_visible_history_counts_and_action_source_conditioning(self):
        import json
        d=decision();p=d['observation']['players'][0]
        p['played_history']=[dict(card_id='A',cost=2),dict(card_id='A',cost=2),dict(card_id='B',cost=1)]
        row=encode_decision(d)[0]
        self.assertEqual(row[json.dumps(['source','previous_visible_plays'])],2/3)
        self.assertEqual(row[json.dumps(['state','play','self','played_card_counts','B'])],1/2)
        p['hand'][0]['card_id']='B';self.assertEqual(encode_decision(d)[0][json.dumps(['source','previous_visible_plays'])],1/2)

    def test_history_ignores_unknown_secret_identity_and_nested_private_fields(self):
        d=decision();q=d['observation']['players'][1]
        q['played_history']=[dict(card_id='PUBLIC',cost=1),dict(card_id='SECRET',cost=2)]
        before=encode_decision(d)
        q['played_history'][1]['hidden_identity']='DO_NOT_LEAK'
        q['played_history'][0]['hidden_hand']=['DO_NOT_LEAK']
        self.assertEqual(before,encode_decision(d))
        self.assertFalse(any('SECRET' in key or 'DO_NOT_LEAK' in key for key in before[0]))

    def test_history_is_order_independent_and_seat_relative(self):
        d=decision();p=d['observation']['players'][0]
        p['played_history']=[dict(card_id='A'),dict(card_id='B')];before=encode_decision(d)
        p['played_history'].reverse();self.assertEqual(before,encode_decision(d))
        d['observation']['players'].reverse();d['actor']=d['observation']['viewer']=1
        d['actions'][0]['target']=-1;self.assertEqual(before,encode_decision(d))

    def test_malformed_visible_history_rejected(self):
        for entry in (None,{},dict(card_id=3)):
            d=decision();d['observation']['players'][0]['played_history']=[entry]
            with self.assertRaises(ValueError):encode_decision(d)

    def test_maximum_health_changes_state_and_target_features(self):
        import json
        d=decision();q=d['observation']['players'][1];q['max_health']=30
        before=encode_decision(d)[0];q['max_health']=40;after=encode_decision(d)[0]
        for key in (['state','play','opponent','max_health'],['target','max_health']):
            self.assertNotEqual(before[json.dumps(key)],after[json.dumps(key)])
        self.assertEqual(before[json.dumps(['target','health'])],after[json.dumps(['target','health'])])
    def test_personal_turn_count_is_distinct_from_global_turn(self):
        import json
        d=decision();p=d['observation']['players'][0];p['turns_taken']=1
        before=encode_decision(d)[0];p['turns_taken']=2;after=encode_decision(d)[0]
        self.assertNotEqual(before[json.dumps(['state','play','self','turns_taken'])],after[json.dumps(['state','play','self','turns_taken'])])
        self.assertEqual(before[json.dumps(['state','play','turn'])],after[json.dumps(['state','play','turn'])])
    def test_maximum_health_target_distinguishes_same_health_heroes(self):
        import json
        d=decision();p,q=d['observation']['players'];p['health']=q['health']=20
        p['armor']=q['armor']=0;p['max_health']=30;q['max_health']=40
        d['actions'].append(dict(d['actions'][0],target=-1))
        d['observation']['legal_actions']=d['actions']
        rows=encode_decision(d)
        self.assertNotEqual(rows[0][json.dumps(['target','max_health'])],rows[1][json.dumps(['target','max_health'])])

    def test_opponent_companion_identity_is_not_a_feature(self):
        d=decision();before=encode_decision(d)
        d['observation']['players'][1]['companion_ids']=['HIDDEN_BEAST']*3
        self.assertEqual(encode_decision(d),before)

    def test_own_companion_identity_changes_features(self):
        d=decision();d['observation']['players'][0]['companion_ids']=['BEAST_A']*3;before=encode_decision(d)
        d['observation']['players'][0]['companion_ids']=['BEAST_B']*3
        self.assertNotEqual(encode_decision(d),before)

    def test_herald_and_hero_lifesteal_are_visible_features(self):
        for field,value in (('herald_count',4),('hero_lifesteal',True)):
            d=decision();before=encode_decision(d);d['observation']['players'][1][field]=value
            self.assertNotEqual(before,encode_decision(d))

    def test_colossal_entity_links_are_not_arbitrary_id_features(self):
        d=decision();board=[dict(uid=22,card_id='ARM',attack=2,health=1,rule_state=dict(colossal_parent=33,herald_multiplier=2))]
        d['observation']['players'][1]['board']=board;before=encode_decision(d)
        board[0]['rule_state']['colossal_parent']=999;board[0]['rule_state']['colossal_appendages']=[888,777]
        self.assertEqual(before,encode_decision(d))
        board[0]['rule_state']['herald_multiplier']=4;self.assertNotEqual(before,encode_decision(d))

    def test_colossal_remaining_count_is_visible_but_parent_ids_are_not_features(self):
        d=decision();d['observation']['players'][0]['board']=[dict(uid=30,card_id='CATA_550',rule_state=dict(colossal_remaining=93,colossal_parent=40,colossal_appendages=[41,42]))]
        before=encode_decision(d)
        d['observation']['players'][0]['board'][0]['rule_state'].update(colossal_parent=999,colossal_appendages=[888])
        self.assertEqual(before,encode_decision(d))
        d['observation']['players'][0]['board'][0]['rule_state']['colossal_remaining']=1
        self.assertNotEqual(before,encode_decision(d))

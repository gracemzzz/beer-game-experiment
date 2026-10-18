"""Lossless formatting controls; no model calls or behavior generation."""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from beergame_study.manual_response_formatting import normalize_rule_types


class FormattingTests(unittest.TestCase):
    def raw(self, boolean='Yes', week='10', cost='15'):
        return json.dumps(dict(rules=dict(backlog_includes_current_unfilled_demand=boolean,
            factory_order_week_7_arrival_week=week, three_week_backlog_cost=cost),
            chains=[dict(orders=[[0,4,7,0]],probes=[[16,4]])]), indent=2)

    def test_only_three_string_tokens_changed(self):
        raw=self.raw()
        converted,edits=normalize_rule_types(raw)
        expected=raw.replace('"Yes"','true').replace('"10"','10').replace('"15"','15')
        self.assertEqual(converted,expected)
        self.assertEqual(len(edits),3)
        self.assertEqual(json.loads(raw)['chains'],json.loads(converted)['chains'])

    def test_wrong_answers_are_not_corrected(self):
        converted,_=normalize_rule_types(self.raw('No','9','12'))
        rules=json.loads(converted)['rules']
        self.assertIs(rules['backlog_includes_current_unfilled_demand'],False)
        self.assertEqual(rules['factory_order_week_7_arrival_week'],9)
        self.assertEqual(rules['three_week_backlog_cost'],12)

    def test_explicit_week_and_currency_units_only_change_rule_tokens(self):
        raw=self.raw(week='Week 10',cost='$15')
        converted,edits=normalize_rule_types(raw)
        expected=raw.replace('"Yes"','true').replace('"Week 10"','10').replace('"$15"','15')
        self.assertEqual(converted,expected)
        self.assertEqual(len(edits),3)
        self.assertEqual(json.loads(raw)['chains'],json.loads(converted)['chains'])

    def test_units_do_not_correct_wrong_answers(self):
        converted,_=normalize_rule_types(self.raw('No','Week 9','$12'))
        rules=json.loads(converted)['rules']
        self.assertIs(rules['backlog_includes_current_unfilled_demand'],False)
        self.assertEqual(rules['factory_order_week_7_arrival_week'],9)
        self.assertEqual(rules['three_week_backlog_cost'],12)

    def test_wrong_units_and_ambiguous_unit_text_rejected(self):
        for raw in (self.raw(week='$10'),self.raw(cost='Week 15'),self.raw(week='Week 9 or 10'),self.raw(cost='$15 approximately')):
            with self.subTest(raw=raw),self.assertRaises(ValueError):normalize_rule_types(raw)

    def test_ambiguous_text_and_duplicate_keys_rejected(self):
        for raw in (self.raw('probably'),self.raw(week='ten'),'{"rules":{},"rules":{}}'):
            with self.subTest(raw=raw),self.assertRaises(ValueError):normalize_rule_types(raw)

    def test_already_typed_requires_no_conversion(self):
        with self.assertRaises(ValueError):normalize_rule_types(self.raw(True,10,15))

    def test_orders_are_never_type_converted(self):
        raw=self.raw().replace('\n          4,','\n          "4",')
        converted,_=normalize_rule_types(raw)
        self.assertEqual(json.loads(raw)['chains'],json.loads(converted)['chains'])


if __name__=='__main__':unittest.main()

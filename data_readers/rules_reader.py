import json
from typing import Dict

from src import (
    RuleInfo, ComplexRuleInfo, CompoundRuleInfo
)


class RulesReader:
    def read_rules(self, path: str) -> Dict[str, RuleInfo]:
        with open(path, "r") as f:
            data = json.load(f)

        db_id_to_wfdt_rule_id = {}

        rules = {}
        for wfdt_rule_id, rule_dict in data.items():
            db_id = rule_dict["rule_id"]
            db_id_to_wfdt_rule_id[db_id] = wfdt_rule_id

            info = rule_dict["info"]
            pos_b = rule_dict["pos_b"]
            pos_a = rule_dict["pos_a"]

            compound_rules = rule_dict.get("compound_rules", None)
            complex = rule_dict.get("complex", None)
            if compound_rules:
                head_rules = [
                    rules[db_id_to_wfdt_rule_id[r]]
                    for r in compound_rules["head"]
                ]
                modifier_rules = [
                    [
                        rules[db_id_to_wfdt_rule_id[r]]
                        for r in ms["complex"]
                    ]
                    for ms in compound_rules["modifiers"]
                ]
                rule = CompoundRuleInfo(
                    db_id, info, pos_b, pos_a,
                    head_rules=head_rules,
                    modifier_rules=modifier_rules,
                )
            elif complex:
                subrules = [
                    rules[db_id_to_wfdt_rule_id[subrule_db_id]]
                    for subrule_db_id in complex
                ]
                rule = ComplexRuleInfo(db_id, info, pos_b, pos_a, subrules)
            else:
                short_id = rule_dict["short_id"]
                rule = RuleInfo(short_id, info, pos_b, pos_a)
            rules[wfdt_rule_id] = rule
        return rules

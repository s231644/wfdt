import pandas as pd
from typing import Dict, Tuple, List

from src import (
    LexItem, WFToken,
    RuleInfo, ComplexRuleInfo,
    Inventory
)
from data_readers.abstract_readers import AnalysesReaderAbstract


class DemoNextReader(AnalysesReaderAbstract):
    POS2UPOS = {
        "V": "VERB",
        "Adj": "ADJ",
        "Nf": "NOUN",
        "Nm": "NOUN",
        "Nx": "NOUN",
        "Nmp": "NOUN",
        "Nfp": "NOUN",
        "Nxp": "NOUN",
        "Npf": "NOUN",
        "Npm": "NOUN",
        "Npx": "NOUN",
        "Adv": "ADV",
        "Num": "NUM",
        "Pro": "PRON"
    }

    PROCESS2INFO = {
        "pre": "PFX",
        "suf": "SFX",
        "conv": "CONV",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def build_inventory(self, path: str) -> Inventory:
        derivations_analyses = self.read_dataset(path)

        rules_by_ids = {}
        for k, v in derivations_analyses.items():
            rule_id = v.rule_id  # 'pre-suf:(antiXique)(NOUN) -> ADJ'
            pattern = rule_id[rule_id.find("(")+1:rule_id.find(")")]
            pattern = pattern.replace("X", "-")
            process = rule_id[:rule_id.find(":")]

            if process == "pre-suf":
                affixes = pattern.split('-')
                prefix, suffix = affixes
                suffix_rule = RuleInfo(
                    short_id=f"-{suffix}",
                    info=self.PROCESS2INFO["suf"],
                    pos_b=v.d_from.upos,
                    pos_a=k.upos
                )
                prefix_rule = RuleInfo(
                    short_id=f"{prefix}-",
                    info=self.PROCESS2INFO["pre"],
                    pos_b=k.upos,
                    pos_a=k.upos
                )
                rule = ComplexRuleInfo(
                    short_id="",
                    info="PFX,SFX",
                    pos_b=v.d_from.upos,
                    pos_a=k.upos,
                    simple_rules=[suffix_rule, prefix_rule]
                )
            elif process in ["pre", "suf", "conv"]:
                rule = RuleInfo(
                    short_id=pattern,
                    info=self.PROCESS2INFO[process],
                    pos_b=v.d_from.upos,
                    pos_a=k.upos
                )
            else:
                raise ValueError(process)

            rules_by_ids[rule_id] = rule

        inventory = Inventory(
            word_analyses=derivations_analyses,
            rules_by_ids=rules_by_ids,
        )
        return inventory

    def read_dataset(self, path: str) -> Dict[LexItem, WFToken]:
        results = {}
        df = pd.read_csv(path, sep="\t").astype(str)
        for i in range(len(df)):
            line = df.loc[i]
            if i > 1000:
                break
            analyses = self.read_sample(line)
            for word, analysis in analyses:
                results[word] = analysis
        return results

    def read_sample(self, line: pd.Series) -> List[Tuple[LexItem, WFToken]]:
        derived_lemma = line["graph_1"]
        source_lemma = line["graph_2"]
        xpos_d = line["cat_1"]
        xpos_s = line["cat_2"]
        upos_d = self.POS2UPOS.get(xpos_d, "_")
        upos_s = self.POS2UPOS.get(xpos_s, "_")
        process = line["type_cstr_1"]
        rule_id = line["cstr_1"]

        word = LexItem(
            lemma=derived_lemma,
            form=derived_lemma,
            upos=upos_d,
            xpos=xpos_d
        )

        analysis = WFToken(
            d_from=LexItem(
                lemma=source_lemma,
                form=source_lemma,
                upos=upos_s,
                xpos=xpos_s
            ),
            rule_id=f"{process}:({rule_id})({upos_s}) -> {upos_d}"
        )

        return [(word, analysis)]


inventory = DemoNextReader().build_inventory(
    "../data/fra/demonext/sample.txt"
    # "../data/fra/demonext/relations.csv"
)

query = LexItem(
    lemma='anti-inflammatoire',
    form='anti-inflammatoire',
    upos='NOUN',
    xpos='Nm'
)

inventory.make_subword_tree(
    query
).html(f"examples/{query.lemma}_{query.upos}.html")

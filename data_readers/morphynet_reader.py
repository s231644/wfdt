import pandas as pd
from typing import Dict, Tuple, List

from src import (
    LexItem, WFToken,
    RuleInfo,
    Inventory
)
from data_readers.abstract_readers import AnalysesReaderAbstract


class MorphyNetDerivationalReader(AnalysesReaderAbstract):
    """
    MorphyNet derivational relations (v1) reader.

    fay	faith	V	N	th	suffix
    faith	faithful	N	J	ful	suffix
    faithful	faithfully	J	R	ly	suffix
    faithful	unfaithful	J	J	un	prefix
    faithful	faithfulness	J	N	ness	suffix
    unfaithful	unfaithfulness	J	N	ness	suffix
    faithfulness	unfaithfulness	N	N	un	prefix

    https://github.com/kbatsuren/MorphyNet
    """
    POS2UPOS = {
        "V": "VERB",
        "J": "ADJ",
        "N": "NOUN",
        "R": "ADV"
    }

    PROCESS2INFO = {
        "prefix": "PFX",
        "suffix": "SFX",
    }

    def build_inventory(
            self,
            path: str,
            bracketing_strategy: str = "last",
            **kwargs
    ) -> Inventory:
        derivations_analyses = self.read_dataset(path)
        rules_by_ids = {}
        for k, v in derivations_analyses.items():
            rule_id = v.rule_id  # 'suffix:(-ish)(NOUN) -> ADJ'
            pattern = rule_id[rule_id.find("(")+1:rule_id.find(")")]
            pattern = pattern.replace("X", "-")
            process = rule_id[:rule_id.find(":")]

            if process in ["prefix", "suffix"]:
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
            bracketing_strategy=bracketing_strategy
        )
        return inventory

    def read_dataset(self, path: str) -> Dict[LexItem, WFToken]:
        with open(path, "r") as f:
            lines = f.readlines()
        results = {}
        for line in lines:
            analyses = self.read_sample(line.strip())
            for word, analysis in analyses:
                results[word] = analysis
        return results

    def read_sample(self, line: str) -> List[Tuple[LexItem, WFToken]]:
        (
            source_lemma, derived_lemma, xpos_s, xpos_d, affix, process
        ) = line.strip().split("\t")
        upos_s = self.POS2UPOS[xpos_s]
        upos_d = self.POS2UPOS[xpos_d]

        if process == "suffix":
            affix = f"-{affix}"
        elif process == "prefix":
            affix = f"{affix}-"

        word = LexItem(
            lang=self.lang,
            lemma=derived_lemma,
            form=derived_lemma,
            upos=upos_d,
            xpos=xpos_d
        )

        analysis = WFToken(
            d_from=LexItem(
                lang=self.lang,
                lemma=source_lemma,
                form=source_lemma,
                upos=upos_s,
                xpos=xpos_s
            ),
            rule_id=f"{process}:({affix})({upos_s}) -> {upos_d}"
        )

        return [(word, analysis)]


# inventory = MorphyNetDerivationalReader(lang="eng").build_inventory(
#     "../data/eng/morphynet-d/sample.txt"
# )
#
# query = LexItem(
#     lang="eng",
#     lemma="unfaithfulness",
#     form="unfaithfulness",
#     upos="NOUN",
#     xpos="N"
# )
#
# inventory.make_subword_tree(
#     query
# ).html(f"examples/{query.lang}_{query.lemma}_{query.upos}.html")

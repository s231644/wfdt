import json
from typing import Dict, List, Tuple, Optional

from data_readers.abstract_readers import AnalysesReaderAbstract
from src import (
    LexItem, WFToken,
    RuleInfo, ComplexRuleInfo, CompoundRuleInfo,
    Inventory
)


class UDerReader(AnalysesReaderAbstract):
    """
    Reader for the UDer 1.1 format.
    Now it only supports DErivBase and DerivBase.Ru datasets,
    as they have explicit rule ids.

    220654.0	gewinnen#VERB	gewinnen	VERB						{}
    220654.1	Gewinn#NOUN#Masc	Gewinn	NOUN	Gender=Masc		220654.0	Rule=dVN10&Type=Derivation		{}
    220654.2	Hauptgewinn#NOUN#Masc	Hauptgewinn	NOUN	Gender=Masc		220654.1	Rule=dNN47&Type=Derivation		{}
    220654.4	Gewinner#NOUN#Masc	Gewinner	NOUN	Gender=Masc		220654.0	Rule=dVN03&Type=Derivation		{}

    https://ufal.mff.cuni.cz/universal-derivations


    TODO: support more datasets (perhaps with "UNK" derivational morpheme).
    """
    def build_inventory(
            self,
            path: str,
            rules_path: Optional[str] = None,
            bracketing_strategy: str = "last",
            **kwargs
    ) -> Inventory:
        uder_analyses = self.read_dataset(path)
        if rules_path is not None:
            rules = self.read_rules(rules_path)
        else:
            rules = None

        inventory = Inventory(
            word_analyses=uder_analyses,
            rules_by_ids=rules,
            bracketing_strategy=bracketing_strategy
        )
        return inventory

    def read_dataset(
            self, path: str,
    ) -> Dict[LexItem, WFToken]:
        with open(path, "r") as f:
            lines = f.readlines()

        results = {}
        id_to_lemma = self._read_id_to_lemma(lines)

        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                analyses = self.read_sample(line, id_to_lemma)
            except KeyError:
                # id_to_lemma has no key "" for the root of the tree
                continue
            for word, analysis in analyses:
                results[word] = analysis
        return results

    def read_sample(
            self, line: str, id_to_lemma: Dict[str, LexItem]
    ) -> List[Tuple[LexItem, WFToken]]:
        (
            lid, lemmapos, lemma, pos, _, _, par, wf_meta, _, _
        ) = line.split("\t")
        # TODO: correct affix and POS tags
        head = id_to_lemma[par]
        wf_info = self._read_wf_meta(wf_meta)
        rule_id = wf_info["Rule"]
        if wf_info.get("Type", "Derivation") == "Compounding":
            source_ids = wf_info["Sources"]
            modifiers = [id_to_lemma[s] for s in source_ids if s != par]
        else:
            modifiers = None
        derived_word = LexItem(
            lang=self.lang,
            lemma=lemma,
            form=lemma,
            upos=pos
        )
        analysis = WFToken(
            d_from=head,
            rule_id=rule_id,
            d_modifiers=modifiers
        )
        return [(derived_word, analysis)]

    def _read_id_to_lemma(self, lines: List[str]) -> Dict[str, LexItem]:
        id_to_lemma = {}
        for line in lines:
            line = line.strip()
            if not line:
                continue
            lid, lemmapos, lemma, pos, _, _, _, _, _, _ = line.split("\t")
            id_to_lemma[lid] = LexItem(
                lang=self.lang,
                lemma=lemma,
                form=lemma,
                upos=pos
            )
        return id_to_lemma

    @staticmethod
    def _read_wf_meta(wf_meta: str):
        wf_info = {}
        for elem in wf_meta.split("&"):
            k, v = elem.split("=")
            if k == "Sources":
                # Sources=1144.0,80074.0
                v = v.split(",")
            wf_info[k] = v
        return wf_info

    @staticmethod
    def read_rules(path: str) -> Dict[str, RuleInfo]:
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


# inventory = UDerReader(lang="deu").build_inventory(
#     "../data/deu/derivbase-uder/sample.txt",
#     "../data/deu/rules_sample.json"
# )
#
# query = LexItem(
#     lang="deu",
#     lemma="Gewinner",
#     form="Gewinner",
#     upos="NOUN",
# )
#
# inventory.make_subword_tree(
#     query
# ).html(f"examples/{query.lang}_{query.lemma}_{query.upos}.html")


# inventory = UDerReader(lang="rus").build_inventory(
#     "../data/rus/derivbaseru-uder/sample.txt",
#     "../data/rus/rules_sample.json"
# )
#
# inventory = UDerReader(lang="rus").build_inventory(
#     "../data/rus/rucompounds-uder/sample.txt",
#     "../data/rus/rules_sample.json"
# )
#
#
# query = LexItem(
#     lang="rus",
#     lemma="пятикомнатный",
#     form="пятикомнатный",
#     upos="ADJ",
# )
#
# inventory.make_subword_tree(
#     query
# ).html(f"examples/{query.lang}_{query.lemma}_{query.upos}.html")

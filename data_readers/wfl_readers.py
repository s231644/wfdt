from abc import ABC
from ast import literal_eval
from typing import Dict, Tuple, List
from xml.etree import ElementTree as ET

from src import (
    LexItem, WFToken,
    RuleInfo,
    Inventory
)
from data_readers.abstract_readers import AnalysesReaderAbstract


class WordFormationLatinReaderAbstract(AnalysesReaderAbstract, ABC):
    """
    A common class for WFL readers.
    """
    POS2UPOS = {
        "V": "VERB",
        "A": "ADJ",
        "N": "NOUN",
        "PR": "PRON",
        "I": "X"
    }

    PROCESS2INFO = {
        "Derivation_Prefix": "PFX",
        "Derivation_Suffix": "SFX",
        "Derivation_Conversion": "CONV",
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
            rule_parts = v.rule_id.split(":")
            if len(rule_parts) == 3:
                rule_id, process, category = rule_parts
                if process == "Derivation_Conversion":
                    rule = RuleInfo(
                        short_id="_",
                        info=self.PROCESS2INFO[process],
                        pos_b=v.d_from.upos,
                        pos_a=k.upos
                    )
                    rules_by_ids[v.rule_id] = rule
                else:
                    # TODO: compounding rules;
                    #  without them the default method is used
                    pass
            elif len(rule_parts) == 4:
                rule_id, process, category, affix = rule_parts
                rule = RuleInfo(
                    short_id=affix,
                    info=self.PROCESS2INFO[process],
                    pos_b=v.d_from.upos,
                    pos_a=k.upos
                )
                rules_by_ids[v.rule_id] = rule
            else:
                raise ValueError

        inventory = Inventory(
            word_analyses=derivations_analyses,
            rules_by_ids=rules_by_ids,
            bracketing_strategy=bracketing_strategy
        )
        return inventory


class WordFormationLatinSQLReader(WordFormationLatinReaderAbstract):
    """
    Reader for WFL / LEMLAT3 from SQL format.

    INSERT INTO `lemmario` VALUES (13151,'dulciorelocus','N2','m','NcB','d1454','dulciorelocus','NOUN',NULL,'B'),(13152,'dulciorelocus','N2/1','*','Af-','d1453','dulciorelocus','ADJ',NULL,'B');
    INSERT INTO `lemmas_wfr` VALUES ('102',13151,13152,1,'A-To-N','Derivation_Conversion',NULL);

    https://github.com/CIRCSE/LEMLAT3
    """

    LEMMAS_PREFIX = "INSERT INTO `lemmario` VALUES"
    WFR_PREFIX = "INSERT INTO `lemmas_wfr` VALUES"

    def read_dataset(self, path: str) -> Dict[LexItem, WFToken]:
        # First read all lemmas and relations.
        lemmas = []
        wfrs = []
        with open(path, "r") as f:
            lines = f.readlines()
        for line in lines:
            for prefix, data in [
                (self.LEMMAS_PREFIX, lemmas),
                (self.WFR_PREFIX, wfrs)
            ]:
                if line.startswith(prefix):
                    line = line[len(prefix):]
                    line = "".join(line.split()).replace("NULL", "None")
                    if line.endswith(";"):
                        line = line[:-1]
                    new_data = literal_eval(f"[{line}]")
                    data.extend(new_data)

        # Make lemmas.
        lemmas_by_ids = {}
        for lemma_record in lemmas:
            (
                id_lemma, lemma, codlem, gen, codmorf,
                n_id, lemma_reduced, upostag, upostag_2, src
            ) = lemma_record
            lemmas_by_ids[id_lemma] = LexItem(
                lang=self.lang,
                lemma=lemma,
                form=lemma,
                upos=upostag,
                lid=id_lemma  # to distinguish conversion within the same POS
            )

        # Make analyses. As for compounding there are multiple relations,
        # we need to collect them all first.
        results = {}
        compound_parents: Dict[LexItem, Dict[int, LexItem]] = {}
        compound_rules: Dict[LexItem, str] = {}

        for wfr in wfrs:
            (
                wfr_key, o_id_lemma, i_id_lemma,
                i_ord, category, wf_type, affix
            ) = wfr

            word = lemmas_by_ids[o_id_lemma]
            parent = lemmas_by_ids[i_id_lemma]

            if wf_type in ["Derivation_Prefix", "Derivation_Suffix"]:
                rule_id = f"{wfr_key}:{wf_type}:{category}:{affix}"
            else:
                rule_id = f"{wfr_key}:{wf_type}:{category}"

            if wf_type == "Compounding":
                compound_rules[word] = rule_id
                if word not in compound_parents:
                    compound_parents[word] = {}
                compound_parents[word][i_ord] = parent
                continue

            # store analysis for a derived word
            analysis = WFToken(
                d_from=parent,
                rule_id=rule_id
            )
            results[word] = analysis

        # resolve compounding order
        for word in compound_parents:
            parents_dict = compound_parents[word]
            parents = []
            for k in sorted(parents_dict.keys()):
                parents.append(parents_dict[k])

            analysis = WFToken(
                d_from=parents[-1],
                rule_id=compound_rules[word],
                d_modifiers=parents[:-1]
            )
            results[word] = analysis

        return results

    def read_sample(
            self, wfr: tuple, lemmas_by_ids: Dict[int, LexItem]
    ) -> List[Tuple[LexItem, WFToken]]:
        raise NotImplementedError


class WordFormationLatinXMLReader(WordFormationLatinReaderAbstract):
    """
    Reader for WFL (2017 version).

    https://github.com/CIRCSE/WFL
    """
    def read_dataset(self, path: str) -> Dict[LexItem, WFToken]:
        xml = ET.parse(path)
        results = {}
        for record in xml.getroot():
            analyses = self.read_sample(record)
            for word, analysis in analyses:
                results[word] = analysis
        return results

    def read_sample(self, record: ET) -> List[Tuple[LexItem, WFToken]]:
        analyses = []

        for c in record:
            if c.tag != "Analysis":
                continue
            for cc in c:
                if cc.tag != "Lemmas":
                    continue
                for xml_lemma in cc:
                    lemma = xml_lemma.attrib["lemma"]
                    try:
                        is_derived = xml_lemma.attrib["is_derived"] == "true"
                    except KeyError:
                        # TODO: why???
                        continue

                    if not is_derived:
                        continue

                    for rule in xml_lemma:
                        rule_id = rule.attrib["id"]
                        rule_category = rule.attrib["category"]
                        rule_type = rule.attrib["type"]
                        if rule_type == "Compounding":
                            source_lemmas = []
                            for sl in rule:
                                source_lemma = sl.attrib["lemma"]
                                source_lemmas.append(source_lemma)

                            xpos_l, xpos_r, xpos_d = rule_category.replace("=", "+").split("+")
                            # TODO: dependency arc direction
                            lemma_l, lemma_r = source_lemmas
                            word = LexItem(
                                lang=self.lang,
                                lemma=lemma,
                                form=lemma,
                                upos=self.POS2UPOS[xpos_d],
                                xpos=xpos_d,
                            )
                            subword_l = LexItem(
                                lang=self.lang,
                                lemma=lemma_l,
                                form=lemma_l,
                                upos=self.POS2UPOS[xpos_l],
                                xpos=xpos_l,
                            )
                            subword_r = LexItem(
                                lang=self.lang,
                                lemma=lemma_r,
                                form=lemma_r,
                                upos=self.POS2UPOS[xpos_r],
                                xpos=xpos_r,
                            )
                            analysis = WFToken(
                                d_from=subword_r,
                                d_modifiers=[subword_l],
                                rule_id=f"{rule_id}:{rule_type}:{rule_category}"
                            )
                            analyses.append((word, analysis))
                            continue

                        xpos_s, _, xpos_d = rule_category.split("-")

                        word = LexItem(
                            lang=self.lang,
                            lemma=lemma,
                            form=lemma,
                            upos=self.POS2UPOS[xpos_d],
                            xpos=xpos_d,
                        )
                        if rule_type == "Derivation_Conversion":
                            for sl in rule:
                                source_lemma = sl.attrib["lemma"]
                                analysis = WFToken(
                                    d_from=LexItem(
                                        lang=self.lang,
                                        lemma=source_lemma,
                                        form=source_lemma,
                                        upos=self.POS2UPOS[xpos_s],
                                        xpos=xpos_s
                                    ),
                                    rule_id=f"{rule_id}:{rule_type}:{rule_category}"
                                )
                                analyses.append((word, analysis))
                            continue

                        rule_affix = rule.attrib["affix"]

                        for sl in rule:
                            source_lemma = sl.attrib["lemma"]
                            analysis = WFToken(
                                d_from=LexItem(
                                    lang=self.lang,
                                    lemma=source_lemma,
                                    form=source_lemma,
                                    upos=self.POS2UPOS[xpos_s],
                                    xpos=xpos_s
                                ),
                                rule_id=f"{rule_id}:{rule_type}:{rule_category}:{rule_affix}"
                            )
                            analyses.append((word, analysis))

        return analyses


# inventory = WordFormationLatinXMLReader(lang="lat").build_inventory(
#     "../data/lat/word-formation-latin/formario_ITTB_17-10-2017_tagged_fixed.xml"
# )
#
# query = LexItem(
#     lang="lat",
#     lemma="conamicus",
#     form="conamicus",
#     upos="NOUN",
#     xpos="N"
# )
#
# inventory.make_subword_tree(
#     query
# ).html(f"examples/{query.lang}_{query.lemma}_{query.upos}.html")


# inventory = WordFormationLatinSQLReader(lang="lat").build_inventory(
#     "../data/lat/word-formation-latin/lemlat_db.sql"
# )


# query = LexItem(
#     lang="lat",
#     lemma="dulciorelocus",
#     form="dulciorelocus",
#     upos="NOUN",
#     lid=13151
# )

# query = LexItem(
#     lang="lat",
#     lemma="obdulcesco",
#     form="obdulcesco",
#     upos="VERB",
#     lid=26637
# )
#
#
# inventory.make_subword_tree(
#     query
# ).html(f"examples/{query.lang}_{query.lemma}_{query.upos}.html")

import re
from typing import Dict, List, Tuple
from xml.etree import ElementTree as ET

from src import (
    LexItem,
    CONLLUToken, CONLLUTree,
    Inventory
)
from data_readers.abstract_readers import ReaderAbstract


class ElixirFMReader(ReaderAbstract):
    """
    Reader for ElixirFM.

    TODO: example

    https://github.com/otakar-smrz/elixir-fm
    """

    XMLNS = "{http://ufal.mff.cuni.cz/pdt/pml/}"

    POS_TO_UPOS = {
        "Verb": "VERB",
        "Adj": "ADJ",
        "Noun": "NOUN",
        "Xtra": "X",
    }

    def build_inventory(self, path: str) -> Inventory:
        word_trees = self.read_dataset(path)
        inventory = Inventory(
            word_trees=word_trees
        )
        return inventory

    def read_dataset(self, path: str) -> Dict[LexItem, CONLLUTree]:
        xml = ET.parse(path)
        results = {}

        for block in xml.getroot():
            if block.tag.replace(self.XMLNS, "") != "data":
                continue
            for record in block:
                analyses = self.read_sample(record)
                for word, analysis in analyses:
                    results[word] = analysis
        return results

    def read_sample(self, record: ET) -> List[Tuple[LexItem, CONLLUTree]]:
        analyses = []
        for nest in record:
            analyses_nest = self.read_nest(nest)
            analyses.extend(analyses_nest)
        return analyses

    def read_nest(self, nest: ET) -> List[Tuple[LexItem, CONLLUTree]]:
        root = None
        entries = None
        for c in nest:
            if c.tag.replace(self.XMLNS, "") == "root":
                root = c
            if c.tag.replace(self.XMLNS, "") == "ents":
                entries = c
        if root is None or entries is None:
            return []

        analyses = []

        root_enc, root_orth, root_bw = root.text.split("\t")
        root_token = CONLLUToken(
            idx="1",
            form=root_orth,
            lemma=root_orth,
        )
        root_tree = CONLLUTree([root_token])

        for entry in entries:
            analyses_entry = self.read_entry(entry, root_tree)
            analyses.extend(analyses_entry)

        return analyses

    def read_entry(self, entry: ET, root_tree: CONLLUTree):
        analyses = []
        morphs, entity = None, None
        for c in entry:
            if c.tag.replace(self.XMLNS, "") == "morphs":
                morphs = c
            if c.tag.replace(self.XMLNS, "") == "entity":
                entity = c
        (
            morphs_pattern, morphs_enc, morphs_orth, morphs_bw
        ) = morphs.text.split("\t")

        word_tree = self.attach_morphs(root_tree, morphs_pattern)

        for info in entity:
            xpos_d = info.tag.replace(self.XMLNS, "")
            upos_d = self.POS_TO_UPOS.get(xpos_d, "X")
            word = LexItem(
                lang=self.lang,
                form=morphs_orth,
                lemma=morphs_orth,
                upos=upos_d,
                xpos=xpos_d
            )
            analyses.append((word, word_tree))
            for expanded in info:
                form_morphs = expanded.text.split("\t")
                if len(form_morphs) != 4:
                    continue
                (
                    fmorphs_pattern, fmorphs_enc, fmorphs_orth, fmorphs_bw
                ) = form_morphs

                form_tree = self.attach_morphs(root_tree, fmorphs_pattern)

                form = LexItem(
                    lang=self.lang,
                    form=fmorphs_orth,
                    lemma=fmorphs_orth,
                    upos=upos_d,
                    xpos=xpos_d
                )
                analyses.append((form, form_tree))
        return analyses

    @staticmethod
    def attach_morphs(
            root_tree: CONLLUTree,
            morphs_pattern: str,
    ) -> CONLLUTree:
        # TODO: distinguish inflectional and derivational morphemes

        # SUFFIXES

        # "al >| _____ |< Iy |< aT"
        stem_and_suffixes = re.split(r" \|< ", morphs_pattern)
        # ["al >| _____", "Iy", "aT"]
        stem = stem_and_suffixes[0]
        suffixes = stem_and_suffixes[1:]

        # PREIFXES

        # "al >| _____"
        prefixes_and_stem = re.split(r" >\| ", stem)
        # ["al", "_____"]
        stem = prefixes_and_stem[-1]
        prefixes = prefixes_and_stem[:-1]

        # RIGHT COMPOUND MODIFIERS

        # FaCL |<< "a" |<< "_hAn"
        stem_and_rdeps = re.split(r" \|<< ", stem)
        stem = stem_and_rdeps[0]
        rdeps = stem_and_rdeps[1:]

        # LEFT COMPOUND MODIFIERS

        # "yA" >>| FaCIL
        stem_and_ldeps = re.split(r" >>\| ", stem)
        stem = stem_and_ldeps[-1]
        ldeps = stem_and_ldeps[:-1]

        # order of attachment: root -> transfix -> modifiers -> affixes

        if stem == "_____":  # stem without changes
            word_tree = root_tree
        else:
            # e.g. "FuCAL"
            transfix_token = CONLLUToken(
                idx="1",
                form=stem,
                lemma=stem,
            )
            transfix_tree = CONLLUTree([transfix_token])
            word_tree = Inventory.merge_trees(
                root_tree, transfix_tree, deprel="affix", is_arc_l2r=True
            )

        for dep in reversed(ldeps):
            dep_token = CONLLUToken(
                idx="1",
                form=dep,
                lemma=dep,
            )
            dep_tree = CONLLUTree([dep_token])
            word_tree = Inventory.merge_trees(
                dep_tree, word_tree, deprel="compound", is_arc_l2r=False
            )

        for dep in rdeps:
            dep_token = CONLLUToken(
                idx="1",
                form=dep,
                lemma=dep,
            )
            dep_tree = CONLLUTree([dep_token])
            word_tree = Inventory.merge_trees(
                word_tree, dep_tree, deprel="compound", is_arc_l2r=True
            )

        for affix in reversed(prefixes):
            affix_token = CONLLUToken(
                idx="1",
                form=affix,
                lemma=affix,
            )
            affix_tree = CONLLUTree([affix_token])
            word_tree = Inventory.merge_trees(
                affix_tree, word_tree, deprel="affix", is_arc_l2r=False
            )

        for affix in suffixes:
            affix_token = CONLLUToken(
                idx="1",
                form=affix,
                lemma=affix,
            )
            affix_tree = CONLLUTree([affix_token])
            word_tree = Inventory.merge_trees(
                word_tree, affix_tree, deprel="affix", is_arc_l2r=True
            )
        return word_tree


# Arabic example

# inventory = ElixirFMReader(lang="arb").build_inventory(
#     "../data/arb/elixirfm/sample.xml"
# )
#
# query = LexItem(
#     lang='arb',
#     lemma='بَصَرِيّ',
#     form='بَصَرِيّ',
#     upos='ADJ',
#     xpos='Adj',
# )
#
# inventory.make_subword_tree(
#     query
# ).html(f"examples/{query.lang}_{query.lemma}_{query.upos}.html")

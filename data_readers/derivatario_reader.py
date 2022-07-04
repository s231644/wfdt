from typing import Dict, List, Tuple

from src import (
    LexItem,
    CONLLUToken, CONLLUTree,
    Inventory
)
from data_readers.abstract_readers import ReaderAbstract


class DerivaTarioReader(ReaderAbstract):
    """
    Reader for DerIvaTario.

    7883;ANTI-TOTALITARISTA;TOTALE:root;ITÀ:ità:mt1:ms2b;ARIO:ario:mt1:ms2a;ISMO:ismo:mt1:ms1;ANTI:anti:mt1:ms1;ISTA:ista:mt6:ms1;

    https://derivatario.sns.it
    """
    prefixes = {
        "acons", "anti", "auto", "bi", "tri", "de", "1de", "2de", "dis", "in",
        "micro", "mini", "ri", "1s", "2s", "co", "neo", "1in", "2in", "a",
        "con", "per", "pre", "inter", "intra", "iper", "mega", "mono", "maxi",
        "multi","pan", "cis", "para", "pro", "tras", "es", "ex", "e", "proto",
        "stra", "trans", "fra"
    }

    def build_inventory(self, path: str) -> Inventory:
        word_trees = self.read_dataset(path)
        inventory = Inventory(
            word_trees=word_trees
        )
        return inventory

    def read_dataset(self, path: str) -> Dict[LexItem, CONLLUTree]:
        with open(path, "r") as f:
            lines = f.readlines()

        results = {}

        for line in lines:
            for word, analysis in self.read_sample(line):
                results[word] = analysis

        return results

    def read_sample(
            self, line: str
    ) -> List[Tuple[LexItem, CONLLUTree]]:
        lemma_id, lemma, base, *affixes = line.lower().strip("\n;").split(";")

        word = LexItem(
            lang=self.lang,
            # lid=lemma_id,
            form=lemma,
            lemma=lemma,
            # upos="_",  # TODO: get UPOS?
            # xpos="_"  # TODO: ???
        )

        base_lemma = base.split(":")[0]

        root_token = CONLLUToken(
            idx="1",
            form=base_lemma,
            lemma=base_lemma,
        )

        word_tree = CONLLUTree([root_token])

        for affix in affixes:
            morpheme, allomorph = affix.split(":")[:2]
            if allomorph.endswith("-p") or allomorph.endswith("-g"):
                allomorph = allomorph[:-2]
            affix_token = CONLLUToken(
                idx="1",
                form=allomorph,
                lemma=morpheme,
            )
            affix_tree = CONLLUTree([affix_token])
            if morpheme in self.prefixes:
                word_tree = Inventory._merge_trees(
                    affix_tree, word_tree, deprel="affix", is_arc_l2r=False
                )
            else:
                # suffix, conversion, backformation, shortening
                word_tree = Inventory._merge_trees(
                    word_tree, affix_tree, deprel="affix", is_arc_l2r=True
                )

        return [(word, word_tree)]


# Italian example

# inventory = DerivaTarioReader(lang="ita").build_inventory(
#     "../data/ita/derivatario/derivatario.csv"
# )

# rivitalizzare
# rivoluzionarismo
# query = LexItem(
#     lang="ita",
#     lemma="anti-totalitarista",
#     form="anti-totalitarista",
# )
#
#
# inventory.make_subword_tree(
#     query
# ).html(f"examples/{query.lang}_{query.lemma}_{query.upos}.html")

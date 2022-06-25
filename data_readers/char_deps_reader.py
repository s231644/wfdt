from typing import Dict, List, Tuple

from src import (
    LexItem,
    CONLLUToken, CONLLUTree,
    Inventory
)
from data_readers.abstract_readers import ReaderAbstract


class CharDepsReader(ReaderAbstract):
    POS2UPOS = {
        # absolute POS tags
        "p": "PRON",
        "n": "NOUN",
        "v": "VERB",
        "a": "ADJ",
        "d": "ADV",

        # character‐level POS tag set: all above +
        # Number, foreign letter transliteration and other non‐Chinese characters
        # TODO: i,f -> UPOS conversion
        "i": "NUM",
        # Functional character 的(of) 们(‐es) 在(at) …
        "f": "AFFIX",
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

        cur_lines = []
        cur_id = "0"
        for line in lines:
            line = line.strip()
            if not line:
                for word, analysis in self.read_sample(cur_lines, cur_id):
                   results[word] = analysis
                cur_lines = []
                continue
            if line.startswith("["):
                e = line.find("]")
                cur_id = line[1:e].strip()
                continue
            cur_lines.append(line)
        else:
            if cur_lines:
                for word, analysis in self.read_sample(cur_lines, cur_id):
                   results[word] = analysis

        return results

    def read_sample(
            self, cur_lines: List[str], cur_id: str
    ) -> List[Tuple[LexItem, CONLLUTree]]:
        tokens = []
        word_xpos = "X"
        for line in cur_lines:
            idx, char, pos, head_idx, deprel = line.split()
            if head_idx == "0":
                word_xpos = deprel.split("-")[-1]  # "root-n" -> "n"
            token = CONLLUToken(
                idx=idx,
                form=char,
                lemma=char,
                upos=self.POS2UPOS[pos],
                xpos=pos,
                head=head_idx,
                deprel=deprel,
            )
            tokens.append(token)
        word_tree = CONLLUTree(tokens)

        lemma = "".join([t.form for t in tokens])
        word = LexItem(
            lid=cur_id,
            form=lemma,
            lemma=lemma,
            upos=self.POS2UPOS[word_xpos],
            xpos=word_xpos
        )
        return [(word, word_tree)]


# Chinese example

# inventory = CharDepsReader().build_inventory(
#     "../data/zho/chinesechardeps/sample.txt"
# )
#
# query = LexItem(
#     lid="47332",
#     lemma="聆听已久",
#     form="聆听已久",
#     upos="ADJ",
#     xpos="a"
# )
#
# inventory.make_subword_tree(
#     query
# ).html(f"{query.lemma}_{query.upos}.html")

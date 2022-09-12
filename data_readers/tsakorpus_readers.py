import os
from collections import Counter
from typing import Dict, Tuple, List
from xml.etree import ElementTree as ET

from src import (
    LexItem,
    CONLLUToken, CONLLUTree,
    Inventory
)
from data_readers.abstract_readers import ReaderAbstract


class EvenkiTsakorpusReader(ReaderAbstract):
    POS2UPOS = {
        "v": "VERB",
        "n": "NOUN",
        "adv": "ADV",
        "adj": "ADJ",
    }

    def build_inventory(self, path: str) -> Inventory:
        if os.path.isfile(path):
            word_trees = self.read_dataset(path)
        elif os.path.isdir(path):
            word_trees = {}
            for fname in os.listdir(path):
                fpath = os.path.join(path, fname)
                if not fpath.endswith(".eaf"):
                    continue
                word_trees_fpath = self.read_dataset(fpath)
                word_trees.update(word_trees_fpath)
        else:
            raise ValueError
        inventory = Inventory(
            word_trees=word_trees
        )
        return inventory

    def read_dataset(self, path: str) -> Dict[LexItem, CONLLUTree]:
        xml = ET.parse(path)
        results = {}

        by_morph = {
            "gl": {},
            "morph_msa": {},
            "morph_type": {}
        }  # ANNOTATION_REF: value
        morphs_by_word = {}
        annid_to_word = {}
        pos_by_word = {}

        sentences = []
        cur_sentence = []

        for elem in xml.getroot():
            if elem.tag != "TIER":
                continue
            tier_id = elem.attrib["TIER_ID"]
            if tier_id in by_morph:
                for token in elem:
                    for ann in token:
                        ref = ann.attrib["ANNOTATION_REF"]
                        for refann in ann:
                            by_morph[tier_id][ref] = refann.text
            elif tier_id == "fon":
                for token in elem:
                    for ann in token:
                        ref = ann.attrib["ANNOTATION_REF"]
                        annid = ann.attrib["ANNOTATION_ID"]
                        if ref not in morphs_by_word:
                            morphs_by_word[ref] = []
                        for refann in ann:
                            morphs_by_word[ref].append((annid, refann.text))
            elif tier_id == "word_pos":
                for token in elem:
                    for ann in token:
                        ref = ann.attrib["ANNOTATION_REF"]
                        for refann in ann:
                            pos_by_word[ref] = refann.text
            elif tier_id == "fonWord":
                for token in elem:
                    for ann in token:
                        annid = ann.attrib["ANNOTATION_ID"]
                        prev_ann = ann.attrib.get("PREVIOUS_ANNOTATION")
                        for refann in ann:
                            annid_to_word[annid] = refann.text
                            if prev_ann:
                                cur_sentence.append(annid)
                            else:
                                if cur_sentence:
                                    sentences.append(cur_sentence)
                                    cur_sentence = []
                else:
                    if cur_sentence:
                        sentences.append(cur_sentence)
                        cur_sentence = []

        for sentence in sentences:
            # ['a25', 'a26', 'a27', 'a28', 'a29', 'a30', 'a31']
            for token_id in sentence:
                for word, analysis in self.read_sample(
                    token_id=token_id,
                    by_morph=by_morph,
                    morphs_by_word=morphs_by_word,
                    annid_to_word=annid_to_word,
                    pos_by_word=pos_by_word
                ):
                    results[word] = analysis

        return results

    def read_sample(
            self,
            token_id: str,
            by_morph,
            morphs_by_word,
            annid_to_word,
            pos_by_word
    ) -> List[Tuple[LexItem, CONLLUTree]]:
        # 'a30'
        token = annid_to_word[token_id]  # 'bičān'

        xpos_d = pos_by_word.get(token_id, "X")  # 'v'

        subword_tokens = []
        content_ids = set()
        pos_tags = {}  # TODO: subword POS tags
        try:
            morphs = morphs_by_word[token_id]
            # [('a113': 'bi'), ('a114': '-čā'), ('a115': '-n')]
        except KeyError as e:
            print(e)
            return []

        # copied from Popoluca reader
        for i, (morph_id, morpheme) in enumerate(morphs):
            morph_type = by_morph["morph_type"].get(morph_id, "x")
            if morph_type in ["stem", "root"]:
                content_ids.add(i)

        for i, (morph_id, morpheme) in enumerate(morphs):
            if not content_ids:
                if i == 0:
                    head = "0"
                    deprel = "x"
                else:
                    head = "1"
                    deprel = "infl"
            elif i == max(content_ids):
                head = "0"
                deprel = "x"
            else:
                head = str(max(content_ids) + 1)
                if i in content_ids:
                    deprel = "compound"
                else:
                    deprel = "infl"

            morpheme_token = CONLLUToken(
                idx=str(i + 1),
                form=morpheme.replace('-', '').replace('=', ''),  # TODO: what is the form in this case?
                lemma=morpheme,
                upos="X",
                xpos=pos_tags.get(i, "X"),
                head=head,
                deprel=deprel,
            )
            subword_tokens.append(morpheme_token)
        word_tree = CONLLUTree(subword_tokens)
        word = LexItem(
            lang=self.lang,
            lemma=token,
            form=token,
            upos="X",  # TODO: convert
            xpos=xpos_d,
        )
        return [(word, word_tree)]

from html.parser import HTMLParser
from typing import Dict, List, Tuple

from src import (
    LexItem,
    CONLLUToken, CONLLUTree,
    Inventory
)
from data_readers.abstract_readers import ReaderAbstract


class CroDeriVHTMLParser(HTMLParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.analyses: List[Tuple[str, List[Dict[str, str]]]] = []

        self.state = "SKIP"
        self.skip_after = False

        self.current_lemma = None
        self.current_morphs: List[Dict[str, str]] = []

    def handle_starttag(self, tag, attrs):
        if tag == "td" and ("class", "text-left col-md-3 forma") in attrs:
            self.state = "LEMMA"
            self.skip_after = True
            return

        if tag == "td" and ("class", "text-center col-md-5") in attrs:
            self.state = "MORPH"
            self.skip_after = True
            return

        if self.state == "LEMMA":
            self.skip_after = False

        if self.state == "MORPH":
            self.skip_after = False

            for k, v in attrs:
                if k != "class":
                    continue
                morph_info = {"class": v, "form": None}
                self.current_morphs.append(morph_info)

    def handle_endtag(self, tag):
        if tag == "td" and self.state == "LEMMA":
            self.state = "SKIP"
            return

        if tag == "td" and self.state == "MORPH":
            self.state = "SKIP"
            return

        if tag == "tr":
            self.analyses.append((self.current_lemma, self.current_morphs))
            self.current_lemma = None
            self.current_morphs = []

    def handle_data(self, data):
        data = data.strip()

        if self.skip_after:
            return

        if self.state == "LEMMA":
            if self.current_lemma is not None:
                return
            self.current_lemma = data
            return

        if self.state == "MORPH":
            if self.current_morphs[-1]["form"] is not None:
                return
            self.current_morphs[-1]["form"] = data
            # merging 'nu' into a single suffix (for cross-lingual consistence)
            if len(self.current_morphs) < 2:
                return
            if self.current_morphs[-1] != {"form": "u", "class": "Suffix"}:
                return
            if self.current_morphs[-2] != {"form": "n", "class": "Suffix"}:
                return
            self.current_morphs.pop()
            self.current_morphs[-1] = {"form": "nu", "class": "Suffix"}
            return


class CroDeriVReader(ReaderAbstract):
    """
    Reader for CroDeriV.

    The overall morphological structure of verbs in CroDeriV is:
        (P4) (P3) (P2) (P1) (L2) (I) L1 (S3) S2 S1 END

    P = prefix
    L = lexical morpheme (Stem)
    I = interfix
    S = suffix
    END = infinitive ending
    () = optional element

    <table class="table">
        <tr class="">
            <td class="text-left col-md-3 forma">
                <a href="/Entry/Details/2">dvoumiti se</a>
            </td>
            <td class="text-center col-md-5">
                <a class="Stem" href="#">&nbsp;dv&nbsp;</a>
                <span class="Interfix">&nbsp;o&nbsp;</span>
                <a class="Stem" href="#">&nbsp;um&nbsp;</a>
                <span class="Suffix">&nbsp;i&nbsp;</span>
                <span class="Ending">&nbsp;ti&nbsp;</span>
            </td>
        </tr>
    </table>

    http://croderiv.ffzg.hr/
    """

    def build_inventory(self, path: str) -> Inventory:
        word_trees = self.read_dataset(path)
        inventory = Inventory(
            word_trees=word_trees,
        )
        return inventory

    def read_dataset(self, path: str) -> Dict[LexItem, CONLLUTree]:
        parser = CroDeriVHTMLParser()
        doc = open(path).read()
        parser.feed(doc)

        results = {}

        for lemma, segmentation in parser.analyses:
            try:
                for word, analysis in self.read_sample(lemma, segmentation):
                    results[word] = analysis
            except Exception as e:
                print(e)
        return results

    def read_sample(
            self, lemma: str, segmentation: List[Dict[str, str]]
    ) -> List[Tuple[LexItem, CONLLUTree]]:
        word = LexItem(
            lang=self.lang,
            form=lemma,
            lemma=lemma,
            upos="VERB"
        )

        tokens_by_class = {
            "Prefix": [],
            "Interfix": [],
            "Suffix": [],
            "Ending": [],
            "Stem": []
        }

        # finding the last stem == the root
        for i, morpheme in enumerate(segmentation):
            mform = morpheme["form"]
            mclass = morpheme["class"]
            morpheme_token = CONLLUToken(
                idx="1",
                form=mform,
                lemma=mform,
            )
            tokens_by_class[mclass].append(morpheme_token)

        stems = tokens_by_class["Stem"]
        assert stems, \
            f"Incorrect verb {lemma} without a stem! {segmentation}"

        word_tree = CONLLUTree([stems[-1]])

        # first merge the stems
        if len(stems) > 1:
            assert len(stems) == 2, ValueError(
                f"Verb {lemma} has {len(stems)} > 2 stems!"
            )
            secondary_tree = CONLLUTree([stems[0]])
            interfixes = tokens_by_class["Interfix"]
            if interfixes:
                assert len(interfixes) == 1, ValueError(
                    f"Verb {lemma} has {len(interfixes)} > 1 interfixes!"
                )
                affix_tree = CONLLUTree(interfixes)
                secondary_tree = Inventory.merge_trees(
                    secondary_tree, affix_tree, deprel="infl", is_arc_l2r=True
                )
            word_tree = Inventory.merge_trees(
                secondary_tree, word_tree, deprel="compound", is_arc_l2r=False
            )

        for prefix_token in reversed(tokens_by_class["Prefix"]):
            affix_tree = CONLLUTree([prefix_token])
            word_tree = Inventory.merge_trees(
                affix_tree, word_tree, deprel="affix", is_arc_l2r=False
            )

        for suffix_token in tokens_by_class["Suffix"]:
            affix_tree = CONLLUTree([suffix_token])
            word_tree = Inventory.merge_trees(
                word_tree, affix_tree, deprel="affix", is_arc_l2r=True
            )

        for suffix_token in tokens_by_class["Ending"]:
            affix_tree = CONLLUTree([suffix_token])
            word_tree = Inventory.merge_trees(
                word_tree, affix_tree, deprel="infl", is_arc_l2r=True
            )

        if lemma.endswith(" se") and word_tree.tokens[-1] != "se":
            # reflexive
            clitic_token = CONLLUToken(
                idx="1",
                form="se",
                lemma="se",
            )
            clitic_tree = CONLLUTree([clitic_token])
            word_tree = Inventory.merge_trees(
                word_tree, clitic_tree, deprel="expl:pv", is_arc_l2r=True
            )

        return [(word, word_tree)]


# Croatian example

# inventory = CroDeriVReader(lang="hrv").build_inventory(
#     "../data/hrv/croderiv/sample.html"
#     # "../data/hrv/croderiv/webpage-data.html"
# )
#
# query = LexItem(
#     lang="hrv",
#     lemma="ukisnuti se",
#     form="ukisnuti se",
#     upos="VERB",
# )
#
# inventory.make_subword_tree(
#     query
# ).html(f"examples/{query.lang}_{query.lemma}_{query.upos}.html")

from typing import Dict, Tuple, List

from src import (
    LexItem, WFToken,
    RuleInfo,
    Inventory
)
from data_readers.abstract_readers import AnalysesReaderAbstract


class AuCoProReader(AnalysesReaderAbstract):
    def __init__(self, lang: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.lang = lang
        if lang == "afr":
            self.interfixes = [
                'e', 'er', 'ere', 'ens', 'n', 'ns', 's'
            ]
        elif lang == "nld":
            self.interfixes = [
                'e', 'en', 'ën', 'n', 's'
            ]
        else:
            raise ValueError(f"Incorrect language {lang}!")

        self.interfix_rules = {
            f"INTERFIX({upos})(-{c})": RuleInfo(
                short_id=f"-{c}",
                info="INTERFIX",
                pos_b=upos,
                pos_a=upos
            ) for upos in ["_"] for c in self.interfixes
        }

    def build_inventory(
            self, path: str,
            bracketing_strategy: str = "last"
    ) -> Inventory:

        compound_analyses = self.read_dataset(path)

        inventory = Inventory(
            word_analyses=compound_analyses,
            rules_by_ids=self.interfix_rules,
            bracketing_strategy=bracketing_strategy
        )
        return inventory

    def read_dataset(self, path: str) -> Dict[LexItem, WFToken]:
        with open(path, "r") as f:
            lines = f.readlines()
        results = {}
        for line in lines:
            for word, analysis in self.read_sample(line.strip()):
                results[word] = analysis
        return results

    def read_sample(self, line: str) -> List[Tuple[LexItem, WFToken]]:
        result = []

        derived_lemma = line.replace("_", "").replace("+", "").replace(" ", "")
        # TODO: correct bracketing and POS tags
        d_upos = "NOUN"

        subwords = []
        compound_items = line.split("+")
        for i, compound_elem in enumerate(compound_items):
            morphemes = compound_elem.replace(" ", "").strip().split("_")
            # assuming stem = lemma
            # TODO: correct bracketing, lemmas and POS tags
            form = "".join(morphemes)
            stem = morphemes[0]
            lemma = stem
            upos = d_upos if i == len(compound_items) - 1 else "_"

            subword = LexItem(
                lemma=lemma,
                form=form,
                upos=upos
            )
            subwords.append(subword)

            # lemma and interfix

            if len(morphemes) == 1:
                continue

            # omit hyphened words

            interfix_form = "".join(morphemes[1:]).replace('-', '')
            if interfix_form not in self.interfixes:
                continue

            interfixed_analysis = WFToken(
                d_from=LexItem(
                    lemma=lemma,
                    form=lemma,
                    upos=upos
                ),
                rule_id=f"INTERFIX({upos})(-{interfix_form})"
            )
            form_lex = LexItem(
                lemma=lemma,
                form=form,
                upos=upos
            )
            result.append((form_lex, interfixed_analysis))

        word = LexItem(
            lemma=derived_lemma,
            form=derived_lemma,
            upos=d_upos
        )

        analysis = WFToken(
            d_from=subwords[-1],
            d_modifiers=subwords[:-1]
        )

        result.append((word, analysis))

        return result


# Afrikaans example

# inventory = AuCoProReader(lang="afr").build_inventory(
#     "../data/afr/aucopro/sample.txt",
#     # "../data/afr/aucopro/List.AUCOPRO.AfrikaansSplitting.txt",
#     bracketing_strategy="last"  # "last", "head", "chain"
# )
#
# query = LexItem(
#     lemma='woordeskatitems',
#     form='woordeskatitems',
#     upos='NOUN',
# )
#
# inventory.make_subword_tree(
#     query
# ).html(f"{query.lemma}_{query.upos}.html")


# Dutch example

# inventory = AuCoProReader(lang="nld").build_inventory(
#     "../data/nld/aucopro/sample.txt",
#     # "../data/nld/aucopro/List.AUCOPRO.DutchSplitting.txt",
#     bracketing_strategy="last"  # "last", "head", "chain"
# )
#
# query = LexItem(
#     lemma='temperatuursverandering',
#     form='temperatuursverandering',
#     upos='NOUN',
# )
#
# inventory.make_subword_tree(
#     query
# ).html(f"{query.lemma}_{query.upos}.html")

from typing import Dict, Tuple, List

from src import (
    LexItem, WFToken,
    RuleInfo,
    Inventory
)
from data_readers.abstract_readers import AnalysesReaderAbstract


class GermaNetReader(AnalysesReaderAbstract):
    def __init__(self, n_lines_skip: int = 2):
        super().__init__()
        self.n_lines_skip = n_lines_skip

        self.interfix_rules = {
            f"INTREFIX({pos})(_)": RuleInfo(
                short_id="_",
                info="INTERFIX",
                pos_b=pos,
                pos_a=pos
            )
            for pos in ["NOUN", "ADJ", "VERB", "_"]
        }
        for pos, itfx in [
            ('NOUN', 's'),
            ('NOUN', 'n'),
            ('NOUN', 'en'),
            ('NOUN', 'es'),
            ('NOUN', 'er'),
            ('NOUN', 'e'),
            ('ADJ', 'el'),
            ('NOUN', 'ns'),
            ('VERB', 'en'),
            ('ADJ', 'er'),
            ('NOUN', 'ens'),
            ('NOUN', 'a'),
            ('NOUN', 'nen'),
            ('NOUN', 'ien'),
            # ('VERB', 'v'),
            ('ADJ', 'e'),
            # ('ADJ', 'al'),
            ('ADJ', 'r'),
            ('NOUN', 'o'),
            ('ADJ', 'o'),
            ('NOUN', 'r'),
            ('ADJ', 'ie'),
            ('VERB', 's'),
            # ('VERB', 't'),
            ('ADJ', 'st'),
            ('ADJ', 'en'),
            ('NOUN', 'een'),
            ('ADJ', 's'),
            ('NOUN', 'i'),
            ('VERB', 'e'),
        ]:
            self.interfix_rules[f"INTREFIX({pos})(-{itfx})"] = RuleInfo(
                short_id=f"-{itfx}",
                info="INTERFIX",
                pos_b=pos,
                pos_a=pos
            )

    @staticmethod
    def guess_pos(word: str) -> str:
        if not word:
            return "_"
        if word[0].isupper():
            return "NOUN"
        if any(word.endswith(x) for x in ["en", "eln", "ern"]):
            # from "DErivBase"
            return "VERB"
        if word[0].isalpha():
            return "ADJ"
        return "NOUN"  # TODO: "_"

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
            lines = f.readlines()[self.n_lines_skip:]
        results = {}
        for line in lines:
            try:
                analyses = self.read_sample(line.strip())
            except Exception as e:
                print(
                    f"Could not process compound, "
                    f"as its modifier differs from the written form: {e}!"
                )
                continue
            for word, analysis in analyses:
                results[word] = analysis
        return results

    @staticmethod
    def clean(word: str) -> str:
        cut_word = word.lower()
        for fr, to in [("ä", "a"), ("ö", "o"), ("ü", "u")]:
            cut_word = cut_word.replace(fr, to)
        cut_word = cut_word.rstrip("-")
        return cut_word

    def read_sample(self, line: str) -> List[Tuple[LexItem, WFToken]]:
        result = []

        derived_lemma, modifiers_str, head_lemma = line.split("\t")

        assert derived_lemma.lower().endswith(head_lemma.lower()), \
            (derived_lemma, head_lemma)

        # TODO: correct bracketing and POS tags
        d_upos = self.guess_pos(derived_lemma)

        # use surface form to find correct interfixes
        cut_word = self.clean(derived_lemma[:-len(head_lemma)])

        cur_end = len(cut_word)
        subwords = []

        for m in reversed(modifiers_str.split()):
            lemma = m.split("|")[0]
            pos = self.guess_pos(lemma)

            found_m = False
            form = self.clean(lemma)

            stems = [form]
            if len(form) > 2:
                for i in range(1, min(5, len(form) - 1)):
                    stems.append(form[:-i])
            for stem in stems:
                idx = cut_word.rfind(stem, 0, cur_end)
                if idx != -1:
                    found_m = True
                else:
                    continue
                surface_form = derived_lemma[idx:cur_end]
                subword = LexItem(
                    lemma=lemma,
                    form=surface_form,
                    upos=pos
                )
                subwords.append(subword)

                interfix_str = cut_word[idx + len(stem):cur_end]
                cur_end = idx
                while interfix_str.endswith("-"):
                    interfix_str = interfix_str[:-1]
                if not interfix_str:
                    break

                rule_id = f"INTREFIX({pos})(-{interfix_str})"
                if rule_id not in self.interfix_rules:
                    # unknown interfix
                    rule_id = f"INTREFIX({pos})(_)"
                interfixed_analysis = WFToken(
                    d_from=LexItem(
                        lemma=lemma,
                        form=lemma,
                        upos=pos
                    ),
                    rule_id=rule_id
                )
                form_lex = LexItem(
                    lemma=lemma,
                    form=surface_form,
                    upos=pos
                )
                result.append((form_lex, interfixed_analysis))
                break
            assert found_m, (derived_lemma, cut_word, lemma)

        subwords = subwords[::-1]

        subwords.append(
            LexItem(
                lemma=head_lemma,
                form=head_lemma,
                upos=d_upos
            )
        )

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


# German example

# inventory = GermaNetReader(n_lines_skip=2).build_inventory(
#     "../data/deu/germanet/sample.txt"
#     # "../data/deu/germanet/split_compounds_from_GermaNet17.0.txt"
# )

# query = LexItem(
#     lemma='Olympiamedaillengewinner',
#     form='Olympiamedaillengewinner',
#     upos='NOUN',
# )

# query = LexItem(
#     lemma='Autobahnanschlussstelle',
#     form='Autobahnanschlussstelle',
#     upos='NOUN',
# )

# inventory.make_subword_tree(
#     query
# ).html(f"examples/{query.lemma}_{query.upos}.html")

import re
from typing import Dict, List, Tuple

from src import (
    LexItem,
    CONLLUToken, CONLLUTree,
    Inventory
)
from data_readers.abstract_readers import ReaderAbstract


class PopolucaDeTexistepecReader(ReaderAbstract):
    """
    Popoluca phrases and sentences
    with canonical morpheme segmentation
    supplied with grammar and Spanish translation.
    The examples are taken from the book (see link below).

    Format:
    Sentence id. Popoluca surface text
    Popoluca canonical morpheme segmentation
    /Spanish/element-wise/translation/
    Spanish surface text

    13. ʔi pɨ:ñdya:ʔ du:ru dyyakaʔ čyo:koʔ
    ʔi pɨ:ñ-da:ʔ du:ru y-yakaʔ y-¢o:koʔ
    /y/hombre-aum./duro/A3-matar/A3-corazón/
    Y el señor estaba desesperado.

    16. maʔte hokska:keʔ
    maʔ=te Ø-hoks=kak=eʔ
    /aux.:pfv.=inc./B3-rozar=iter.=dep./
    Otra vez empezó a rozar.

    The book:
    https://arqueologiamexicana.mx/sites/default/files/banco_imagenes/popoluca-de-texistepec.pdf
    """

    # TODO: map to universal features
    ABREVIATURAS = {
        '1': 'primera persona',
        '1,2 pl.': 'plural de la primera (excl.) o segunda persona',
        r'1\2': 'primera persona agente, segunda persona paciente',
        '2': 'segunda persona',
        r'2\1': 'segunda persona agente, primera persona paciente',
        '3': 'tercera persona',
        'A': 'marcador de caso ergativo y posesión',
        'adjr.': 'adjetivizador',
        'adjr. aum.': 'adjetivizador aumentizante',
        'adjr. int.': 'adjetivizador intensificante',
        'and.': 'andativo',
        'antipas.': 'antipasivo',
        'apl.': 'aplicativo',
        'apll.': 'aplicativo doble',
        'aum.': 'aumentativo',
        'aux.': 'verbo auxiliar',
        'B': 'marcador de caso absolutivo',
        'caus.': 'causativo',
        'cn.': 'clasificador numeral',
        'cop.': 'verbo copulativo',
        'cuot.': 'cuotativo',
        'def.': 'definido',
        'deíc.': 'sufijo en ciertas raíces deícticas',
        'denom.': 'denominalizador',
        'dep.': 'dependiente',
        'desid.': 'desiderativo',
        'devrbr.': 'deverbalizador',
        'dif.': 'acción difusa',
        'dim.': 'diminutivo',
        'distr.': 'distributivo',
        'est. pos.': 'estativo de verbo posicional',
        'excl.': 'exclamación',
        'fem.': 'femenino',
        'fos.': 'fosilizado',
        'fut.': 'futuro',
        'fut. inm.': 'futuro inmediato',
        'h': '/h/ ligadura',
        'hab.': 'habitual',
        'hum.': 'humanos',
        'imp.': 'imperativo',
        'inc.': 'incoativo',
        'incl.': 'inclusivo',
        'instr.': 'instrumental',
        'int.': 'intensivo',
        'interr.': 'partícula interrogativa',
        'intro. adj.': 'morfema que introduce adjetivos',
        'ipfv.': 'imperfectivo',
        'it.': 'intensivo-traslativo',
        'iter.': 'iterativo',
        'k': '/k/ epentética',
        'loc.1': 'locativo',
        'loc.2': 'locativo',
        'loc.3': 'locativo',
        'loc.4': 'locativo',
        'loc.5': 'locativo',
        'neg.': 'negación',
        'no hum.': 'no humano',
        'nom.': 'nominalizador',
        'nom. instr.': 'nominalizador instrumental',
        'onomat.': 'onomatopeya',
        'opt.': 'optativo',
        'perm.': 'permisivo',
        'pfv.': 'perfectivo',
        'pl.': 'plural',
        'pas.': 'pasivo',
        'pos.': 'posicional',
        'pro.': 'pronombre',
        'pro. pos.': 'pronombre poseído',
        'psd.': 'pasado-condicional',
        'rec.': 'recíproco',
        'RED': 'reduplicación',
        'rel.': 'relativizador',
        'sub.': 'subordinador',
        'sub. fos.': 'subordinador fosilizado',
        'suf. adj.': 'sufijo de ciertos adjetivos',
        'tras.': 'traslativo',
        'trr.': 'transitivador',
        'vrbr.': 'verbalizador',
        'y': 'ligadura /y/'
    }

    PUNCT = "¿?¡!,…"

    REPLACES = {"é": "ɨ"}

    SPANISH_POS_VOCAB = {
        "hombre": "NOUN",
        "duro": "ADJ",
        "matar": "VERB",
        "corazón": "NOUN",
        "rozar": "VERB",
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
        for line in lines:
            line = line.strip()
            if not line:
                for word, analysis in self.read_sample(cur_lines):
                    results[word] = analysis
                cur_lines = []
                continue
            if line.startswith("#"):
                continue
            cur_lines.append(line)
        else:
            if cur_lines:
                for word, analysis in self.read_sample(cur_lines):
                    results[word] = analysis
        return results

    def read_sample(
            self, cur_lines: List[str]
    ) -> List[Tuple[LexItem, CONLLUTree]]:
        sentence_analyses = []

        (
            surface_text, segmented_text, gram_feats_text, translation_text
        ) = cur_lines

        for rk, rv in self.REPLACES.items():
            surface_text = surface_text.replace(rk, rv)
            segmented_text = segmented_text.replace(rk, rv)

        sent_id, *surface_tokens = surface_text.split()
        # ["maʔte", "hokska:keʔ"]

        segmented_tokens = segmented_text.split()
        # ["maʔ=te", "Ø-hoks=kak=eʔ"]

        gram_feats_tokens = gram_feats_text.strip("\n/").split("/")
        # ["aux.:pfv.=inc.", "B3-rozar=iter.=dep."]

        assert \
            len(surface_tokens) == len(segmented_tokens) == len(gram_feats_tokens), \
            (sent_id, len(surface_tokens), len(segmented_tokens), len(gram_feats_tokens))

        for surface_token, segmented_token, gram_feats_token in zip(
            surface_tokens, segmented_tokens, gram_feats_tokens
        ):

            morphemes = re.split("[-=]", segmented_token)
            # ["Ø", "hoks", "kak", "eʔ"]

            gram_feats = re.split("[-=]", gram_feats_token)
            # ["B3", "rozar", "iter.", "dep."]

            assert \
                len(morphemes) == len(gram_feats), \
                (sent_id, morphemes, gram_feats)

            subword_tokens = []

            content_ids = set()
            pos_tags = {}
            for i, (morpheme, morpheme_feats) in enumerate(
                    zip(morphemes, gram_feats)
            ):
                # TODO: check with self.ABREVIATURAS
                if morpheme_feats[-1] not in "12345D.":
                    content_ids.add(i)
                    if morpheme[-2:] in ["ar", "er", "ir"]:
                        # simple guessing
                        pos_tags[i] = "VERB"
                    else:
                        # search in vocab
                        pos_tags[i] = self.SPANISH_POS_VOCAB.get(morpheme, "X")

            for i, (morpheme, morpheme_feats) in enumerate(
                    zip(morphemes, gram_feats)
            ):
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
                    elif gram_feats == "RED":
                        deprel = "reduplication"
                    else:
                        deprel = "infl"

                morpheme_token = CONLLUToken(
                    idx=str(i + 1),
                    form=morpheme,  # TODO: what is the form in this case?
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
                form=surface_token,
                lemma=segmented_token,
                upos="X",
                xpos="X"
            )
            sentence_analyses.append((word, word_tree))

        return sentence_analyses


# inventory = PopolucaDeTexistepecReader(lang="poq").build_inventory(
#     "../data/poq/popoluca_de_texistepec/sample.txt"
# )

# query = LexItem(
#     lemma='Ø-hoks=kak=eʔ',
#     form='hokska:keʔ',
#     upos='X',
#     xpos='X',
#     lid=None,
#     lang='poq'
# )
#
# inventory.make_subword_tree(
#     query
# ).html(f"examples/{query.lang}_{query.lemma}_{query.upos}.html")

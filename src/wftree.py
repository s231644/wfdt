from src.deptree import CONLLUToken, CONLLUTree
from src.merging import merge_trees
from src.wftoken import WFToken


derivbase = {
    "принять": WFToken("принять", "VERB", "*ять", "при-", False),
    "прием": WFToken("прием", "NOUN", "принять", "-0N", True),
    "приемный": WFToken("приемный", "ADJ", "прием", "N+н(ый)", True),
    "приемная": WFToken("приемная", "NOUN", "приемный", "N", True),
    "обставить": WFToken("обставить", "VERB", "ставить", "об-", False),
    "просто": WFToken("просто", "ADV", "простой", "-о", True),
    "дело": WFToken("дело", "NOUN", "делать", "-0N", True),
    "деловой": WFToken("деловой", "ADJ", "дело", "-ов(ый)", True),
    "по-деловому": WFToken("по-деловому", "ADV", "деловой", "по--ому", True),
}


def make_wf_tree(word: str) -> CONLLUTree:
    if word not in derivbase:
        return CONLLUTree([CONLLUToken("1", word, word)])
    wf_token = derivbase[word]

    affix_tree = CONLLUTree([CONLLUToken("1", wf_token.derived_with, wf_token.derived_with)])
    stem_tree = make_wf_tree(wf_token.derived_from)

    if wf_token.strong:
        return merge_trees(stem_tree, affix_tree, deprel="deriv", is_arc_l2r=False)
    else:
        return merge_trees(stem_tree, affix_tree, deprel="deriv", is_arc_l2r=True)


def make_wfdt(text: str):
    word_tree = CONLLUTree.from_text(text)
    subword_trees = []
    subword_roots = [-1]
    cur_len = 0
    united_subword_tokens = []
    for token in word_tree.tokens:
        subword_tree = make_wf_tree(token.lemma)
        subword_roots.append(cur_len + subword_tree.root_idx)
        subword_trees.append(subword_tree)
        for subword_token in subword_tree.tokens:
            subword_token.idx = str(len(united_subword_tokens) + 1)
            subword_token.head = str(int(subword_token.head) + cur_len)
            united_subword_tokens.append(subword_token)
        cur_len += len(subword_tree)

    for i, token in enumerate(word_tree.tokens):
        united_subword_tokens[subword_roots[i+1]].head = str(subword_roots[int(token.head)]+1)
        united_subword_tokens[subword_roots[i+1]].deprel = token.deprel

    return CONLLUTree(united_subword_tokens)

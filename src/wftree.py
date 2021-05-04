from collections import namedtuple

from src.deptree import CONLLUToken, CONLLUTree
from src.merging import merge_trees

WFToken = namedtuple("WFToken", ["derived_from_lemma", "derived_from_upos", "rule_id"])
WFCompoundToken = namedtuple("WFCompoundToken", ["derived_from_lemma", "derived_from_upos", "derived_from_modifiers", "rule_id"])

RuleInfo = namedtuple("RuleInfo", ["short_id", "info", "pos_b", "pos_a"])
ComplexRuleInfo = namedtuple("ComplexRuleInfo", ["short_id", "info", "pos_b", "pos_a", "simple_rules"])
CompoundRuleInfo = namedtuple("CompoundRuleInfo", ["short_id", "info", "pos_b", "pos_a", "head_rules", "modifier_rules", "after_rules"])


# TODO: create this dict automatically
rules_by_ids = {
    "при-": RuleInfo("при-", "PFX", "VERB", "VERB"),
    "об-": RuleInfo("об-", "PFX", "VERB", "VERB"),
    "-0N": RuleInfo("-0N", "SFX", "VERB", "NOUN"),
    "-н(ый)": RuleInfo("-н(ый)", "SFX", "NOUN", "ADJ"),
    "-ов(ый)": RuleInfo("-ов(ый)", "SFX", "NOUN", "ADJ"),
    "rule977(adj + о -> adv)": RuleInfo("-о", "SFX", "ADJ", "ADV"),
    "-ость": RuleInfo("-ость", "SFX", "ADJ", "NOUN"),
    "N": RuleInfo("N", "CONV", "ADJ", "NOUN"),
    "rule994(по + adj + ому -> adv)": ComplexRuleInfo(
        "по--ому", "PFX,SFX", "ADJ", "ADV", [
            RuleInfo("-ому", "SFX", "ADJ", "ADV"),
            RuleInfo("по-", "PFX", "ADV", "ADV"),
        ]
    ),
    "A+A": CompoundRuleInfo(
        "A+A", "COMPOUND", "ADJ", "ADJ", [], [], []
    ),
    "N+A": CompoundRuleInfo(
        "N+A", "COMPOUND", "ADJ", "ADJ", [], [], []
    ),
    "U+N+н(ый)": CompoundRuleInfo(
        "U+N+н(ый)", "COMPOUND,SFX", "NOUN", "ADJ", [RuleInfo("-н(ый)", "SFX", "NOUN", "ADJ")], [], []
    ),
    "A+N+н(ый)": CompoundRuleInfo(
        "A+N+н(ый)", "COMPOUND,SFX", "NOUN", "ADJ", [RuleInfo("-н(ый)", "SFX", "NOUN", "ADJ")], [], []
    )

}


derivbase = {
    "принять": WFToken("*ять", "VERB", "при-"),
    "прием": WFToken("принять", "VERB", "-0N"),
    "приемный": WFToken("прием", "NOUN", "-н(ый)"),
    "приемная": WFToken("приемный", "ADJ", "N"),
    "обставить": WFToken("ставить", "VERB", "об-"),
    "просто": WFToken("простой", "ADJ", "rule977(adj + о -> adv)"),
    "дело": WFToken("делать", "VERB", "-0N"),
    "деловой": WFToken("дело", "NOUN", "-ов(ый)"),
    "по-деловому": WFToken("деловой", "ADJ", "rule994(по + adj + ому -> adv)"),
    "достоверность": WFToken("достоверный", "ADJ", "-ость"),
    "благородно": WFToken("благородный", "ADJ", "rule977(adj + о -> adv)"),
    "самозабвенно": WFToken("самозабвенный", "ADJ", "rule977(adj + о -> adv)"),
    "еда": WFToken("есть", "VERB", "-0N"),
    "сон": WFToken("спать", "VERB", "-0N"),

    "достоверный": WFCompoundToken("верный", "ADJ", ("достойный",), "A+A"),
    "самозабвенный": WFCompoundToken("забвенный", "ADJ", ("себя",), "N+A"),
    "многочисленный": WFCompoundToken("число", "NOUN", ("много",), "U+N+н(ый)"),
    "белоколонный": WFCompoundToken("колона", "NOUN", ("белый",), "A+N+н(ый)"),
    "благородный": WFCompoundToken("род", "NOUN", ("благой",), "A+N+н(ый)"),

}


def merge_with_simple_rule(stem_tree: CONLLUTree, rule: RuleInfo) -> CONLLUTree:
    affix_tree = CONLLUTree([CONLLUToken("1", rule.short_id, rule.short_id)])
    if rule.info == "SFX":
        if rule.pos_a != rule.pos_b:
            tree = merge_trees(stem_tree, affix_tree, deprel="sfx", is_arc_l2r=False)
        else:
            # TODO: separate modifiers from other suffixes
            tree = merge_trees(stem_tree, affix_tree, deprel="msfx", is_arc_l2r=True)
    elif rule.info == "PTFX":
        tree = merge_trees(stem_tree, affix_tree, deprel="refl", is_arc_l2r=True)
    elif rule.info == "PFX":
        tree = merge_trees(affix_tree, stem_tree, deprel="mpfx", is_arc_l2r=False)
    elif rule.info == "CONV":
        tree = merge_trees(stem_tree, affix_tree, deprel="conv", is_arc_l2r=False)
    else:
        raise AssertionError('Rule info is incorrect!', rule.short_id, rule.info)
    return tree


def merge_with_complex_rule(stem_tree: CONLLUTree, rule: ComplexRuleInfo) -> CONLLUTree:
    tree = stem_tree
    for simple_rule in rule.simple_rules:
        tree = merge_with_simple_rule(tree, simple_rule)
    return tree


def make_wf_tree(word: str) -> CONLLUTree:
    if word not in derivbase:
        return CONLLUTree([CONLLUToken("1", word, word)])
    wf_token = derivbase[word]
    stem_tree = make_wf_tree(wf_token.derived_from_lemma)
    rule = rules_by_ids[wf_token.rule_id]
    if isinstance(rule, RuleInfo):
        return merge_with_simple_rule(stem_tree, rule)
    elif isinstance(rule, ComplexRuleInfo):
        return merge_with_complex_rule(stem_tree, rule)
    elif isinstance(rule, CompoundRuleInfo):
        modifiers_trees = [make_wf_tree(m) for m in wf_token.derived_from_modifiers]
        # TODO: rules for modifiers
        for hrule in rule.head_rules:
            stem_tree = merge_with_simple_rule(stem_tree, hrule)
        for modifier_tree in reversed(modifiers_trees):  # (m1 (m2 (m3 h))) sfx
            stem_tree = merge_trees(modifier_tree, stem_tree, "compound", is_arc_l2r=False)
        for hrule in rule.after_rules:  # prefix?
            stem_tree = merge_with_simple_rule(stem_tree, hrule)
        return stem_tree
    else:
        raise NotImplementedError


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

    renumerated = {"0": 0}
    for i, token in enumerate(word_tree.tokens):
        renumerated[token.idx] = i + 1

    for i, token in enumerate(word_tree.tokens):
        renum_head = renumerated[token.deps.split(":")[0]]
        # if token.idx.isdigit():
        #     renum_head = renumerated[token.head]
        # else:
        #     # 33.1	_	_	_	_	_	_	_	3:conj	_
        #     renum_head = renumerated[token.deps.split(":")[0]]
        united_subword_tokens[subword_roots[i+1]].head = str(subword_roots[renum_head]+1)
        united_subword_tokens[subword_roots[i+1]].deprel = token.deprel

    return CONLLUTree(united_subword_tokens)

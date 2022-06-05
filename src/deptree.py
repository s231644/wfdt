from copy import deepcopy
from dataclasses import dataclass
from typing import Dict, List, Optional, Union

from dep_tregex.ya_dep import visualize_tree


@dataclass
class WFToken:
    d_lemma: str
    d_upos: str
    rule_id: str
    d_modifiers: Optional[List[str]] = None


@dataclass
class RuleInfo:
    short_id: str
    info: str
    pos_b: str
    pos_a: str


@dataclass
class ComplexRuleInfo(RuleInfo):
    simple_rules: List[RuleInfo]


@dataclass
class CompoundRuleInfo(RuleInfo):
    head_rules: Optional[List[RuleInfo]] = None
    modifier_rules: Optional[List[List[RuleInfo]]] = None
    after_rules: Optional[List[RuleInfo]] = None


@dataclass
class CONLLUToken:
    idx: str
    form: str
    lemma: str = "_"
    upos: str = "_"
    xpos: str = "_"
    feats: str = "_"
    head: str = "0"
    deprel: str = "root"
    deps: str = "_"
    misc: str = "_"

    def __post_init__(self):
        self.ihead = int(self.head)
        self.iidx = int(self.idx)

    def set_head(self, head: Union[str, int]):
        if isinstance(head, int):
            self.ihead = head
            self.head = str(head)
        else:
            self.head = head
            self.ihead = int(head)

    def set_idx(self, idx: Union[str, int]):
        if isinstance(idx, int):
            self.iidx = idx
            self.idx = str(idx)
        else:
            self.idx = idx
            self.iidx = int(idx)

    def __str__(self):
        return "\t".join([
            self.idx, self.form, self.lemma, self.upos, self.xpos,
            self.feats, self.head, self.deprel, self.deps, self.misc
        ])

    def __repr__(self):
        return self.__str__()

    @classmethod
    def from_str(cls, line: str):
        return cls(*line.split("\t"))


class CONLLUTree:
    def __init__(
            self,
            tokens: List[CONLLUToken],
            sent_id: str = "",
            sent_text: Optional[str] = None,
            root_idx: Optional[int] = None
    ):
        self.tokens = tokens

        if root_idx is not None:
            self.root_idx = int(root_idx)
        else:
            for i, token in enumerate(tokens):
                if token.ihead == 0:
                    self.root_idx = i

        self.sent_id = sent_id
        self.sent_text = sent_text or ' '.join([token.form for token in tokens])

    def __str__(self):
        return "\n".join(
            [
                f'# sent_id = {self.sent_id}',
                f'# text = {self.sent_text}'
            ] + [str(token) for token in self.tokens]
        )

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def visualize_tree(text):
        return visualize_tree(text)

    def latex(self, fpath: Optional[str] = None):
        tokens = []
        edges = []

        for t in self.tokens:
            tokens.append(t.lemma)
            if t.ihead > 0:
                edges.append(
                    r"\depedge{%s}{%s}{%s}" % (t.head, t.idx, t.deprel)
                )

        lines = [
            r"\begin{dependency}",
            "\t" + r"\begin{deptext}",
            "\t\t" + r" \& ".join(tokens) + r" \\",
            "\t" + r"\end{deptext}",
            *["\t" + e for e in edges],
            r"\end{dependency}",
        ]
        content = "\n".join(lines)
        if fpath:
            with open(fpath, "w") as f:
                f.write(content)
        return content

    def html(self, fpath: Optional[str] = None) -> str:
        content = self.visualize_tree(
            "\n".join([str(token) for token in self.tokens])
        )
        if fpath:
            with open(fpath, "w") as f:
                f.write(content)
        return content

    @classmethod
    def from_text(cls, text: str):
        lines = text.strip().split("\n")
        tokens = [
            CONLLUToken.from_str(line)
            for line in lines
            if (not line.startswith("#") and '-' not in line.split('\t')[0])
        ]
        return cls(tokens)

    def __len__(self):
        return len(self.tokens)

    def __iter__(self):
        iter(self.tokens)

    def __getitem__(self, item):
        return self.tokens[item]


class Inventory:
    def __init__(
            self,
            rules_by_ids: Optional[Dict[str, RuleInfo]] = None,
            word_analyses: Optional[Dict[str, WFToken]] = None,
            word_trees: Optional[Dict[str, CONLLUTree]] = None
    ):
        self.rules_by_ids = rules_by_ids or {}
        self.word_analyses = word_analyses or {}
        self.word_trees = word_trees or {}

    @staticmethod
    def _merge_trees(
            tree_l: CONLLUTree,
            tree_r: CONLLUTree,
            deprel: str,
            is_arc_l2r: bool = True
    ) -> CONLLUTree:
        tokens_l = deepcopy(tree_l.tokens)
        tokens_r = deepcopy(tree_r.tokens)
        l = len(tree_l.tokens)
        for t in tokens_r:
            t.set_idx(t.iidx + l)
            if t.ihead > 0:
                t.set_head(t.ihead + l)

        l_root_idx = tree_l.root_idx
        r_root_idx = tree_r.root_idx
        if is_arc_l2r:
            tokens_r[r_root_idx].set_head(tokens_l[l_root_idx].iidx)
            tokens_r[r_root_idx].deprel = deprel
            root_idx = l_root_idx
        else:
            tokens_l[l_root_idx].set_head(tokens_r[r_root_idx].iidx)
            tokens_l[l_root_idx].deprel = deprel
            root_idx = r_root_idx + l
        return CONLLUTree(tokens_l + tokens_r, root_idx=root_idx)

    def _merge_with_simple_rule(
            self,
            stem_tree: CONLLUTree,
            rule: RuleInfo
    ) -> CONLLUTree:
        affix_tree = CONLLUTree(
            [CONLLUToken("1", rule.short_id, rule.short_id)])
        if rule.info == "SFX":
            tree = self._merge_trees(
                stem_tree, affix_tree, deprel="affix", is_arc_l2r=True
            )
        elif rule.info == "PTFX":
            tree = self._merge_trees(
                stem_tree, affix_tree, deprel="refl", is_arc_l2r=True
            )
        elif rule.info == "PFX":
            tree = self._merge_trees(
                affix_tree, stem_tree, deprel="affix", is_arc_l2r=False
            )
        elif rule.info == "CONV":
            tree = self._merge_trees(
                stem_tree, affix_tree, deprel="conv", is_arc_l2r=True
            )
        else:
            raise AssertionError(
                'Rule info is incorrect!', rule.short_id, rule.info
            )
        return tree

    def make_subword_tree(self, word: str) -> CONLLUTree:
        if word in self.word_trees:
            return self.word_trees[word]
        if word not in self.word_analyses:
            return CONLLUTree([CONLLUToken("1", word, word)])
        wf_token = self.word_analyses[word]
        stem_tree = self.make_subword_tree(wf_token.d_lemma)
        rule = self.rules_by_ids[wf_token.rule_id]

        if isinstance(rule, CompoundRuleInfo):
            # applying modifier rules, e. g. interfixation
            modifiers_trees = []
            for m, m_rules in zip(
                    wf_token.d_modifiers or [], rule.modifier_rules or []
            ):
                m_tree = self.make_subword_tree(m)
                for m_rule in m_rules:
                    m_tree = self._merge_with_simple_rule(m_tree, m_rule)
                modifiers_trees.append(m_tree)
            # (pfx (m1 (m2 h)) sfx))
            for modifier_tree in reversed(modifiers_trees):
                stem_tree = self._merge_trees(
                    modifier_tree, stem_tree, "compound", is_arc_l2r=False
                )
            for r in rule.head_rules or []:
                stem_tree = self._merge_with_simple_rule(stem_tree, r)
            for r in rule.after_rules or []:  # e. g. prefix
                stem_tree = self._merge_with_simple_rule(stem_tree, r)
            return stem_tree

        if isinstance(rule, ComplexRuleInfo):
            for simple_rule in rule.simple_rules:
                stem_tree = self._merge_with_simple_rule(stem_tree, simple_rule)
            return stem_tree

        if isinstance(rule, RuleInfo):
            stem_tree = self._merge_with_simple_rule(stem_tree, rule)
            return stem_tree
        raise NotImplementedError

    @staticmethod
    def load_tree(text: str) -> CONLLUTree:
        word_tree = CONLLUTree.from_text(text)
        return word_tree

    def make_tree(self, text: str) -> CONLLUTree:
        word_tree = self.load_tree(text)
        subword_trees = []
        subword_roots = [-1]
        cur_len = 0
        united_subword_tokens = []
        for token in word_tree.tokens:
            subword_tree = self.make_subword_tree(token.lemma)
            subword_roots.append(cur_len + subword_tree.root_idx)
            subword_trees.append(subword_tree)
            for subword_token in subword_tree.tokens:
                subword_token.set_idx(len(united_subword_tokens) + 1)
                subword_token.set_head(int(subword_token.head) + cur_len)
                united_subword_tokens.append(subword_token)
            cur_len += len(subword_tree)

        renumerated = {"0": 0}
        for i, token in enumerate(word_tree.tokens):
            renumerated[token.idx] = i + 1

        for i, token in enumerate(word_tree.tokens):
            if token.head.isdigit():
                head_idx = token.head
            else:
                # 33.1	_	_	_	_	_	_	_	3:conj	_
                head_idx = token.deps.split(":")[0]
            renum_head = renumerated[head_idx]
            idx = subword_roots[i + 1]
            united_subword_tokens[idx].set_head(subword_roots[renum_head] + 1)
            united_subword_tokens[idx].deprel = token.deprel

        return CONLLUTree(united_subword_tokens)

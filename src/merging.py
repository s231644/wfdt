from copy import deepcopy

from src.deptree import CONLLUTree


def merge_trees(
        tree_l: CONLLUTree, tree_r: CONLLUTree,
        deprel: str, is_arc_l2r: bool = True
):
    tokens_l = deepcopy(tree_l.tokens)
    tokens_r = deepcopy(tree_r.tokens)
    l = len(tree_l.tokens)
    for t in tokens_r:
        t.idx = str(int(t.idx) + l)
        if int(t.head) > 0:
            t.head = str(int(t.head) + l)
    if is_arc_l2r:
        tokens_r[tree_r.root_idx].head = tokens_l[tree_l.root_idx].idx
        tokens_r[tree_r.root_idx].deprel = deprel
        root_idx = tree_l.root_idx
    else:
        tokens_l[tree_l.root_idx].head = str(
            int(tree_r.tokens[tree_r.root_idx].idx) + l
        )
        tokens_l[tree_l.root_idx].deprel = deprel
        root_idx = tree_r.root_idx + l
    return CONLLUTree(tokens_l + tokens_r, root_idx=root_idx)

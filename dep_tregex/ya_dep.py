import io

from dep_tregex.conll import read_trees_conll
from dep_tregex.tree_to_html import (
    write_prologue_html, write_epilogue_html, write_tree_html
)


def visualize_tree(text):
    file = io.StringIO()
    write_prologue_html(file)

    for i, tree in enumerate(read_trees_conll(text)):
        write_tree_html(file, tree)

    write_epilogue_html(file)
    return file.getvalue()

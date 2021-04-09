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


# if __name__ == '__main__':
#     text = """1	If	if	SCONJ	IN	_	3	mark	_	Discourse=condition:86->87
# 2	you	you	PRON	PRP	Case=Nom|Person=2|PronType=Prs	3	nsubj	_	Entity=(person-9)
# 3	want	want	VERB	VBP	Mood=Ind|Tense=Pres|VerbForm=Fin	12	advcl	_	_
# 4	to	to	PART	TO	_	5	mark	_	_
# 5	make	make	VERB	VB	VerbForm=Inf	3	xcomp	_	_
# 6	the	the	DET	DT	Definite=Def|PronType=Art	7	det	_	Entity=(person-26
# 7	audience	audience	NOUN	NN	Number=Sing	5	obj	_	Entity=person-26)
# 8	laugh	laugh	VERB	VB	VerbForm=Inf	5	xcomp	_	SpaceAfter=No
# 9	,	,	PUNCT	,	_	3	punct	_	_
# 10	your	your	PRON	PRP$	Person=2|Poss=Yes|PronType=Prs	11	nmod:poss	_	Discourse=joint:87->84|Entity=(abstract-87(person-9)
# 11	punchline	punchline	NOUN	NN	Number=Sing	12	nsubj	_	Entity=abstract-87)
# 12	needs	need	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	0	root	_	_
# 13	to	to	PART	TO	_	15	mark	_	_
# 14	be	be	AUX	VB	VerbForm=Inf	15	cop	_	_
# 15	surprising	surprising	ADJ	JJ	Degree=Pos	12	xcomp	_	SpaceAfter=No
# 16	.	.	PUNCT	.	_	12	punct	_	_"""
#     data = visualize_tree(text)
#     print(data)
#     with open('file.html', mode='w') as f:
#         print(data, file=f)

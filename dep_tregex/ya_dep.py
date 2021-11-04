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


if __name__ == '__main__':
    text = """1	If	if	SCONJ	IN	_	3	mark	_	Discourse=condition:86->87
2	you	you	PRON	PRP	Case=Nom|Person=2|PronType=Prs	3	nsubj	_	Entity=(person-9)
3	want	want	VERB	VBP	Mood=Ind|Tense=Pres|VerbForm=Fin	12	advcl	_	_
4	to	to	PART	TO	_	5	mark	_	_
5	make	make	VERB	VB	VerbForm=Inf	3	xcomp	_	_
6	the	the	DET	DT	Definite=Def|PronType=Art	7	det	_	Entity=(person-26
7	audience	audience	NOUN	NN	Number=Sing	5	obj	_	Entity=person-26)
8	laugh	laugh	VERB	VB	VerbForm=Inf	5	xcomp	_	SpaceAfter=No
9	,	,	PUNCT	,	_	3	punct	_	_
10	your	your	PRON	PRP$	Person=2|Poss=Yes|PronType=Prs	11	nmod:poss	_	Discourse=joint:87->84|Entity=(abstract-87(person-9)
11	punchline	punchline	NOUN	NN	Number=Sing	12	nsubj	_	Entity=abstract-87)
12	needs	need	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	0	root	_	_
13	to	to	PART	TO	_	15	mark	_	_
14	be	be	AUX	VB	VerbForm=Inf	15	cop	_	_
15	surprising	surprising	ADJ	JJ	Degree=Pos	12	xcomp	_	SpaceAfter=No
16	.	.	PUNCT	.	_	12	punct	_	_"""

    text0 = """# sent_id = es-train-019-s446
# text = Incluso escuchándolas sin atención se aprecia la diferencia en la tecnología de grabación, lo que hace difícil aceptar que se hicieran el mismo año.
1	Incluso	incluso	ADV	_	_	2	advmod	_	_
2-4	escuchándolas	_	_	_	_	_	_	_	_
2	escuchán	escuchán	VERB	_	Mood=Ind|Number=Plur|Person=3|Tense=Fut|VerbForm=Fin	8	advcl	_	_
3	do	do	NOUN	_	_	2	iobj	_	_
4	las	él	PRON	_	Case=Acc|Gender=Fem|Number=Plur|Person=3|PrepCase=Npr|PronType=Prs	2	obj	_	_
5	sin	sin	ADP	_	_	6	case	_	_
6	atención	atención	NOUN	_	Gender=Fem|Number=Sing	2	obl	_	_
7	se	él	PRON	_	Case=Acc,Dat|Person=3|PrepCase=Npr|PronType=Prs|Reflex=Yes	8	iobj	_	_
8	aprecia	apreciar	VERB	_	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	0	root	_	_
9	la	el	DET	_	Definite=Def|Gender=Fem|Number=Sing|PronType=Art	10	det	_	_
10	diferencia	diferencia	NOUN	_	Gender=Fem|Number=Sing	8	nsubj	_	_
11	en	en	ADP	_	_	13	case	_	_
12	la	el	DET	_	Definite=Def|Gender=Fem|Number=Sing|PronType=Art	13	det	_	_
13	tecnología	tecnología	NOUN	_	Gender=Fem|Number=Sing	10	nmod	_	_
14	de	de	ADP	_	_	15	case	_	_
15	grabación	grabación	NOUN	_	Gender=Fem|Number=Sing	13	nmod	_	SpaceAfter=No
16	,	,	PUNCT	_	_	8	punct	_	_
17	lo	él	PRON	_	Case=Acc|Gender=Masc|Number=Sing|Person=3|PrepCase=Npr|PronType=Prs	18	det	_	_
18	que	que	SCONJ	_	_	20	mark	_	_
19	hace	hacer	VERB	_	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	20	cop	_	_
20	difícil	difícil	ADJ	_	Number=Sing	8	parataxis	_	_
21	aceptar	aceptar	VERB	_	VerbForm=Inf	20	xcomp	_	_
22	que	que	SCONJ	_	_	24	mark	_	_
23	se	él	PRON	_	Case=Acc,Dat|Person=3|PrepCase=Npr|PronType=Prs|Reflex=Yes	24	iobj	_	_
24	hicieran	hacer	VERB	_	Mood=Sub|Number=Plur|Person=3|Tense=Imp|VerbForm=Fin	21	ccomp	_	_
25	el	el	DET	_	Definite=Def|Gender=Masc|Number=Sing|PronType=Art	27	det	_	_
26	mismo	mismo	ADJ	_	Gender=Masc|Number=Sing	27	amod	_	_
27	año	año	NOUN	_	Gender=Masc|Number=Sing	24	obl	_	SpaceAfter=No
28	.	.	PUNCT	_	_	8	punct	_	_
"""

    data = visualize_tree(text0)
    print(data)
    with open('file.html', mode='w') as f:
        print(data, file=f)

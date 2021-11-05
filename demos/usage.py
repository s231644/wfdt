from src import WFToken, RuleInfo, ComplexRuleInfo, CompoundRuleInfo, Inventory

rules_by_ids = {
    "-able": RuleInfo("-able", "SFX", "NOUN", "ADJ"),
    "-ite": RuleInfo("-ite", "SFX", "VERB", "ADV"),
    "-ly": RuleInfo("-ly", "SFX", "ADJ", "ADV"),

    "in-": RuleInfo("in-", "PFX", "ADJ", "ADJ"),

    "ADJ + NOUN + -ed -> ADJ": CompoundRuleInfo(
        "A+N+ed", "COMPOUND,SFX", "NOUN", "ADJ",
        [RuleInfo("-ed", "SFX", "NOUN", "ADJ")], [[]], []
    ),
}

word_analyses = {
    'comfortable': WFToken('comfort', 'NOUN', '-able'),
    'definite': WFToken('define', 'VERB', '-ite'),
    'indefinite': WFToken('definite', 'ADJ', 'in-'),
    'indefinitely': WFToken('indefinite', 'ADJ', '-ly'),
    'green-eyed': WFToken('eye', 'NOUN', "ADJ + NOUN + -ed -> ADJ", ['green'])
}

inventory = Inventory(
    word_analyses=word_analyses,
    rules_by_ids=rules_by_ids
)

for word in word_analyses:
    subword_tree = inventory.make_subword_tree(word)
    subword_tree.html(fpath=f"tree_{word}.html")

ud_sentence = """
# sent_id = weblog-blogspot.com_rigorousintuition_20050518101500_ENG_20050518_101500-0028
# text = So instead Posada may be held indefinitely, in comfortable custody.
1	So	so	ADV	RB	_	6	advmod	6:advmod	_
2	instead	instead	ADV	RB	_	6	advmod	6:advmod	_
3	Posada	Posada	PROPN	NNP	Number=Sing	6	nsubj:pass	6:nsubj:pass	_
4	may	may	AUX	MD	VerbForm=Fin	6	aux	6:aux	_
5	be	be	AUX	VB	VerbForm=Inf	6	aux:pass	6:aux:pass	_
6	held	hold	VERB	VBN	Tense=Past|VerbForm=Part|Voice=Pass	0	root	0:root	_
7	indefinitely	indefinitely	ADV	RB	_	6	advmod	6:advmod	SpaceAfter=No
8	,	,	PUNCT	,	_	6	punct	6:punct	_
9	in	in	ADP	IN	_	11	case	11:case	_
10	comfortable	comfortable	ADJ	JJ	Degree=Pos	11	amod	11:amod	_
11	custody	custody	NOUN	NN	Number=Sing	6	obl	6:obl:in	SpaceAfter=No
12	.	.	PUNCT	.	_	6	punct	6:punct	_
""".strip()

tree = inventory.make_tree(ud_sentence)
tree_html = tree.html("file.html")

# print(tree.latex())

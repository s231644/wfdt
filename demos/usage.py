from src import (
    LexItem, WFToken,
    RuleInfo, ComplexRuleInfo, CompoundRuleInfo,
    Inventory
)

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

lexicon = {
    'comfort': LexItem(
        lemma='comfort', form='comfort', upos='NOUN'
    ),
    'comfortable': LexItem(
        lemma='comfortable', form='comfortable', upos='ADJ'
    ),
    'define': LexItem(
        lemma='define', form='define', upos='VERB'
    ),
    'definite': LexItem(
        lemma='definite', form='definite', upos='ADJ'
    ),
    'indefinite': LexItem(
        lemma='indefinite', form='indefinite', upos='ADJ'
    ),
    'indefinitely': LexItem(
        lemma='indefinitely', form='indefinitely', upos='ADV'
    ),
    'eye': LexItem(
        lemma='eye', form='eye', upos='NOUN'
    ),
    'green': LexItem(
        lemma='green', form='green', upos='ADJ'
    ),
    'green-eyed': LexItem(
        lemma='green-eyed', form='green-eyed', upos='ADJ'
    ),
}

word_analyses = {
    lexicon['comfortable']: WFToken(
        d_from=lexicon['comfort'],
        rule_id='-able',
    ),
    lexicon['definite']: WFToken(
        d_from=lexicon['define'],
        rule_id='-ite',
    ),
    lexicon['indefinite']: WFToken(
        d_from=lexicon['definite'],
        rule_id='in-',
    ),
    lexicon['indefinitely']: WFToken(
        d_from=lexicon['indefinite'],
        rule_id='-ly',
    ),
    lexicon['green-eyed']: WFToken(
        d_from=lexicon['eye'],
        rule_id="ADJ + NOUN + -ed -> ADJ",
        d_modifiers=[lexicon['green']]
    )
}

inventory = Inventory(
    word_analyses=word_analyses,
    rules_by_ids=rules_by_ids
)

for word in word_analyses:
    subword_tree = inventory.make_subword_tree(word)
    subword_tree.html(fpath=f"tree_{word.lemma}_{word.upos}.html")

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

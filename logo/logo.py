from src import (
    LexItem, WFToken,
    RuleInfo,
    Inventory
)

rules_by_ids = {
    "-ion": RuleInfo("ion", "SFX", "VERB", "NOUN"),
    "-ent": RuleInfo("ent", "SFX", "VERB", "ADJ"),
    "-cy": RuleInfo("cy", "SFX", "ADJ", "NOUN"),

    "in-": RuleInfo("in", "PFX", "ADJ", "ADJ"),

    "-s": RuleInfo("s", "INFL", "NOUN", "NOUN"),
}

lexicon = {
    'word': LexItem(
        lemma='word', form='word', upos='NOUN'
    ),

    'form': LexItem(
        lemma='form', form='form', upos='VERB'
    ),
    'formation': LexItem(
        lemma='formation', form='formation', upos='NOUN'
    ),

    'depend': LexItem(
        lemma='depend', form='depend', upos='VERB'
    ),
    'dependent': LexItem(
        lemma='dependent', form='dependent', upos='ADJ'
    ),
    'independent': LexItem(
        lemma='independent', form='independent', upos='ADJ'
    ),
    'dependency': LexItem(
        lemma='dependency', form='dependency', upos='NOUN'
    ),
    'independency': LexItem(
        lemma='independency', form='independency', upos='NOUN'
    ),

    'tree': LexItem(
        lemma='tree', form='tree', upos='NOUN'
    ),
    'trees': LexItem(
        lemma='trees', form='trees', upos='NOUN'
    ),
}

word_analyses = {
    lexicon['formation']: WFToken(
        d_from=lexicon['form'],
        rule_id='-ion',
    ),
    lexicon['dependent']: WFToken(
        d_from=lexicon['depend'],
        rule_id='-ent',
    ),
    lexicon['independent']: WFToken(
        d_from=lexicon['dependent'],
        rule_id='in-',
    ),
    lexicon['independency']: WFToken(
        d_from=lexicon['independent'],
        rule_id='-cy',
    ),
    lexicon['dependency']: WFToken(
        d_from=lexicon['dependent'],
        rule_id='-cy',
    ),
    lexicon['trees']: WFToken(
        d_from=lexicon['tree'],
        rule_id='-s',
    ),
}

inventory = Inventory(
    word_analyses=word_analyses,
    rules_by_ids=rules_by_ids
)

ud_sentence = """
# text = word formation dependency trees
1	word	word	NOUN	_	_	2	compound	2:compound	_
2	formation	formation	NOUN	_	_	4	compound	4:compound	_
3	dependency	dependency	NOUN	_	_	4	compound	4:compound	_
4	trees	trees	NOUN	_	_	0	root	0:root	_
""".strip()

tree = inventory.make_tree(ud_sentence)
tree_html = tree.html("logo.html")

# print(tree.latex())

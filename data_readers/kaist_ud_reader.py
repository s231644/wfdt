from typing import Dict, List, Tuple, Any

from src import (
    LexItem,
    CONLLUToken, CONLLUTree,
    Inventory
)
from data_readers.abstract_readers import ReaderAbstract


class KaistUDTReader(ReaderAbstract):
    """
    KAIST Universal Dependencies Treebank already has morpheme-segmented
    tokens in the lemma column, and there are fine-grained KAIST POS tags
    (more than 60) assigned to each morpheme.

    !!! It is not clear yet how to assign intra-word dependencies.

    # sent_id = M2TA_069-s4
    # text = 서울에는 다리도 많았습니다.
    1	서울에는	서울+에+는	PROPN	nq+jca+jxt	_	3	dislocated	_	_
    2	다리도	다리+도	ADV	ncn+jxc	_	3	advcl	_	_
    3	많았습니다	많+았+습니다	ADJ	paa+ep+ef	_	0	root	_	SpaceAfter=No
    4	.	.	PUNCT	sf	_	3	punct	_	_

    # sent_id = M2TA_069-s30
    # text = 한인은 성냥, 연필, 공책, 비누 같은 일용품도 만들지 못하도록 하고 토지를 빼앗아 간도로 밀려나가게 되었다.
    1	한인은	한인+은	NOUN	ncn+jxt	_	17	dislocated	_	_
    2	성냥	성냥	NOUN	ncn	_	9	dep	_	SpaceAfter=No
    3	,	,	PUNCT	sp	_	2	punct	_	_
    4	연필	연필	NOUN	ncn	_	2	conj	_	SpaceAfter=No
    5	,	,	PUNCT	sp	_	4	punct	_	_
    6	공책	공책	NOUN	ncn	_	2	conj	_	SpaceAfter=No
    7	,	,	PUNCT	sp	_	6	punct	_	_
    8	비누	비누	NOUN	ncn	_	2	conj	_	_
    9	같은	같+ㄴ	ADJ	paa+etm	_	10	amod	_	_
    10	일용품도	일용품+도	ADV	ncn+jxc	_	11	advcl	_	_
    11	만들지	만들+지	VERB	pvg+ecx	_	13	ccomp	_	_
    12	못하도록	못하+도록	SCONJ	px+ecs	_	11	aux	_	_
    13	하고	하+고	CCONJ	pvg+ecc	_	0	root	_	_
    14	토지를	토지+를	NOUN	ncn+jco	_	15	obj	_	_
    15	빼앗아	빼앗+아	SCONJ	pvg+ecs	_	17	ccomp	_	_
    16	간도로	간도+로	ADV	nq+jca	_	17	advcl	_	_
    17	밀려나가게	밀리+어+나+아+가+게	AUX	pvg+ecx+px+ecx+px+ecx	_	13	conj	_	_
    18	되었다	되+었+다	AUX	px+ep+ef	_	17	aux	_	SpaceAfter=No
    19	.	.	PUNCT	sf	_	18	punct	_	_

    """
    # KAIST POS to UPOS (https://aclanthology.org/2020.lrec-1.472.pdf)
    POS2UPOS = {
        "pad": "ADJ",
        "paa": "ADJ",

        "mag": "ADV",
        "maj": "ADV",
        "mad": "ADV",

        "ii": "INTJ",

        "ncpa": "NOUN",
        "ncps": "NOUN",
        "ncn": "NOUN",
        "ncr": "NOUN",

        "nq": "PROPN",
        "nqpa": "PROPN",
        "nqpb": "PROPN",
        "nqpc": "PROPN",
        "nqq": "PROPN",
        "f": "PROPN",

        "pvd": "VERB",
        "pvg": "VERB",

        "nbn": "ADP",
        "nbs": "ADP",
        "nbu": "ADP",
        "jcs": "ADP",
        "jcc": "ADP",
        "jcm": "ADP",
        "jco": "ADP",
        "jca": "ADP",
        "jcv": "ADP",
        "jcr": "ADP",
        "jxc": "ADP",
        "jxf": "ADP",
        "jgt": "ADP",
        "jp": "ADP",
        "jxt": "ADP",
        "jct": "ADP",

        "px": "AUX",
        "ep": "AUX",

        "jcj": "CCONJ",
        "ecc": "CCONJ",

        "mmd": "DET",
        "mma": "DET",

        "nnc": "NUM",
        "nno": "NUM",

        "ef": "PART",
        "ecx": "PART",
        "etn": "PART",
        "etm": "PART",
        "xp": "PART",
        "xsnu": "PART",
        "xsnca": "PART",
        "xsncc": "PART",
        "xsna": "PART",
        "xsns": "PART",
        "xsnx": "PART",
        "xsvv": "PART",
        "xsvn": "PART",
        "xsva": "PART",
        "xsms": "PART",
        "xsmn": "PART",
        "xsam": "PART",
        "xsas": "PART",
        "xsv": "PART",
        "xsn": "PART",
        "xsm": "PART",
        "xsa": "PART",

        "npp": "PRON",
        "npd": "PRON",

        "ecs": "SCONJ",

        "sf": "PUNCT",
        "se": "PUNCT",
        "sp": "PUNCT",
        "sd": "PUNCT",
        "sl": "PUNCT",
        "sr": "PUNCT",

        "sy": "SYM",
        "su": "SYM",

        "n/a": "X"
    }

    def build_inventory(self, *args, **kwargs) -> Inventory:
        raise NotImplementedError

    def read_dataset(self, *args, **kwargs) -> Dict[LexItem, Any]:
        raise NotImplementedError

    def read_sample(self, *args, **kwargs) -> Tuple[LexItem, Any]:
        raise NotImplementedError

from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import List, Union


@dataclass
@dataclass_json
class DatasetCard:
    lang: str
    name: str
    version: str
    authors: str
    url: str
    record_format: str
    level: Union[List[str], str]
    phoenomena: List[str]


all_cards = {
    "afr_aucopro": DatasetCard(
        lang="afr",
        name="AuCoPro",
        version="2014-01-31",
        authors="Menno van Zaanen & Gerhard B. van Huyssteen",
        url="http://tinyurl.com/aucopro",
        record_format="segmentation",
        level=["morph"],
        phoenomena=["compounding"]
    ),
    "deu_germanet": DatasetCard(
        lang="deu",
        name="GermaNet",
        version="17.0",
        authors="Henrich, V., & E. Hinrichs",
        url="https://uni-tuebingen.de/fakultaeten/philosophische-fakultaet/fachbereiche/neuphilologie/seminar-fuer-sprachwissenschaft/arbeitsbereiche/allg-sprachwissenschaft-computerlinguistik/ressourcen/lexica/germanet-1/",
        record_format="segmentation",
        level=["lemma"],
        phoenomena=["compounding"]
    ),
    "fra_demonext": DatasetCard(
        lang="fra",
        name="Demonext",
        version="2022-06-25",
        authors="Fiammetta Namer, Nabil Hathout",
        url="https://www.demonext.xyz/en/home/",
        record_format="relations",
        level=["lemma", "affix morpheme"],
        phoenomena=["derivation"]
    ),
    "ita_derivatario": DatasetCard(
        lang="ita",
        name="DerIvaTario",
        version="2016",
        authors="Talamo, Celata, & Bertinetto",
        url="https://derivatario.sns.it",
        record_format="segmentation",
        level=["lemma", "affix morpheme"],
        phoenomena=["derivation"]
    ),
    "kor_kaist_udt": DatasetCard(
        lang="kor",
        name="The KAIST Korean Universal Dependency Treebank",
        version="2018-04-15 v2.2",
        authors="Jayeol Chun, Na-Rae Han, Jena D. Hwang, and Jinho D. Choi",
        url="https://github.com/UniversalDependencies/UD_Korean-Kaist",
        record_format="segmentation",
        level=["wordform", "morpheme"],
        phoenomena=["inflection", "derivation", "compounding"]
    ),
    "lat_wfl": DatasetCard(
        lang="lat",
        name="Word Formation Latin (WFL)",
        version="17-10-2017",
        authors="Eleonora Litta, Marco Passarotti, Chris Culy",
        url="https://github.com/CIRCSE/WFL",
        record_format="relations",
        level=["lemma", "affix morpheme"],
        phoenomena=["derivation", "compounding"]
    ),
    "lat_lemlat3": DatasetCard(
        lang="lat",
        name="LEMLAT3",
        version="3.0",
        authors="Marco Passarotti, Paolo Ruffolo, Flavio M. Cecchini, Eleonora Litta, Marco Budassi",
        url="https://github.com/CIRCSE/LEMLAT3",
        record_format="relations",
        level=["lemma", "affix morpheme"],
        phoenomena=["derivation", "compounding"]
    ),
    "ndl_aucopro": DatasetCard(
        lang="ndl",
        name="AuCoPro",
        version="2014-01-31",
        authors="Menno van Zaanen & Gerhard B. van Huyssteen",
        url="http://tinyurl.com/aucopro",
        record_format="segmentation",
        level=["morph"],
        phoenomena=["compounding"]
    ),
    "zho_chinesechardeps": DatasetCard(
        lang="zho",
        name="SJTU (Shanghai Jiao Tong University) Chinese Character Dependency Treebank",
        version="20120519_45000",
        authors="Zhao Hai, Masao Utiyama and Eiichiro Sumita",
        url="https://bcmi.sjtu.edu.cn/~zebraform/",
        record_format="intraword dependencies",
        level=["morpheme"],
        phoenomena=["derivation", "compounding"]
    ),
}

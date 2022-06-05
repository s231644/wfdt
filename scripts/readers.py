import json
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple

from src import WFToken, RuleInfo, ComplexRuleInfo, CompoundRuleInfo, Inventory
from src import CONLLUToken, CONLLUTree


class RulesReader:
    def read_rules(self, path: str) -> Dict[RuleInfo]:
        pass


class ReaderAbstract(ABC):
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def read_dataset(self, *args, **kwargs) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def read_sample(self, *args, **kwargs) -> Tuple[str, Any]:
        raise NotImplementedError


class AnalysesReaderAbstract(ReaderAbstract, ABC):
    @abstractmethod
    def read_dataset(self, *args, **kwargs) -> Dict[str, WFToken]:
        raise NotImplementedError

    @abstractmethod
    def read_sample(self, *args, **kwargs) -> Tuple[str, WFToken]:
        raise NotImplementedError


# AuCoPro


class ReaderAuCoPro(AnalysesReaderAbstract):
    def read_dataset(self, path: str) -> Dict[str, WFToken]:
        with open(path, "r") as f:
            lines = f.readlines()
        results = {}
        for line in lines:
            word, analysis = self.read_sample(line.strip())
            results[word] = analysis
        return results

    def read_sample(self, line: str) -> Tuple[str, WFToken]:
        word = line.replace("_", "").replace("+", "").replace(" ", "")
        lemmas = [p.split("_")[0].strip() for p in line.split("+")]
        # TODO: correct bracketing and POS tags
        d_upos = "NOUN"
        head = lemmas[-1]
        modifiers = lemmas[:-1]
        rule_id = "UNK + " * len(modifiers) + f"{d_upos} -> {d_upos}"
        analysis = WFToken(head, d_upos, rule_id, modifiers)
        return word, analysis


# reader = ReaderAuCoPro()
# results = reader.read_dataset("../data/Afrikaans/aucopro/sample.txt")
# print(results)

# reader = ReaderAuCoPro()
# results = reader.read_dataset("../data/Dutch/aucopro/sample.txt")
# print(results)


# GermaNet


class ReaderGermaNet(AnalysesReaderAbstract):
    def __init__(self, n_lines_skip: int = 2):
        super().__init__()
        self.n_lines_skip = n_lines_skip

    def read_dataset(self, path: str) -> Dict[str, WFToken]:
        with open(path, "r") as f:
            lines = f.readlines()[self.n_lines_skip:]
        results = {}
        for line in lines:
            word, analysis = self.read_sample(line.strip())
            results[word] = analysis
        return results

    def read_sample(self, line: str) -> Tuple[str, WFToken]:
        word, modifiers_str, head = line.split("\t")
        modifiers = []
        for m in modifiers_str.split():
            modifiers.append(m.split("|")[0])
        # TODO: correct bracketing and POS tags
        d_upos = "NOUN"
        rule_id = "UNK + " * len(modifiers) + f"{d_upos} -> {d_upos}"
        analysis = WFToken(head, d_upos, rule_id, modifiers)
        return word, analysis

# reader = ReaderGermaNet(n_lines_skip=2)
# results = reader.read_dataset("../data/German/germanet/sample.txt")
# print(results)


# UDer


class ReaderUDer(AnalysesReaderAbstract):
    def read_dataset(self, path: str) -> Dict[str, WFToken]:
        with open(path, "r") as f:
            lines = f.readlines()

        results = {}
        id_to_lemma = self._read_id_to_lemma(lines)

        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                word, analysis = self.read_sample(line, id_to_lemma)
            except KeyError:
                # id_to_lemma has no key "" for the root of the tree
                continue
            results[word] = analysis
        return results

    def read_sample(
            self, line: str, id_to_lemma: Dict[str, str]
    ) -> Tuple[str, WFToken]:
        lid, lemmapos, lemma, pos, _, _, par, wf_meta, _, _ = line.split("\t")
        # TODO: correct affix and POS tags
        d_upos = "UNK"
        head = id_to_lemma[par]
        wf_info = self._read_wf_meta(wf_meta)
        rule_id = wf_info["Rule"]
        if wf_info.get("Type", "Derivation") == "Compounding":
            source_ids = wf_info["Sources"]
            modifiers = [id_to_lemma[s] for s in source_ids if s != par]
        else:
            modifiers = None
        analysis = WFToken(head, d_upos, rule_id, modifiers)
        return lemma, analysis

    @staticmethod
    def _read_id_to_lemma(lines: List[str]) -> Dict[str, str]:
        id_to_lemma = {}
        for line in lines:
            line = line.strip()
            if not line:
                continue
            lid, lemmapos, lemma, pos, _, _, _, _, _, _ = line.split("\t")
            id_to_lemma[lid] = lemma
        return id_to_lemma

    @staticmethod
    def _read_wf_meta(wf_meta: str):
        wf_info = {}
        for elem in wf_meta.split("&"):
            k, v = elem.split("=")
            if k == "Sources":
                # Sources=1144.0,80074.0
                v = v.split(",")
            wf_info[k] = v
        return wf_info


# reader = ReaderUDer()
# results = reader.read_dataset("../data/German/derivbase-uder/sample.txt")
# print(results)

# reader = ReaderUDer()
# results = reader.read_dataset("../data/Russian/derivbaseru-uder/sample.txt")
# print(results)
#
# reader = ReaderUDer()
# results = reader.read_dataset("../data/Russian/rucompounds-uder/sample.txt")
# print(results)


# Character‐level Dependencies of Chinese


class CharDepsReader(ReaderAbstract):
    POS2UPOS = {
        # absolute POS tags
        "p": "PRON",
        "n": "NOUN",
        "v": "VERB",
        "a": "ADJ",
        "d": "ADV",

        # character‐level POS tag set: all above +
        # Number, foreign letter transliteration and other non‐Chinese characters
        # TODO: i,f -> UPOS conversion
        "i": "NUM",
        # Functional character 的(of) 们(‐es) 在(at) …
        "f": "AFFIX",
    }

    def read_dataset(self, path: str) -> Dict[str, CONLLUTree]:
        with open(path, "r") as f:
            lines = f.readlines()

        results = {}

        cur_lines = []
        for line in lines:
            line = line.strip()
            if not line:
                word, analysis = self.read_sample(cur_lines)
                results[word] = analysis
                cur_lines = []
                continue
            if line.startswith("["):
                continue
            cur_lines.append(line)
        else:
            if cur_lines:
                word, analysis = self.read_sample(cur_lines)
                results[word] = analysis

        return results

    def read_sample(self, cur_lines: List[str]) -> Tuple[str, CONLLUTree]:
        tokens = []
        for line in cur_lines:
            idx, char, pos, head_idx, deprel = line.split()
            token = CONLLUToken(
                idx=idx,
                form=char,
                lemma=char,
                upos=self.POS2UPOS[pos],
                xpos=pos,
                head=head_idx,
                deprel=deprel,
            )
            tokens.append(token)
        word = "".join([t.form for t in tokens])
        word_tree = CONLLUTree(tokens)
        return word, word_tree


# reader = CharDepsReader()
# results = reader.read_dataset("../data/Chinese/chinesechardeps/sample.txt")
# print(results)

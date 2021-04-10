from dataclasses import dataclass


@dataclass
class CONLLUToken:
    idx: str
    form: str
    lemma: str = "_"
    upos: str = "_"
    xpos: str = "_"
    feats: str = "_"
    head: str = "0"
    deprel: str = "root"
    deps: str = "_"
    misc: str = "_"

    def __str__(self):
        return "\t".join([
            self.idx, self.form, self.lemma, self.upos, self.xpos,
            self.feats, self.head, self.deprel, self.deps, self.misc
        ])

    def __repr__(self):
        return self.__str__()

    @classmethod
    def from_str(cls, line: str):
        return cls(*line.split("\t"))

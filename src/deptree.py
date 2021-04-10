from typing import List, Optional

from src.deptoken import CONLLUToken
from dep_tregex.ya_dep import visualize_tree


class CONLLUTree:
    def __init__(
            self,
            tokens: List[CONLLUToken],
            sent_id: str = "",
            sent_text: Optional[str] = None,
            root_idx: Optional[int] = None
    ):
        self.tokens = tokens

        if root_idx is not None:
            self.root_idx = int(root_idx)
        else:
            for i, token in enumerate(tokens):
                if token.head == "0":
                    self.root_idx = i

        self.sent_id = sent_id
        self.sent_text = sent_text or ' '.join([token.form for token in tokens])

    def __str__(self):
        return "\n".join(
            [
                f'# sent_id = {self.sent_id}',
                f'# text = {self.sent_text}'
            ] + [str(token) for token in self.tokens]
        )

    def __repr__(self):
        return self.__str__()

    def html(self, fpath: Optional[str] = None):
        content = visualize_tree("\n".join([str(token) for token in self.tokens]))
        if fpath:
            with open(fpath, "w") as f:
                f.write(content)
        return content

    @classmethod
    def from_text(cls, text: str):
        lines = text.strip().split("\n")
        tokens = [
            CONLLUToken.from_str(line)
            for line in lines if not line.startswith("#")
        ]
        return cls(tokens)

    def __len__(self):
        return len(self.tokens)

    def __iter__(self):
        iter(self.tokens)

    def __getitem__(self, item):
        return self.tokens[item]

from dataclasses import dataclass


@dataclass
class WFToken:
    lemma: str
    upos: str
    derived_from: str  # derivation only
    derived_with: str  # simple rules only
    strong: bool

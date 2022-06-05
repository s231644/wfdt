import os
from dataclasses import dataclass


@dataclass
class DatasetInfo:
    lang: str
    name: str
    path: str
    meta: str = ""


datasets = [
    DatasetInfo(
        lang="Afrikaans",
        name="AuCoPro",
        path="Afrikaans/aucopro/sample.txt",
        meta="Source: https://gerhard.pro/research-projects/aucopro/"
    ),
    DatasetInfo(
        lang="Dutch",
        name="AuCoPro",
        path="Dutch/aucopro/sample.txt",
        meta="Source: https://gerhard.pro/research-projects/aucopro/"
    ),
]

from .abstract_readers import ReaderAbstract, AnalysesReaderAbstract
from .aucopro_reader import AuCoProReader
from .char_deps_reader import CharDepsReader
from .demonext_reader import DemonextReader
from .germanet_reader import GermaNetReader
from .uder_reader import UDerReader

__all__ = [
    "ReaderAbstract",
    "AnalysesReaderAbstract",
    "AuCoProReader",
    "CharDepsReader",
    "DemonextReader",
    "GermaNetReader",
    "UDerReader"
]

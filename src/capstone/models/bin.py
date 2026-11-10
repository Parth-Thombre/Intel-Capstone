from dataclasses import dataclass

from .enums import BinState


@dataclass(eq=False)
class Bin:
    """The standard container that carries material."""
    bin_id: str
    contents: str = ""
    state: BinState = BinState.EMPTY

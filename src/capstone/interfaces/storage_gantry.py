from abc import ABC, abstractmethod


class StorageGantry(ABC):
    @abstractmethod
    def place_bin_at_handoff(self, bin) -> None: ...

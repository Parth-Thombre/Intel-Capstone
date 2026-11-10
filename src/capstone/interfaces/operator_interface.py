from abc import ABC, abstractmethod


class OperatorInterface(ABC):
    @abstractmethod
    def prompt_fill(self, bin_id: str, material_type: str, tool_id: str) -> None: ...

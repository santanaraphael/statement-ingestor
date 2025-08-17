from abc import ABC, abstractmethod
from statement_ingestor.models import Statement


class BaseParser(ABC):
    @abstractmethod
    def parse(self, file_path: str) -> Statement:
        pass

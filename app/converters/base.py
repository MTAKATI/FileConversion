# Defines the abstract standard that all conversion strategies must implement.

from abc import ABC, abstractmethod
from pathlib import Path

class BaseConversionStrategy(ABC):
    @abstractmethod
    def convert(self, input_path: Path, output_path: Path) -> Path:
        """
        Converts the at input_path and save the output to output_path.
        Must return the final Path object of the converted file.
        """
        pass
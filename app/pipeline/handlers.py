from abc import ABC, abstractmethod
from pathlib import Path
from app.converters.factory import ConverterFactory

class BaseHandler(ABC):
    def __init__(self, next_handler=None):
        self.next_handler = next_handler

    def handle(self, context:dict) -> dict:
        self.process(context)
        if self.next_handler:
            return self.next_handler.handle(context)
        return context

    @abstractmethod
    def process(self, context: dict):
        pass

class ValidationHandler(BaseHandler):
        """Step 1: Ensure input file exists before running conversion"""
        def process(self, context:dict):
            input_path = Path(context["input_path"])
            if not input_path.exists():
                raise FileNotFoundError(f"Input file does not exist: {input_path}")
            context["input_path_obj"] = input_path

class ExecutionHandler(BaseHandler):
     """Step 2: Resolve strategy from Factory amd run conversion."""
     def process(self, context:dict):
          input_path = context["input_path_obj"]
          output_path = Path(context["output_path"])

          strategy = ConverterFactory.get_strategy(input_path)
          result_path = strategy.convert(input_path, output_path)

          context["result_path"]= str(result_path)

class CleanupHandler(BaseHandler):
     """Step 3: Optional post-processing / cleaning-up step"""
     def process(self, context: dict):
        # Example: Log completion or remove temporary source files if requested
        context["status"] = "COMPLETED"
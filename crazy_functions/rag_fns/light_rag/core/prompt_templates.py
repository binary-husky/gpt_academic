from dataclasses import dataclass, field
from typing import Dict, List
import importlib.util
import os


@dataclass
class PromptTemplates:
    """Manage system prompt templates for RAG system"""

    # Delimiters and separators
    field_separator: str = field(default="<SEP>")
    tuple_delimiter: str = field(default="<|>")
    record_delimiter: str = field(default="##")
    completion_delimiter: str = field(default="<|COMPLETE|>")

    # Process tickers
    process_tickers: List[str] = field(
        default_factory=lambda: ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    )

    # Default entity types
    default_entity_types: List[str] = field(
        default_factory=lambda: ["organization", "person", "geo", "event"]
    )

    # All prompt templates predefined with empty defaults
    entity_extraction: str = field(default="")
    summarize_entity_descriptions: str = field(default="")
    entiti_continue_extraction: str = field(default="")
    entiti_if_loop_extraction: str = field(default="")
    fail_response: str = field(default="")
    rag_response: str = field(default="")
    naive_rag_response: str = field(default="")
    keywords_extraction: str = field(default="")

    def __post_init__(self):
        """Load prompts from the prompt.py file after initialization"""
        self.load_prompts()

    def load_prompts(self, prompts_path: str = None):
        """Load prompts from the specified file path or from default location"""
        if prompts_path is None:
            # Default path relative to current directory
            prompts_path = os.path.join(os.path.dirname(__file__), "prompt.py")

        try:
            # Load the module from file path
            spec = importlib.util.spec_from_file_location("prompt", prompts_path)
            if spec and spec.loader:
                prompt_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(prompt_module)

                # Get the PROMPTS dictionary
                prompts_dict = getattr(prompt_module, "PROMPTS", {})

                # Load field separator from module level
                self.field_separator = getattr(prompt_module, "GRAPH_FIELD_SEP", self.field_separator)

                # Load delimiters from PROMPTS dictionary
                self.tuple_delimiter = prompts_dict.get("DEFAULT_TUPLE_DELIMITER", self.tuple_delimiter)
                self.record_delimiter = prompts_dict.get("DEFAULT_RECORD_DELIMITER", self.record_delimiter)
                self.completion_delimiter = prompts_dict.get("DEFAULT_COMPLETION_DELIMITER", self.completion_delimiter)

                # Load process tickers
                self.process_tickers = prompts_dict.get("process_tickers", self.process_tickers)

                # Load entity types
                self.default_entity_types = prompts_dict.get("DEFAULT_ENTITY_TYPES", self.default_entity_types)

                # Load all prompt templates
                for key, value in prompts_dict.items():
                    # Convert the key to match class attribute names if needed
                    attr_name = key.lower()
                    if hasattr(self, attr_name):
                        setattr(self, attr_name, value)

        except Exception as e:
            print(f"Error loading prompts from {prompts_path}: {str(e)}")
            raise

    def format_entity_extraction(self, text: str, entity_types: List[str] = None) -> str:
        """Format entity extraction prompt"""
        if entity_types is None:
            entity_types = self.default_entity_types
        return self.entity_extraction.format(
            entity_types=", ".join(entity_types),
            input_text=text,
            tuple_delimiter=self.tuple_delimiter,
            record_delimiter=self.record_delimiter,
            completion_delimiter=self.completion_delimiter
        )

    def format_summarize_entity(self, entity_name: str, description_list: List[str]) -> str:
        """Format entity summarization prompt"""
        return self.summarize_entity_descriptions.format(
            entity_name=entity_name,
            description_list="\n".join(description_list)
        )

    def format_keyword_extraction(self, query: str) -> str:
        """Format keyword extraction prompt"""
        return self.keywords_extraction.format(query=query)

    def format_rag_response(
            self,
            context_data: str,
            response_type: str = "detailed paragraph"
    ) -> str:
        """Format RAG response prompt"""
        return self.rag_response.format(
            context_data=context_data,
            response_type=response_type
        )

    def format_naive_rag_response(
            self,
            content_data: str,
            response_type: str = "detailed paragraph"
    ) -> str:
        """Format naive RAG response prompt"""
        return self.naive_rag_response.format(
            content_data=content_data,
            response_type=response_type
        )
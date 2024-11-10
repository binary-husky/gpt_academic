from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple
from collections import defaultdict
import re
from enum import Enum, auto


class ExtractionPhase(Enum):
    """Extraction process phases"""
    INITIAL = auto()
    GLEANING = auto()
    VERIFY = auto()


@dataclass
class ExtractionState:
    """State of the extraction process"""
    chunks: Dict[str, dict]
    current_chunk_index: int = 0
    phase: ExtractionPhase = ExtractionPhase.INITIAL
    gleaning_count: int = 0
    extracted_nodes: Dict[str, List[dict]] = field(default_factory=lambda: defaultdict(list))
    extracted_edges: Dict[Tuple[str, str], List[dict]] = field(default_factory=lambda: defaultdict(list))


@dataclass
class PromptInfo:
    """Information about a prompt to be sent to LLM"""
    prompt: str
    prompt_type: str
    chunk_key: str
    history: List[Tuple[str, str]] = field(default_factory=list)


@dataclass
class EntityRelationExtractor:
    """
    Extract entities and their relationships from text chunks.

    This class implements a stateful extraction process that can:
    1. Extract entities and their relationships from text chunks
    2. Support multiple rounds of extraction (gleaning)
    3. External LLM calling for flexibility
    4. Maintain extraction history and state

    Attributes:
        prompt_templates: PromptTemplates instance containing required prompts
        entity_extract_max_gleaning: Maximum number of gleaning iterations
        required_prompts: Set of required prompt templates
    """
    prompt_templates: 'PromptTemplates'
    entity_extract_max_gleaning: int = 1
    required_prompts: Set[str] = field(default_factory=lambda: {
        'entity_extraction',
        'entiti_continue_extraction',
        'entiti_if_loop_extraction'
    })

    def __post_init__(self):
        """Validate prompt templates and initialize state"""
        self._validate_prompts()
        self._state: Optional[ExtractionState] = None

    def _validate_prompts(self) -> None:
        """Validate all required prompts exist in templates"""
        missing_prompts = self.required_prompts - set(dir(self.prompt_templates))
        if missing_prompts:
            raise ValueError(f"Missing required prompt templates: {missing_prompts}")

    def initialize_extraction(self, chunks: Dict[str, dict]) -> List[PromptInfo]:
        """
        Initialize new extraction process for given chunks.

        Args:
            chunks: Dictionary of text chunks to process

        Returns:
            List of prompts to be sent to LLM
        """
        self._state = ExtractionState(chunks=chunks)
        return self._get_next_prompts()

    def _get_next_prompts(self) -> List[PromptInfo]:
        """Generate next batch of prompts based on current state"""
        if not self._state or self._state.current_chunk_index >= len(self._state.chunks):
            return []

        chunk_items = list(self._state.chunks.items())
        chunk_key, chunk_data = chunk_items[self._state.current_chunk_index]

        if self._state.phase == ExtractionPhase.INITIAL:
            return [self._create_initial_prompt(chunk_key, chunk_data)]
        elif self._state.phase == ExtractionPhase.GLEANING:
            return [self._create_gleaning_prompt(chunk_key)]
        elif self._state.phase == ExtractionPhase.VERIFY:
            return [self._create_verify_prompt(chunk_key)]
        return []

    def _create_initial_prompt(self, chunk_key: str, chunk_data: dict) -> PromptInfo:
        """Create initial extraction prompt for a chunk"""
        prompt = self.prompt_templates.format_entity_extraction(
            text=chunk_data['content'],
            entity_types=self.prompt_templates.default_entity_types
        )
        return PromptInfo(
            prompt=prompt,
            prompt_type='initial_extraction',
            chunk_key=chunk_key
        )

    def _create_gleaning_prompt(self, chunk_key: str) -> PromptInfo:
        """Create gleaning prompt for additional extraction"""
        return PromptInfo(
            prompt=self.prompt_templates.entiti_continue_extraction,
            prompt_type='continue_extraction',
            chunk_key=chunk_key
        )

    def _create_verify_prompt(self, chunk_key: str) -> PromptInfo:
        """Create verification prompt"""
        return PromptInfo(
            prompt=self.prompt_templates.entity_if_loop_extraction,
            prompt_type='verify_extraction',
            chunk_key=chunk_key
        )

    def process_response(self, response: str, prompt_info: PromptInfo) -> List[PromptInfo]:
        """
        Process LLM response and determine next steps.

        Args:
            response: LLM response text
            prompt_info: Information about the prompt that generated this response

        Returns:
            List of next prompts to be sent to LLM
        """
        if not self._state:
            raise RuntimeError("Extraction not initialized")

        if prompt_info.prompt_type == 'initial_extraction':
            return self._handle_initial_response(response, prompt_info)
        elif prompt_info.prompt_type == 'continue_extraction':
            return self._handle_gleaning_response(response, prompt_info)
        elif prompt_info.prompt_type == 'verify_extraction':
            return self._handle_verify_response(response, prompt_info)
        return []

    def _handle_initial_response(self, response: str, prompt_info: PromptInfo) -> List[PromptInfo]:
        """Handle response from initial extraction"""
        self._process_extraction_response(response, prompt_info.chunk_key)

        if self.entity_extract_max_gleaning > 0:
            self._state.phase = ExtractionPhase.GLEANING
            return self._get_next_prompts()
        return self._move_to_next_chunk()

    def _handle_gleaning_response(self, response: str, prompt_info: PromptInfo) -> List[PromptInfo]:
        """Handle response from gleaning extraction"""
        self._process_extraction_response(response, prompt_info.chunk_key)
        self._state.gleaning_count += 1

        if self._state.gleaning_count >= self.entity_extract_max_gleaning:
            return self._move_to_next_chunk()

        self._state.phase = ExtractionPhase.VERIFY
        return self._get_next_prompts()

    def _handle_verify_response(self, response: str, prompt_info: PromptInfo) -> List[PromptInfo]:
        """Handle response from verification prompt"""
        if self._clean_str(response).lower() == 'yes':
            self._state.phase = ExtractionPhase.GLEANING
            return self._get_next_prompts()
        return self._move_to_next_chunk()

    def _move_to_next_chunk(self) -> List[PromptInfo]:
        """Move to next chunk and return appropriate prompts"""
        self._state.current_chunk_index += 1
        self._state.phase = ExtractionPhase.INITIAL
        self._state.gleaning_count = 0
        return self._get_next_prompts()

    def _process_extraction_response(self, response: str, chunk_key: str) -> None:
        """Process a single extraction response"""
        records = self._split_into_records(response)

        for record in records:
            record_match = re.search(r'\((.*?)\)', record)
            if not record_match:
                continue

            record_content = record_match.group(1)
            attributes = self._split_record_attributes(record_content)

            if len(attributes) < 1:
                continue

            if attributes[0] == '"entity"':
                entity_data = self._extract_entity(attributes, chunk_key)
                if entity_data:
                    self._state.extracted_nodes[entity_data['entity_name']].append(entity_data)

            elif attributes[0] == '"relationship"':
                relation_data = self._extract_relationship(attributes, chunk_key)
                if relation_data:
                    key = (relation_data['src_id'], relation_data['tgt_id'])
                    self._state.extracted_edges[key].append(relation_data)

    def _split_into_records(self, text: str) -> List[str]:
        """Split response text into individual records"""
        markers = [self.prompt_templates.record_delimiter, self.prompt_templates.completion_delimiter]
        results = re.split("|".join(re.escape(marker) for marker in markers), text)
        return [r.strip() for r in results if r.strip()]


    def _split_record_attributes(self, record: str) -> List[str]:
        """Split record into attributes"""
        return [attr for attr in record.split(self.prompt_templates.tuple_delimiter) if attr.strip()]

    def _extract_entity(self, attributes: List[str], chunk_key: str) -> Optional[dict]:
        """Extract entity data from attributes"""
        if len(attributes) < 4:
            return None

        entity_name = self._clean_str(attributes[1].upper())
        if not entity_name:
            return None

        return {
            'entity_name': entity_name,
            'entity_type': self._clean_str(attributes[2].upper()),
            'description': self._clean_str(attributes[3]),
            'source_id': chunk_key
        }

    def _extract_relationship(self, attributes: List[str], chunk_key: str) -> Optional[dict]:
        """Extract relationship data from attributes"""
        if len(attributes) < 6:
            return None

        return {
            'src_id': self._clean_str(attributes[1].upper()),
            'tgt_id': self._clean_str(attributes[2].upper()),
            'description': self._clean_str(attributes[3]),
            'keywords': self._clean_str(attributes[4]),
            'weight': float(attributes[5]) if self._is_float(attributes[5]) else 1.0,
            'source_id': chunk_key
        }

    @staticmethod
    def _clean_str(s: str) -> str:
        """Clean a string by removing quotes and extra whitespace"""
        return s.strip().strip('"').strip("'")

    @staticmethod
    def _is_float(s: str) -> bool:
        """Check if string can be converted to float"""
        try:
            float(s.strip().strip('"').strip("'"))
            return True
        except ValueError:
            return False

    def get_results(self) -> Tuple[Dict[str, List[dict]], Dict[Tuple[str, str], List[dict]]]:
        """Get the final extracted nodes and edges"""
        if not self._state:
            return defaultdict(list), defaultdict(list)
        return self._state.extracted_nodes, self._state.extracted_edges
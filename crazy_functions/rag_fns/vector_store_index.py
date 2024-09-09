from llama_index.core import VectorStoreIndex
from typing import Any,  List, Optional

from llama_index.core.callbacks.base import CallbackManager
from llama_index.core.schema import TransformComponent
from llama_index.core.service_context import ServiceContext
from llama_index.core.settings import (
    Settings,
    callback_manager_from_settings_or_context,
    transformations_from_settings_or_context,
)
from llama_index.core.storage.storage_context import StorageContext


class GptacVectorStoreIndex(VectorStoreIndex):
    
    @classmethod
    def default_vector_store(
        cls,
        storage_context: Optional[StorageContext] = None,
        show_progress: bool = False,
        callback_manager: Optional[CallbackManager] = None,
        transformations: Optional[List[TransformComponent]] = None,
        # deprecated
        service_context: Optional[ServiceContext] = None,
        embed_model = None,
        **kwargs: Any,
    ):
        """Create index from documents.

        Args:
            documents (Optional[Sequence[BaseDocument]]): List of documents to
                build the index from.

        """
        storage_context = storage_context or StorageContext.from_defaults()
        docstore = storage_context.docstore
        callback_manager = (
            callback_manager
            or callback_manager_from_settings_or_context(Settings, service_context)
        )
        transformations = transformations or transformations_from_settings_or_context(
            Settings, service_context
        )

        with callback_manager.as_trace("index_construction"):

            return cls(
                nodes=[],
                storage_context=storage_context,
                callback_manager=callback_manager,
                show_progress=show_progress,
                transformations=transformations,
                service_context=service_context,
                embed_model=embed_model,
                **kwargs,
            )


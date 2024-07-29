import datetime
from typing import Optional, Union, Tuple, Any, Iterator, Sequence, Callable
from uuid import UUID

import requests
from urllib3 import Retry

from langsmith import Client as LangSmithClient

from langchain_core.document_loaders.base import BaseLoader
from langchain_core.documents import Document


class LangSmithLoader(BaseLoader):
    """Load LangSmith Dataset examples as Documents.

    Example:
        .. code-block:: python

            from langchain_core.document_loaders import LangSmithLoader

            loader = LangSmithLoader(dataset_id="...", limit=100)
            docs = []
            for doc in loader.lazy_load():
                docs.append(doc)

    """

    def __init__(
            self,
            *,
            client: Optional[LangSmithClient] = None,
            api_url: Optional[str] = None,
            api_key: Optional[str] = None,
            retry_config: Optional[Retry] = None,
            timeout_ms: Optional[Union[int, Tuple[int, int]]] = None,
            session: Optional[requests.Session] = None,
            content_key: Optional[str] = None,
            format_content: Optional[Callable[..., str]]=None,
            **list_examples_params: Any
    ) -> None:
        """Init loader.

        Args:
            ...
        """
        if not client:
            client = LangSmithClient(
                api_url,
                api_key=api_key,
                retry_config=retry_config,
                timeout_ms=timeout_ms,
                session=session,
            )
        self._client = client
        self._list_examples_params = list_examples_params
        self._content_key = list(content_key.split(".")) if content_key else []
        self._format_content = format_content

    def lazy_load(self) -> Iterator[Document]:
        for example in self._client.list_examples(
            **self._list_examples_params
        ):
            content = example.inputs
            for key in self._content_key:
                content = content[key]
            if self._format_content:
                content = self._format_content(content)
            yield Document(content, metadata=example.dict())
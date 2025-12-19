from collections import defaultdict
from typing import Dict

from test_processing_ir.inverted_index import InvertedIndex
from test_processing_ir.text_processor import TextProcessor


class Indexer:
    """
   the full indexing process:
    - Text acquisition
    - Text transformation
    - Index creation
    """

    def __init__(self) -> None:
        self.processor = TextProcessor()
        self.index = InvertedIndex()
        self.documents: Dict[int, str] = {}

    def add_document(self, doc_id: int, text: str) -> None:
        """
        Text acquisition step.
        Stores raw documents.
        """
        self.documents[doc_id] = text


    def build_index(self) -> None:
        """
        Runs transformation and index creation.
        """
        for doc_id, text in self.documents.items():
            terms = self.processor.process(text)
            self.index.add_document(doc_id, terms)

    def search(self, query: str) -> Dict[int, int]:
        """
        Simple term-based search.
        """
        processed_terms = self.processor.process(query)
        results = defaultdict(int)

        for term in processed_terms:
            postings = self.index.search(term)
            for doc_id, freq in postings.items():
                results[doc_id] += freq

        return dict(sorted(results.items(), key=lambda x: x[1], reverse=True))

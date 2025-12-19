from collections import defaultdict
from typing import List, Dict


class InvertedIndex:
    """
   inverted index.
    """

    def __init__(self) -> None:
        """Creates an empty inverted index."""
        self.index: Dict[str, Dict[int, int]] = defaultdict(dict)

    def add_document(self, doc_id: int, terms: List[str]) -> None:
        """
        Adds a document's terms to the index.
        """
        term_frequency = defaultdict(int)

        for term in terms:
            term_frequency[term] += 1


        for term, freq in term_frequency.items():
            self.index[term][doc_id] = freq

    def search(self, term: str) -> Dict[int, int]:
        """
        Returns documents containing the term.
        """
        return self.index.get(term, {})

    def __repr__(self) -> str:
        return f"InvertedIndex(size={len(self.index)})"

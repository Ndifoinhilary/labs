import re
from typing import List


def stem(token: str) -> str:
    """Stemming function"""
    suffixes = ["ing", "ly", "ed", "s", "es", "er", "est"]

    for suffix in suffixes:
        if token.endswith(suffix) and len(token) > len(suffix) + 2:
            return token[:-len(suffix)]

    return token


class TextProcessor:
    """
        Handles text transformation:
        - Tokenization
        - Normalization
        - Stop-word removal
        - Stemming (simple implementation)
        """

    STOP_WORDS = {
        "is", "the", "of", "and", "to", "in", "a", "that", "for", "with", "this", "on", "as", "by", "an"
    }

    def __init__(self):
        self.token_pattern = re.compile(r"[a-zA-Z]+")

    def tokenize(self, text: str) -> List[str]:
        """Tokenizes a text into a list of words"""
        return self.token_pattern.findall(text.lower())

    def remove_stop_words(self, tokens: List[str]) -> List[str]:
        """Removes stop words from a list of tokens"""
        return [token for token in tokens if token not in self.STOP_WORDS]

    def process(self, text: str) -> List[str]:
        """
        Full transformation.
        """
        tokens = self.tokenize(text)
        tokens = self.remove_stop_words(tokens)
        return [stem(token) for token in tokens]

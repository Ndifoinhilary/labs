from indexer import Indexer


def main() -> None:
    """
    Main
    """

    indexer = Indexer()

    # -------------------------
    # Text Acquisition
    # -------------------------
    indexer.add_document(1, "Information retrieval is important for fast search")
    indexer.add_document(2, "Retrieval of information should be efficient")
    indexer.add_document(3, "Search engines use inverted index for retrieval")

    # -------------------------
    # Build Index
    # -------------------------
    indexer.build_index()

    # -------------------------
    # Search
    # -------------------------
    query = "information retrieval"
    results = indexer.search(query)

    for doc_id, score in results.items():
        print(f"Doc {doc_id} (score={score}): {indexer.documents[doc_id]}")


if __name__ == "__main__":
    main()

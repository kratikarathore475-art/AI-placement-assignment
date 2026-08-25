def split_text(text, chunk_size=500, chunk_overlap=50):
    """
    Split text into smaller chunks.

    Args:
        text (str): The complete document text.
        chunk_size (int): Maximum size of each chunk.
        chunk_overlap (int): Number of overlapping characters.

    Returns:
        list: List of text chunks.
    """

    chunks = []

    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size

        chunk = text[start:end]

        chunks.append(chunk)

        start = end - chunk_overlap

    return chunks













  
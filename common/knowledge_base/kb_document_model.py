from langchain.docstore.document import Document


class DocumentWithVSId(Document):
    """
    矢量化后的文档
    """
    id: str = None
    score: float = 3.0

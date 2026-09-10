from sqlalchemy import String, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import BaseClass

class Chunk(BaseClass):
    __tablename__ = "chunks"

    chunk_id: Mapped[int] = mapped_column(primary_key=True)
    doc_id: Mapped[str] = mapped_column(String(100), ForeignKey("documents.doc_id"))
    page: Mapped[int] = mapped_column()
    text: Mapped[str] = mapped_column(Text)
    char_start: Mapped[int] = mapped_column()
    char_end: Mapped[int] = mapped_column()

    document: Mapped["Document"] = relationship(back_populates="chunks")

class Document(BaseClass):
    __tablename__ = "documents"

    doc_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    title: Mapped[str] = mapped_column(String(255))

    chunks: Mapped[list["Chunk"]] = relationship(back_populates="document")
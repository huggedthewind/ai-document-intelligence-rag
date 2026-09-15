from sqlalchemy import String, ForeignKey, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

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

class Query(BaseClass):
    __tablename__ = "queries"

    query_id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(Text)
    doc_id: Mapped[str | None] = mapped_column(String(100), ForeignKey("documents.doc_id"))
    top_k: Mapped[int] = mapped_column(default=5)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    answers: Mapped[list["Answer"]] = relationship(back_populates="query")

class Answer(BaseClass):
    __tablename__ = "answers"

    answer_id: Mapped[int] = mapped_column(primary_key=True)
    query_id: Mapped[int] = mapped_column(ForeignKey("queries.query_id"))
    text: Mapped[str] = mapped_column(Text)

    query: Mapped["Query"] = relationship(back_populates="answers")
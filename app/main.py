from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import Document
from app.schemas import DocumentCreate, DocumentResponse
from app.embeddings import encode, embedding_to_json

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Semantic Document Search")


@app.post("/documents", response_model=DocumentResponse, status_code=201)
def create_document(payload: DocumentCreate, db: Session = Depends(get_db)):
    vector = encode(payload.content)

    document = Document(
        title=payload.title,
        content=payload.content,
        embedding=embedding_to_json(vector),
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return document
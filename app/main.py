from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import Document
from app.schemas import DocumentCreate, DocumentResponse, DocumentSearchResult
from app.search import rank_documents
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

@app.get("/documents/search", response_model=list[DocumentSearchResult])
def search_documents(q: str, top_k: int = 5, db: Session = Depends(get_db)):
    if not q.strip():
        raise HTTPException(status_code=422, detail="Query parameter 'q' cannot be empty")

    query_vector = encode(q)
    documents = db.query(Document).all()

    ranked = rank_documents(query_vector, documents, top_k=top_k)

    results = []
    for doc, score in ranked:
        results.append(
            DocumentSearchResult(
                id=doc.id,
                title=doc.title,
                content=doc.content,
                score=score,
            )
        )

    return results

@app.delete("/documents/{document_id}", status_code=204)
def delete_document(document_id: int, db: Session = Depends(get_db)):
    # document = db.query(Document).filter(Document.id == document_id).first()
    document = db.get(Document, document_id)

    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    db.delete(document)
    db.commit()
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Donation, Ngo

app = FastAPI(title="FoodRescueAI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "FoodRescueAI backend running"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
                response["connection_status"] = "Connected"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "❌ Not Available"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"
    return response


# Utility to convert Mongo _id to string

def serialize(doc):
    if not doc:
        return doc
    d = dict(doc)
    if "_id" in d:
        d["_id"] = str(d["_id"])  # keep as _id for transparency
    return d


# Donation endpoints
@app.post("/donations")
def create_donation(payload: Donation):
    try:
        inserted_id = create_document("donation", payload)
        return {"_id": inserted_id, **payload.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/donations")
def list_donations() -> List[dict]:
    try:
        docs = get_documents("donation", {}, limit=100)
        return [serialize(doc) for doc in docs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# NGO endpoints
@app.post("/ngos")
def create_ngo(payload: Ngo):
    try:
        inserted_id = create_document("ngo", payload)
        return {"_id": inserted_id, **payload.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/ngos")
def list_ngos() -> List[dict]:
    try:
        docs = get_documents("ngo", {}, limit=100)
        return [serialize(doc) for doc in docs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

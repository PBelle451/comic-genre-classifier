"""
Serviço FastAPI que expõe o classificador de gênero de quadrinhos treinado.

Rodar localmente:
    uvicorn api:app --reload --port 8000   (execute de dentro de src/comic_classifier)
"""

import json
from contextlib import asynccontextmanager
from pathlib import Path

import torch
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

from model import ComicRNNClassifier
from preprocessing import tokenize, encode

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
MODELS_DIR = PROJECT_ROOT / "models"
STATIC_DIR = Path(__file__).resolve().parent / "static"

_state: dict = {}


def load_artifacts() -> None:
    vocab = json.loads((PROCESSED_DIR / "vocab.json").read_text(encoding="utf-8"))
    meta = json.loads((PROCESSED_DIR / "meta.json").read_text(encoding="utf-8"))
    checkpoint = torch.load(MODELS_DIR / "best_model.pt", map_location="cpu", weights_only=True)

    model = ComicRNNClassifier(**checkpoint["hyperparams"])
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    id2label = {v: k for k, v in checkpoint["label2id"].items()}
    _state.update(vocab=vocab, meta=meta, model=model, id2label=id2label)


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_artifacts()
    yield
    _state.clear()


app = FastAPI(title="Comic Genre Classifier", version="1.0", lifespan=lifespan)


class TextInput(BaseModel):
    text: str


class PredictionResponse(BaseModel):
    label: str
    confidence: float
    probabilities: dict[str, float]


@app.get("/", include_in_schema=False)
def root():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": "model" in _state}


@app.post("/predict", response_model=PredictionResponse)
def predict(payload: TextInput) -> PredictionResponse:
    tokens = tokenize(payload.text)
    ids = encode(tokens, _state["vocab"], _state["meta"]["max_len"])
    input_tensor = torch.tensor([ids], dtype=torch.long)

    with torch.no_grad():
        logits = _state["model"](input_tensor)
        probs = torch.softmax(logits, dim=1)[0]

    id2label = _state["id2label"]
    probabilities = {id2label[i]: round(probs[i].item(), 4) for i in range(len(id2label))}
    best_idx = int(probs.argmax())

    return PredictionResponse(
        label=id2label[best_idx],
        confidence=round(probs[best_idx].item(), 4),
        probabilities=probabilities,
    )
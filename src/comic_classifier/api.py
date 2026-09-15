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

_state: dict = {}  # "cache" global em memória: modelo e artefatos carregados uma vez só


def load_artifacts() -> None:
    """Carrega tudo que a API precisa para prever: vocabulário, max_len e o
    modelo treinado (com os MESMOS hiperparâmetros salvos no checkpoint —
    por isso o treino grava "hyperparams" junto com os pesos)."""
    vocab = json.loads((PROCESSED_DIR / "vocab.json").read_text(encoding="utf-8"))
    meta = json.loads((PROCESSED_DIR / "meta.json").read_text(encoding="utf-8"))
    checkpoint = torch.load(MODELS_DIR / "best_model.pt", map_location="cpu", weights_only=True)

    model = ComicRNNClassifier(**checkpoint["hyperparams"])  # reconstrói a arquitetura...
    model.load_state_dict(checkpoint["model_state_dict"])  # ...e carrega os pesos treinados nela
    model.eval()  # modo avaliação: desliga dropout (queremos previsões estáveis, não aleatórias)

    id2label = {v: k for k, v in checkpoint["label2id"].items()}  # inverte {"terror": 3} -> {3: "terror"}
    _state.update(vocab=vocab, meta=meta, model=model, id2label=id2label)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Roda uma vez quando o servidor sobe (antes do `yield`) e uma vez quando
    desliga (depois do `yield`). Carregar o modelo aqui — e não dentro de
    cada requisição — evita reabrir o arquivo e reconstruir a rede a cada
    chamada de /predict, que seria bem mais lento."""
    load_artifacts()
    yield
    _state.clear()


app = FastAPI(title="Comic Genre Classifier", version="1.0", lifespan=lifespan)


class TextInput(BaseModel):
    """Formato esperado no corpo (JSON) do POST /predict: {"text": "..."}.
    O Pydantic valida automaticamente — se faltar "text" ou vier com tipo
    errado, o FastAPI já devolve um erro 422 antes de chegar na função."""
    text: str


class PredictionResponse(BaseModel):
    """Formato da resposta — também documentado sozinho na página /docs
    graças a essas anotações de tipo."""
    label: str
    confidence: float
    probabilities: dict[str, float]


@app.get("/", include_in_schema=False)
def root():
    """Serve a página HTML de teste (static/index.html) na raiz do site."""
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
def health():
    """Endpoint simples pra verificar se o serviço está de pé e o modelo
    carregado — útil para checagens automáticas (Docker healthcheck, etc.)."""
    return {"status": "ok", "model_loaded": "model" in _state}


@app.post("/predict", response_model=PredictionResponse)
def predict(payload: TextInput) -> PredictionResponse:
    # Mesmo pipeline de tokenização/codificação usado no treino — crucial
    # usar as MESMAS funções, senão o modelo recebe um formato diferente do
    # que aprendeu.
    tokens = tokenize(payload.text)
    ids = encode(tokens, _state["vocab"], _state["meta"]["max_len"])
    input_tensor = torch.tensor([ids], dtype=torch.long)  # [ids] = batch de tamanho 1

    with torch.no_grad():  # sem gradientes, só inferência
        logits = _state["model"](input_tensor)
        probs = torch.softmax(logits, dim=1)[0]  # logits -> probabilidades que somam 1

    id2label = _state["id2label"]
    probabilities = {id2label[i]: round(probs[i].item(), 4) for i in range(len(id2label))}
    best_idx = int(probs.argmax())  # índice da maior probabilidade

    return PredictionResponse(
        label=id2label[best_idx],
        confidence=round(probs[best_idx].item(), 4),
        probabilities=probabilities,
    )
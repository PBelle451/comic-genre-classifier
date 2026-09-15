"""
Arquitetura do classificador: Embedding treinado do zero + RNN (GRU ou LSTM,
bidirecional) + camada densa final. Usa pack_padded_sequence para ignorar o
padding durante a passagem pela rede recorrente.
"""

import json

import torch
import torch.nn as nn
from torch.nn.utils.rnn import pack_padded_sequence


class ComicRNNClassifier(nn.Module):
    def __init__(
        self,
        vocab_size: int,
        num_classes: int,
        embed_dim: int = 100,
        hidden_dim: int = 64,
        num_layers: int = 1,
        bidirectional: bool = True,
        dropout: float = 0.3,
        rnn_type: str = "gru",
        pad_idx: int = 0,
    ):
        super().__init__()
        self.pad_idx = pad_idx
        self.rnn_type = rnn_type.lower()
        self.bidirectional = bidirectional

        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=pad_idx)

        rnn_cls = nn.GRU if self.rnn_type == "gru" else nn.LSTM
        self.rnn = rnn_cls(
            input_size=embed_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=bidirectional,
            dropout=dropout if num_layers > 1 else 0.0,
        )

        num_directions = 2 if bidirectional else 1
        self.dropout = nn.Dropout(dropout)
        self.fc = nn.Linear(hidden_dim * num_directions, num_classes)

    def forward(self, input_ids: torch.Tensor) -> torch.Tensor:
        # Comprimento real de cada sequência (ignora o padding)
        lengths = (input_ids != self.pad_idx).sum(dim=1).clamp(min=1).cpu()

        embedded = self.embedding(input_ids)
        packed = pack_padded_sequence(embedded, lengths, batch_first=True, enforce_sorted=False)
        _, hidden = self.rnn(packed)

        if self.rnn_type == "lstm":
            hidden = hidden[0]  # (h_n, c_n) -> usa só h_n

        if self.bidirectional:
            # últimas camadas: [-2]=forward, [-1]=backward
            final = torch.cat([hidden[-2], hidden[-1]], dim=1)
        else:
            final = hidden[-1]

        return self.fc(self.dropout(final))


def build_model_from_artifacts(processed_dir, **overrides) -> ComicRNNClassifier:
    """Instancia o modelo lendo vocab_size e num_classes dos artefatos da etapa 3."""
    meta = json.loads((processed_dir / "meta.json").read_text(encoding="utf-8"))
    label2id = json.loads((processed_dir / "label2id.json").read_text(encoding="utf-8"))
    params = dict(vocab_size=meta["vocab_size"], num_classes=len(label2id))
    params.update(overrides)
    return ComicRNNClassifier(**params)


if __name__ == "__main__":
    from pathlib import Path
    import numpy as np

    processed_dir = Path(__file__).resolve().parents[2] / "data" / "processed"
    model = build_model_from_artifacts(processed_dir, rnn_type="gru")
    print(model)

    n_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"\nParâmetros treináveis: {n_params:,}")

    # Sanity check: passa um batch real de treino pela rede
    train = np.load(processed_dir / "train.npz")
    batch = torch.from_numpy(train["input_ids"][:8])
    logits = model(batch)
    print(f"\nInput shape:  {tuple(batch.shape)}")
    print(f"Output shape: {tuple(logits.shape)}  (esperado: [8, num_classes])")
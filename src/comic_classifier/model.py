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
    """Embedding (treinado do zero) -> RNN (GRU ou LSTM) -> camada densa.

    Fluxo de shapes, com batch_size=B, max_len=L, embed_dim=E, hidden_dim=H:
      input_ids  (B, L)               -- IDs inteiros de palavras
      embedded   (B, L, E)            -- cada ID vira um vetor de E números
      hidden     (camadas*direções, B, H) -- "resumo" da sequência inteira
      final      (B, H) ou (B, 2H)    -- se bidirecional, concatena as 2 direções
      logits     (B, num_classes)     -- pontuação de cada gênero (antes do softmax)
    """

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

        # Embedding: uma "tabela" (vocab_size x embed_dim) onde cada linha é o
        # vetor que representa uma palavra. Começa aleatório e é ajustado
        # durante o treino, junto com o resto da rede (não usamos embeddings
        # pré-treinados tipo GloVe/Word2Vec aqui). padding_idx=0 congela o
        # vetor do <PAD> em zero, já que ele não carrega informação real.
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=pad_idx)

        # GRU e LSTM são dois "sabores" de rede recorrente — processam a frase
        # palavra por palavra, mantendo uma memória (hidden state) do que já
        # leram. GRU é mais simples/leve; LSTM tem uma memória extra (cell
        # state) e costuma ajudar em sequências mais longas.
        rnn_cls = nn.GRU if self.rnn_type == "gru" else nn.LSTM
        self.rnn = rnn_cls(
            input_size=embed_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,  # espera tensores (batch, seq, features), não (seq, batch, features)
            bidirectional=bidirectional,  # lê a frase da esquerda->direita E direita->esquerda
            dropout=dropout if num_layers > 1 else 0.0,  # só tem efeito com 2+ camadas
        )

        # Se bidirecional, a saída da RNN tem o dobro do tamanho (forward +
        # backward concatenados), por isso hidden_dim * num_directions aqui.
        num_directions = 2 if bidirectional else 1
        self.dropout = nn.Dropout(dropout)  # zera neurônios aleatoriamente no treino, combate overfitting
        self.fc = nn.Linear(hidden_dim * num_directions, num_classes)  # camada final: "resumo" -> 4 notas de gênero

    def forward(self, input_ids: torch.Tensor) -> torch.Tensor:
        # Cada frase foi preenchida (padding) até max_len, mas o padding não
        # é uma palavra de verdade — contamos só os tokens != <PAD> para saber
        # o comprimento REAL de cada frase no batch.
        lengths = (input_ids != self.pad_idx).sum(dim=1).clamp(min=1).cpu()

        embedded = self.embedding(input_ids)  # (B, L) -> (B, L, E)

        # pack_padded_sequence "empacota" o batch de um jeito que a RNN
        # processa só os tokens reais de cada frase, pulando o padding —
        # sem isso, a rede perderia tempo (e aprenderia ruído) processando
        # um monte de <PAD> no final das frases mais curtas.
        # enforce_sorted=False: não precisamos ordenar o batch por tamanho manualmente.
        packed = pack_padded_sequence(embedded, lengths, batch_first=True, enforce_sorted=False)
        _, hidden = self.rnn(packed)  # só nos interessa o hidden state final, não a saída passo-a-passo

        if self.rnn_type == "lstm":
            hidden = hidden[0]  # LSTM devolve (h_n, c_n); GRU devolve só h_n -> padroniza aqui

        # hidden tem shape (num_layers * num_directions, B, hidden_dim).
        # Com 1 camada bidirecional, isso é (2, B, H): índice -2 = última
        # camada lendo da esquerda pra direita, índice -1 = direita pra esquerda.
        if self.bidirectional:
            final = torch.cat([hidden[-2], hidden[-1]], dim=1)  # (B, H) + (B, H) -> (B, 2H)
        else:
            final = hidden[-1]  # (B, H)

        return self.fc(self.dropout(final))  # (B, 2H ou H) -> (B, num_classes)


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
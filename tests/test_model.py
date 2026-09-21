"""Testes da arquitetura ComicRNNClassifier — checam formatos de tensor,
não a qualidade das previsões (isso é papel da avaliação em train.py)."""

import torch

from model import ComicRNNClassifier


def test_forward_output_shape_gru_bidirectional():
    model = ComicRNNClassifier(
        vocab_size=50, num_classes=4, embed_dim=16, hidden_dim=8, rnn_type="gru", bidirectional=True
    )
    batch = torch.randint(1, 50, (5, 10))  # 5 frases, 10 tokens cada
    logits = model(batch)
    assert logits.shape == (5, 4)


def test_forward_output_shape_lstm_unidirectional():
    model = ComicRNNClassifier(
        vocab_size=50, num_classes=4, embed_dim=16, hidden_dim=8, rnn_type="lstm", bidirectional=False
    )
    batch = torch.randint(1, 50, (3, 7))
    logits = model(batch)
    assert logits.shape == (3, 4)


def test_padding_idx_embedding_is_zero_vector():
    model = ComicRNNClassifier(vocab_size=20, num_classes=4, embed_dim=8, pad_idx=0)
    assert torch.all(model.embedding.weight[0] == 0)


def test_forward_handles_sequences_with_padding():
    model = ComicRNNClassifier(vocab_size=50, num_classes=4, embed_dim=16, hidden_dim=8)
    batch = torch.zeros((2, 6), dtype=torch.long)
    batch[0, :3] = torch.tensor([5, 6, 7])  # frase "curta": 3 tokens + 3 de padding
    batch[1, :6] = torch.tensor([5, 6, 7, 8, 9, 10])  # frase "longa": preenche tudo
    logits = model(batch)
    assert logits.shape == (2, 4)


def test_forward_raises_on_all_padding_sequence_is_handled_gracefully():
    # Uma sequência 100% padding (comprimento 0) não deve quebrar o forward —
    # o clamp(min=1) em forward() garante um comprimento mínimo de 1.
    model = ComicRNNClassifier(vocab_size=20, num_classes=4, embed_dim=8, hidden_dim=8)
    batch = torch.zeros((1, 5), dtype=torch.long)
    logits = model(batch)
    assert logits.shape == (1, 4)
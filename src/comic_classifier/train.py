"""
Treina o ComicRNNClassifier nos dados pré-processados, com early stopping
baseado na perda de validação, e avalia o melhor checkpoint no conjunto de
teste (classification report + matriz de confusão).
"""

import argparse
import json
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.metrics import classification_report, confusion_matrix

from model import ComicRNNClassifier

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
MODELS_DIR = PROJECT_ROOT / "models"


def load_split(name: str) -> TensorDataset:
    data = np.load(PROCESSED_DIR / f"{name}.npz")
    input_ids = torch.from_numpy(data["input_ids"]).long()
    labels = torch.from_numpy(data["labels"]).long()
    return TensorDataset(input_ids, labels)


def run_epoch(model, loader, criterion, optimizer=None) -> tuple[float, float]:
    is_train = optimizer is not None
    model.train(is_train)
    total_loss, correct, total = 0.0, 0, 0

    for input_ids, labels in loader:
        if is_train:
            optimizer.zero_grad()
        with torch.set_grad_enabled(is_train):
            logits = model(input_ids)
            loss = criterion(logits, labels)
            if is_train:
                loss.backward()
                optimizer.step()

        total_loss += loss.item() * len(labels)
        correct += (logits.argmax(dim=1) == labels).sum().item()
        total += len(labels)

    return total_loss / total, correct / total


def main():
    parser = argparse.ArgumentParser(description="Treina o classificador de gênero de quadrinhos")
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--patience", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--embed-dim", type=int, default=100)
    parser.add_argument("--hidden-dim", type=int, default=64)
    parser.add_argument("--rnn-type", choices=["gru", "lstm"], default="gru")
    parser.add_argument("--no-bidirectional", action="store_true")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    torch.manual_seed(args.seed)

    meta = json.loads((PROCESSED_DIR / "meta.json").read_text())
    label2id = json.loads((PROCESSED_DIR / "label2id.json").read_text())
    id2label = {v: k for k, v in label2id.items()}

    train_loader = DataLoader(load_split("train"), batch_size=args.batch_size, shuffle=True)
    val_loader = DataLoader(load_split("val"), batch_size=args.batch_size)
    test_loader = DataLoader(load_split("test"), batch_size=args.batch_size)

    model = ComicRNNClassifier(
        vocab_size=meta["vocab_size"],
        num_classes=len(label2id),
        embed_dim=args.embed_dim,
        hidden_dim=args.hidden_dim,
        rnn_type=args.rnn_type,
        bidirectional=not args.no_bidirectional,
    )

    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    best_val_loss = float("inf")
    epochs_without_improvement = 0

    for epoch in range(1, args.epochs + 1):
        train_loss, train_acc = run_epoch(model, train_loader, criterion, optimizer)
        val_loss, val_acc = run_epoch(model, val_loader, criterion)

        print(
            f"Época {epoch:02d} | treino: loss={train_loss:.4f} acc={train_acc:.3f} "
            f"| validação: loss={val_loss:.4f} acc={val_acc:.3f}"
        )

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            epochs_without_improvement = 0
            torch.save(
                {
                    "model_state_dict": model.state_dict(),
                    "hyperparams": {
                        "vocab_size": meta["vocab_size"],
                        "num_classes": len(label2id),
                        "embed_dim": args.embed_dim,
                        "hidden_dim": args.hidden_dim,
                        "rnn_type": args.rnn_type,
                        "bidirectional": not args.no_bidirectional,
                    },
                    "label2id": label2id,
                },
                MODELS_DIR / "best_model.pt",
            )
        else:
            epochs_without_improvement += 1
            if epochs_without_improvement >= args.patience:
                print(f"\nEarly stopping na época {epoch} (sem melhora por {args.patience} épocas).")
                break

    # Avaliação final no conjunto de teste, com o melhor checkpoint
    checkpoint = torch.load(MODELS_DIR / "best_model.pt", weights_only=True)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    all_preds, all_labels = [], []
    with torch.no_grad():
        for input_ids, labels in test_loader:
            preds = model(input_ids).argmax(dim=1)
            all_preds.extend(preds.tolist())
            all_labels.extend(labels.tolist())

    target_names = [id2label[i] for i in range(len(id2label))]
    print("\n=== Avaliação no conjunto de teste ===")
    print(classification_report(all_labels, all_preds, target_names=target_names))
    print("Matriz de confusão (linhas=real, colunas=previsto):")
    print(target_names)
    print(confusion_matrix(all_labels, all_preds))
    print(f"\nMelhor checkpoint salvo em: {MODELS_DIR / 'best_model.pt'}")


if __name__ == "__main__":
    main()
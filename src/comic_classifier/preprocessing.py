"""
Pré-processa o dataset sintético de quadrinhos:
  1. Tokeniza o texto (minúsculas, mantém acentuação, remove pontuação).
  2. Faz o split estratificado em treino/validação/teste.
  3. Constrói o vocabulário a partir APENAS do split de treino (evita data leakage).
  4. Codifica as sequências (word -> índice) com padding/truncamento em max_len.
  5. Salva vocab.json, label2id.json, meta.json e os splits codificados (.npz).
"""

import argparse
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

PAD_TOKEN, UNK_TOKEN = "<PAD>", "<UNK>"
TOKEN_RE = re.compile(r"[a-zà-öø-ÿ0-9]+", re.IGNORECASE)

# Raiz do projeto = duas pastas acima deste arquivo (src/comic_classifier/preprocessing.py)
PROJECT_ROOT = Path(__file__).resolve().parents[2]


def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())


def build_vocab(token_lists: list[list[str]], min_freq: int = 1) -> dict[str, int]:
    freq: dict[str, int] = {}
    for tokens in token_lists:
        for tok in tokens:
            freq[tok] = freq.get(tok, 0) + 1
    vocab = {PAD_TOKEN: 0, UNK_TOKEN: 1}
    for word, count in sorted(freq.items(), key=lambda kv: (-kv[1], kv[0])):
        if count >= min_freq:
            vocab[word] = len(vocab)
    return vocab


def encode(tokens: list[str], vocab: dict[str, int], max_len: int) -> list[int]:
    ids = [vocab.get(tok, vocab[UNK_TOKEN]) for tok in tokens[:max_len]]
    ids += [vocab[PAD_TOKEN]] * (max_len - len(ids))
    return ids


def split_dataset(df: pd.DataFrame, val_size: float, test_size: float, seed: int):
    train_df, temp_df = train_test_split(
        df, test_size=val_size + test_size, stratify=df["label"], random_state=seed
    )
    relative_test = test_size / (val_size + test_size)
    val_df, test_df = train_test_split(
        temp_df, test_size=relative_test, stratify=temp_df["label"], random_state=seed
    )
    return train_df.reset_index(drop=True), val_df.reset_index(drop=True), test_df.reset_index(drop=True)


def encode_split(df: pd.DataFrame, vocab: dict[str, int], label2id: dict[str, int], max_len: int):
    input_ids = np.array(
        [encode(tokenize(t), vocab, max_len) for t in df["text"]], dtype=np.int64
    )
    labels = np.array([label2id[l] for l in df["label"]], dtype=np.int64)
    return input_ids, labels


def main():
    parser = argparse.ArgumentParser(description="Pré-processa o dataset de quadrinhos")
    parser.add_argument("--input", type=Path, default=PROJECT_ROOT / "data" / "raw" / "comics_synthetic.csv")
    parser.add_argument("--output-dir", type=Path, default=PROJECT_ROOT / "data" / "processed")
    parser.add_argument("--min-freq", type=int, default=1)
    parser.add_argument("--val-size", type=float, default=0.15)
    parser.add_argument("--test-size", type=float, default=0.15)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    train_df, val_df, test_df = split_dataset(df, args.val_size, args.test_size, args.seed)

    train_tokens = [tokenize(t) for t in train_df["text"]]
    vocab = build_vocab(train_tokens, min_freq=args.min_freq)

    max_len = max(len(tokenize(t)) for t in df["text"])

    labels_sorted = sorted(df["label"].unique())
    label2id = {label: i for i, label in enumerate(labels_sorted)}

    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name, split_df in [("train", train_df), ("val", val_df), ("test", test_df)]:
        input_ids, labels = encode_split(split_df, vocab, label2id, max_len)
        np.savez(args.output_dir / f"{name}.npz", input_ids=input_ids, labels=labels)

    (args.output_dir / "vocab.json").write_text(json.dumps(vocab, ensure_ascii=False, indent=2))
    (args.output_dir / "label2id.json").write_text(json.dumps(label2id, ensure_ascii=False, indent=2))
    (args.output_dir / "meta.json").write_text(
        json.dumps({"max_len": max_len, "vocab_size": len(vocab)}, indent=2)
    )

    print(f"Vocabulário: {len(vocab)} tokens | max_len: {max_len}")
    print(f"Treino: {len(train_df)} | Validação: {len(val_df)} | Teste: {len(test_df)}")
    print("Distribuição de treino por classe:")
    print(train_df["label"].value_counts())


if __name__ == "__main__":
    main()
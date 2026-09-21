"""Testes da geração do dataset sintético."""

import random

from data_generation import GENRES, generate_dataset, generate_sample


def test_generate_sample_returns_nonempty_string():
    rng = random.Random(0)
    text = generate_sample("terror", rng)
    assert isinstance(text, str)
    assert len(text) > 0


def test_generate_sample_is_deterministic_given_same_seed():
    text_a = generate_sample("terror", random.Random(42))
    text_b = generate_sample("terror", random.Random(42))
    assert text_a == text_b


def test_generate_dataset_has_expected_size():
    df = generate_dataset(samples_per_class=10, seed=1, overlap_prob=0.0)
    assert len(df) == 10 * len(GENRES)


def test_generate_dataset_is_balanced_across_genres():
    df = generate_dataset(samples_per_class=15, seed=2, overlap_prob=0.0)
    counts = df["label"].value_counts()
    assert all(counts[genre] == 15 for genre in GENRES)


def test_generate_dataset_has_no_duplicate_text_within_a_genre():
    df = generate_dataset(samples_per_class=20, seed=3, overlap_prob=0.0)
    for genre in GENRES:
        texts = df.loc[df["label"] == genre, "text"]
        assert texts.is_unique


def test_generate_dataset_same_seed_is_reproducible():
    df_a = generate_dataset(samples_per_class=5, seed=7, overlap_prob=0.3)
    df_b = generate_dataset(samples_per_class=5, seed=7, overlap_prob=0.3)
    assert df_a.equals(df_b)
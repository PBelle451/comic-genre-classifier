"""Testes da geração do dataset sintético."""

import random
import re

from data_generation import (
    GENRES,
    TEMPLATES_EN,
    VOCAB_EN,
    generate_dataset,
    generate_sample,
)


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


# ---------------------------------------------------------------------------
# Multilíngue (português + inglês)
# ---------------------------------------------------------------------------

def _english_allowed_words() -> set[str]:
    """Todas as palavras que PODEM aparecer numa frase em inglês: as do
    vocabulário inglês + as dos templates ingleses (sem os placeholders)."""
    chunks = [re.sub(r"\{[^}]*\}", " ", t) for t in TEMPLATES_EN]
    for genre_vocab in VOCAB_EN.values():
        for values in genre_vocab.values():
            chunks.extend(values)
    return set(re.findall(r"[a-z]+", " ".join(chunks).lower()))


def test_generate_sample_english_is_nonempty_and_ascii():
    rng = random.Random(0)
    for genre in GENRES:
        text = generate_sample(genre, rng, lang="en")
        assert text and text.isascii()


def test_english_samples_never_leak_portuguese_words_even_with_full_overlap():
    # overlap_prob=1.0 -> todo slot vem do pool compartilhado. O pool é por
    # língua, então ainda assim só pode sair vocabulário inglês.
    allowed = _english_allowed_words()
    rng = random.Random(5)
    for _ in range(100):
        text = generate_sample("terror", rng, overlap_prob=1.0, lang="en")
        words = set(re.findall(r"[a-z]+", text.lower()))
        assert words <= allowed, f"palavras fora do inglês: {words - allowed}"


def test_multilingual_dataset_has_lang_column_and_is_balanced():
    df = generate_dataset(samples_per_class=10, seed=1, languages=("pt", "en"))
    assert "lang" in df.columns
    assert len(df) == 2 * len(GENRES) * 10
    counts = df.groupby(["lang", "label"]).size()
    assert (counts == 10).all()
    assert set(df["lang"]) == {"pt", "en"}


def test_default_dataset_is_portuguese_only_for_backward_compatibility():
    df = generate_dataset(samples_per_class=5, seed=1)
    assert set(df["lang"]) == {"pt"}
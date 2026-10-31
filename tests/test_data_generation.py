"""Testes do gerador de dataset sintético e da integridade das premissas."""

import random
import re
import string

from data_generation import (
    build_hero,
    generate_dataset,
    generate_premise,
    generate_sample,
)
from premises import FLAVOR, GENRES, LANGUAGES, NAMES, SUBGENRES, TEMPLATES

POOLS = ("roles", "settings", "threats", "goals", "twists")
WORD_RE = re.compile(r"[^\W\d_]+")  # sequências de letras (com acentos)


# ---------------------------------------------------------------------------
# Geração básica
# ---------------------------------------------------------------------------

def test_generate_sample_returns_nonempty_string():
    text = generate_sample("terror", random.Random(0))
    assert isinstance(text, str) and len(text) > 0


def test_generate_sample_is_deterministic_given_same_seed():
    assert generate_sample("terror", random.Random(42)) == generate_sample("terror", random.Random(42))


def test_generate_dataset_has_expected_size_and_is_balanced():
    df = generate_dataset(samples_per_class=10, seed=1)
    assert len(df) == 10 * len(GENRES)
    assert (df["label"].value_counts() == 10).all()


def test_generate_dataset_has_no_duplicate_text_within_a_genre():
    df = generate_dataset(samples_per_class=40, seed=3, hybrid_prob=0.3)
    for genre in GENRES:
        assert df.loc[df["label"] == genre, "text"].is_unique


def test_generate_dataset_same_seed_is_reproducible():
    df_a = generate_dataset(samples_per_class=5, seed=7, hybrid_prob=0.3, languages=("pt", "en"))
    df_b = generate_dataset(samples_per_class=5, seed=7, hybrid_prob=0.3, languages=("pt", "en"))
    assert df_a.equals(df_b)


def test_dataset_has_expected_columns():
    df = generate_dataset(samples_per_class=3, seed=1)
    assert list(df.columns) == ["text", "label", "lang", "subgenre", "hybrid"]


def test_default_dataset_is_portuguese_only_for_backward_compatibility():
    df = generate_dataset(samples_per_class=5, seed=1)
    assert set(df["lang"]) == {"pt"}


def test_multilingual_dataset_is_balanced_per_language_and_genre():
    df = generate_dataset(samples_per_class=10, seed=1, languages=("pt", "en"))
    assert len(df) == 2 * len(GENRES) * 10
    assert (df.groupby(["lang", "label"]).size() == 10).all()
    assert set(df["lang"]) == {"pt", "en"}


# ---------------------------------------------------------------------------
# Subgêneros e híbridos
# ---------------------------------------------------------------------------

def test_subgenre_always_belongs_to_the_requested_genre():
    rng = random.Random(0)
    for lang in LANGUAGES:
        for genre in GENRES:
            for _ in range(20):
                premise = generate_premise(genre, rng, lang=lang)
                assert premise["subgenre"] in SUBGENRES[lang][genre]


def test_without_hybrid_probability_no_premise_is_hybrid():
    df = generate_dataset(samples_per_class=20, seed=2, hybrid_prob=0.0)
    assert (df["hybrid"] == "none").all()


def test_full_hybrid_probability_adds_flavor_from_another_genre():
    rng = random.Random(1)
    for lang in LANGUAGES:
        for genre in GENRES:
            for _ in range(20):
                premise = generate_premise(genre, rng, hybrid_prob=1.0, lang=lang)
                assert premise["hybrid"] != "none" and premise["hybrid"] != genre
                # a frase-tempero do outro gênero aparece no texto
                assert any(s in premise["text"] for s in FLAVOR[lang][premise["hybrid"]])


def test_hybrid_label_stays_the_main_genre():
    df = generate_dataset(samples_per_class=30, seed=4, hybrid_prob=1.0)
    assert (df["hybrid"] != df["label"]).all()
    assert set(df["label"]) == set(GENRES)


# ---------------------------------------------------------------------------
# Heróis (nome + aposto)
# ---------------------------------------------------------------------------

def test_build_hero_named_role_uses_name_from_matching_pool_and_apposition():
    rng = random.Random(0)
    for lang in LANGUAGES:
        for gender in ("f", "m"):
            hero = build_hero(lang, (gender, "a role text"), rng)
            first_name = hero.split()[0]
            assert first_name in NAMES[lang][gender]
            assert hero.endswith(", a role text,")


def test_build_hero_collective_role_has_no_name():
    assert build_hero("pt", (None, "um grupo de amigos"), random.Random(0)) == "um grupo de amigos"


# ---------------------------------------------------------------------------
# Nenhuma língua vaza palavras de outra
# ---------------------------------------------------------------------------

def _all_strings(lang: str) -> list[str]:
    chunks = [re.sub(r"\{[^}]*\}", " ", t) for t in TEMPLATES[lang]]
    for genre_vocab in SUBGENRES[lang].values():
        for pools in genre_vocab.values():
            chunks.extend(role[1] for role in pools["roles"])
            for key in POOLS[1:]:
                chunks.extend(pools[key])
    for sentences in FLAVOR[lang].values():
        chunks.extend(sentences)
    names = NAMES[lang]
    chunks.extend(names["f"] + names["m"] + names["surnames"])
    return chunks


def test_premises_only_use_words_from_their_own_language():
    for lang in LANGUAGES:
        allowed = set(WORD_RE.findall(" ".join(_all_strings(lang)).lower()))
        rng = random.Random(5)
        for genre in GENRES:
            for _ in range(60):
                text = generate_sample(genre, rng, hybrid_prob=0.5, lang=lang)
                words = set(WORD_RE.findall(text.lower()))
                assert words <= allowed, f"[{lang}] palavras fora do vocabulário: {words - allowed}"


# ---------------------------------------------------------------------------
# Integridade do conteúdo em premises.py
# ---------------------------------------------------------------------------

def test_every_language_covers_every_genre_with_at_least_two_subgenres():
    for lang in LANGUAGES:
        assert set(SUBGENRES[lang]) == set(GENRES)
        for genre in GENRES:
            assert len(SUBGENRES[lang][genre]) >= 2


def test_languages_have_the_same_subgenres_and_pool_sizes():
    base = LANGUAGES[0]
    for lang in LANGUAGES[1:]:
        for genre in GENRES:
            assert set(SUBGENRES[lang][genre]) == set(SUBGENRES[base][genre])
            for sub in SUBGENRES[base][genre]:
                for pool in POOLS:
                    assert len(SUBGENRES[lang][genre][sub][pool]) == len(SUBGENRES[base][genre][sub][pool]), (
                        f"{lang}/{genre}/{sub}/{pool} tem tamanho diferente de {base}"
                    )


def test_pools_are_nonempty_and_free_of_commas():
    # Vírgulas dentro das peças quebrariam a pontuação dos templates.
    for lang in LANGUAGES:
        for genre_vocab in SUBGENRES[lang].values():
            for pools in genre_vocab.values():
                for pool in POOLS:
                    assert pools[pool], f"pool {pool} vazio"
                strings = [r[1] for r in pools["roles"]]
                for pool in POOLS[1:]:
                    strings.extend(pools[pool])
                assert all("," not in s for s in strings)


def test_english_content_has_no_apostrophes():
    # O tokenizador quebraria "clan's" em dois tokens ("clan" e "s").
    assert all("'" not in s for s in _all_strings("en"))


def test_every_language_has_flavor_for_every_genre_and_names_for_both_genders():
    for lang in LANGUAGES:
        assert set(FLAVOR[lang]) == set(GENRES)
        assert all(FLAVOR[lang][g] for g in GENRES)
        assert NAMES[lang]["f"] and NAMES[lang]["m"] and NAMES[lang]["surnames"]


def test_templates_only_use_known_placeholders():
    known = {"hero", "hero_cap", "setting", "setting_cap", "threat", "goal", "twist"}
    for lang in LANGUAGES:
        for template in TEMPLATES[lang]:
            assert set(re.findall(r"\{(\w+)\}", template)) <= known


def test_generated_text_has_no_unfilled_placeholders_or_double_spaces():
    rng = random.Random(9)
    for lang in LANGUAGES:
        for genre in GENRES:
            for _ in range(40):
                text = generate_sample(genre, rng, hybrid_prob=0.5, lang=lang)
                assert "{" not in text and "}" not in text
                assert "  " not in text
                assert text[0] in (string.ascii_uppercase + "ÁÉÍÓÚÂÊÔÃÕÇ")
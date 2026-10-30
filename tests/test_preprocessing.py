"""Testes do pré-processamento: tokenização, vocabulário e codificação."""

from preprocessing import PAD_TOKEN, UNK_TOKEN, build_vocab, encode, tokenize


def test_tokenize_lowercases_and_strips_punctuation():
    assert tokenize("Um Dragão, enfim!") == ["um", "dragão", "enfim"]


def test_tokenize_empty_string_returns_empty_list():
    assert tokenize("") == []


def test_tokenize_preserves_accented_characters():
    assert tokenize("herói fantástico") == ["herói", "fantástico"]


def test_build_vocab_reserves_pad_and_unk_at_indices_0_and_1():
    vocab = build_vocab([["ola", "mundo"]])
    assert vocab[PAD_TOKEN] == 0
    assert vocab[UNK_TOKEN] == 1


def test_build_vocab_includes_seen_words():
    vocab = build_vocab([["ola", "mundo"], ["ola"]])
    assert "ola" in vocab
    assert "mundo" in vocab


def test_build_vocab_min_freq_filters_rare_words():
    vocab = build_vocab([["comum", "comum", "raro"]], min_freq=2)
    assert "comum" in vocab
    assert "raro" not in vocab


def test_encode_pads_short_sequences_with_zero():
    vocab = {PAD_TOKEN: 0, UNK_TOKEN: 1, "ola": 2}
    assert encode(["ola"], vocab, max_len=4) == [2, 0, 0, 0]


def test_encode_truncates_sequences_longer_than_max_len():
    vocab = {PAD_TOKEN: 0, UNK_TOKEN: 1, "a": 2, "b": 3, "c": 4}
    assert encode(["a", "b", "c"], vocab, max_len=2) == [2, 3]


def test_encode_maps_unknown_words_to_unk():
    vocab = {PAD_TOKEN: 0, UNK_TOKEN: 1, "ola": 2}
    assert encode(["palavra-nunca-vista"], vocab, max_len=1) == [1]


def test_encode_output_always_has_length_max_len():
    vocab = {PAD_TOKEN: 0, UNK_TOKEN: 1, "a": 2}
    for tokens in ([], ["a"], ["a", "a", "a", "a", "a"]):
        assert len(encode(tokens, vocab, max_len=3)) == 3


def test_split_dataset_stratifies_by_genre_and_language():
    import pandas as pd

    from preprocessing import split_dataset

    # 2 gêneros x 2 línguas x 20 amostras = 80 linhas
    rows = [
        {"text": f"t{i}", "label": label, "lang": lang}
        for label in ("a", "b")
        for lang in ("pt", "en")
        for i in range(20)
    ]
    df = pd.DataFrame(rows)
    train_df, val_df, test_df = split_dataset(df, val_size=0.25, test_size=0.25, seed=0)

    for split_df, expected in ((train_df, 10), (val_df, 5), (test_df, 5)):
        counts = split_df.groupby(["label", "lang"]).size()
        assert (counts == expected).all()
"""Testes do pré-processamento: tokenização, vocabulário e codificação."""

from preprocessing import PAD_TOKEN, UNK_TOKEN, build_vocab, encode, tokenize

# Testa se não tem pontos de exclamação e interrogação e se está em letra minúscula na tokenização
def test_tokenize_lowercases_and_strips_punctuation():
    assert tokenize("Um Dragão, enfim!") == ["um", "dragão", "enfim"]

# Testa se a string vazia retorna uma lista vazia na tokenização
def test_tokenize_empty_string_returns_empty_list():
    assert tokenize("") == []

# Testa se a pontuação está sendo preservada na tokenização
def test_tokenize_preserves_accented_characters():
    assert tokenize("herói fantástico") == ["herói", "fantástico"]

# Testa se durante a tokenização, a separação de caracteres do vocabulário em números está sendo feita corretamente.
def test_build_vocab_reserves_pad_and_unk_at_indices_0_and_1():
    vocab = build_vocab([["ola", "mundo"]])
    assert vocab[PAD_TOKEN] == 0
    assert vocab[UNK_TOKEN] == 1

# Testa se o vocabulário já tem palavras já vistas previamente.
def test_build_vocab_includes_seen_words():
    vocab = build_vocab([["ola", "mundo"], ["ola"]])
    assert "ola" in vocab
    assert "mundo" in vocab

# Testa filtros de frequência nas palavras.
def test_build_vocab_min_freq_filters_rare_words():
    vocab = build_vocab([["comum", "comum", "raro"]], min_freq=2)
    assert "comum" in vocab
    assert "raro" not in vocab

# Testa o encode de sequências curtas dando a elas o valor zero.
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

# Se os testes não passaram, você fez alguma merdaa
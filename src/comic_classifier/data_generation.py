"""
Gera um dataset sintético de premissas de quadrinhos rotuladas por gênero:
super-herói, terror/horror, ficção científica e mangá/fantasia, em várias
línguas (hoje: português "pt" e inglês "en").

Como cada premissa é montada (o CONTEÚDO fica em premises.py):
  1. sorteia um SUBGÊNERO do gênero (ex: terror -> casa-assombrada, folk-rural,
     psicologico);
  2. sorteia as peças daquele subgênero: papel do herói (com nome próprio),
     cenário, ameaça, objetivo e reviravolta — todas coerentes entre si;
  3. encaixa as peças num molde de frase da língua;
  4. com probabilidade `hybrid_prob`, acrescenta uma frase-tempero de OUTRO
     gênero (ex: um toque de terror numa trama de ficção científica). O rótulo
     continua sendo o gênero principal — é isso que torna a tarefa difícil de
     um jeito realista (híbridos coerentes, não ruído aleatório).

O dataset final tem as colunas: text, label (gênero), lang, subgenre e hybrid
(o gênero do tempero, ou "none").
"""

import argparse
import random
from pathlib import Path

import pandas as pd

from premises import FLAVOR, GENRES, LANGUAGES, NAMES, SUBGENRES, TEMPLATES


def capitalize_first(text: str) -> str:
    """Deixa só a primeira letra maiúscula (usado quando uma peça abre a frase,
    ex: 'nas ruas de Porto Negro' -> 'Nas ruas de Porto Negro')."""
    return text[0].upper() + text[1:] if text else text


def build_hero(lang: str, role: tuple, rng: random.Random) -> str:
    """Monta o herói a partir do papel sorteado.

    Papel com gênero gramatical ("f"/"m") ganha um nome próprio sorteado do
    banco de nomes, com o papel como aposto (já entre vírgulas, e os templates
    sempre põem um verbo logo depois do herói):
        "a perita forense" -> "Marina Tavares, a perita forense,"
    Papel coletivo (None) fica como está: "um grupo de justiceiros de bairro".
    """
    gender, text = role
    if gender is None:
        return text
    names = NAMES[lang]
    return f"{rng.choice(names[gender])} {rng.choice(names['surnames'])}, {text},"


def generate_premise(genre: str, rng: random.Random, hybrid_prob: float = 0.0, lang: str = "pt") -> dict:
    """Monta UMA premissa e devolve um dicionário com o texto e os metadados
    (subgênero e gênero do tempero híbrido, se houver)."""
    # sorted() garante uma ordem estável das chaves -> mesma seed, mesmo resultado
    subgenre = rng.choice(sorted(SUBGENRES[lang][genre]))
    pools = SUBGENRES[lang][genre][subgenre]

    hero = build_hero(lang, rng.choice(pools["roles"]), rng)
    setting = rng.choice(pools["settings"])
    template = rng.choice(TEMPLATES[lang])

    text = template.format(
        hero=hero,
        hero_cap=capitalize_first(hero),
        setting=setting,
        setting_cap=capitalize_first(setting),
        threat=rng.choice(pools["threats"]),
        goal=rng.choice(pools["goals"]),
        twist=rng.choice(pools["twists"]),
    )

    # Híbrido: a trama principal continua do gênero `genre`, mas uma frase do
    # tempero de outro gênero é acrescentada ao final.
    hybrid = "none"
    if rng.random() < hybrid_prob:
        hybrid = rng.choice([g for g in GENRES if g != genre])
        text = f"{text} {rng.choice(FLAVOR[lang][hybrid])}"

    return {"text": text, "subgenre": subgenre, "hybrid": hybrid}


def generate_sample(genre: str, rng: random.Random, hybrid_prob: float = 0.0, lang: str = "pt") -> str:
    """Atalho que devolve só o texto da premissa."""
    return generate_premise(genre, rng, hybrid_prob, lang)["text"]


def generate_dataset(
    samples_per_class: int, seed: int, hybrid_prob: float = 0.0, languages=("pt",)
) -> pd.DataFrame:
    """Gera o dataset completo: `samples_per_class` premissas ÚNICAS para cada
    combinação (língua, gênero), depois embaralha tudo num único DataFrame.

    Ex: com languages=("pt", "en") e samples_per_class=150 -> 2 x 4 x 150 = 1200
    linhas, perfeitamente balanceadas entre línguas e gêneros."""
    rng = random.Random(seed)  # RNG próprio (não usa random global) -> reprodutível
    rows = []
    for lang in languages:
        for genre in GENRES:
            seen = set()  # já gerados para esta (língua, gênero), evita repetição
            attempts = 0
            # Fica gerando até bater a meta de amostras ÚNICAS, com um teto de
            # tentativas para não entrar em loop infinito caso as combinações
            # se esgotem antes de atingir samples_per_class.
            while len(seen) < samples_per_class and attempts < samples_per_class * 40:
                premise = generate_premise(genre, rng, hybrid_prob, lang)
                attempts += 1
                if premise["text"] in seen:
                    continue  # premissa repetida, sorteia de novo
                seen.add(premise["text"])
                rows.append({**premise, "label": genre, "lang": lang})
    df = pd.DataFrame(rows)[["text", "label", "lang", "subgenre", "hybrid"]]
    # Embaralha as linhas (senão o CSV ficaria com todo super-herói primeiro,
    # depois todo terror, etc.).
    return df.sample(frac=1, random_state=seed).reset_index(drop=True)


def main():
    parser = argparse.ArgumentParser(description="Gera dataset sintético de premissas de quadrinhos")
    parser.add_argument(
        "--samples-per-class",
        type=int,
        default=150,
        help="Amostras por gênero, POR LÍNGUA (o total é línguas x 4 gêneros x este valor)",
    )
    parser.add_argument(
        "--languages",
        nargs="+",
        choices=LANGUAGES,
        default=LANGUAGES,
        help="Línguas a gerar (padrão: todas as registradas em premises.py)",
    )
    parser.add_argument("--seed", type=int, default=42)  # mesma seed = mesmo dataset sempre
    parser.add_argument(
        "--hybrid-prob",
        type=float,
        default=0.3,
        help="Probabilidade de uma premissa receber um tempero de outro gênero (híbrido coerente)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parents[2] / "data" / "raw" / "comics_synthetic.csv",
    )
    args = parser.parse_args()

    df = generate_dataset(args.samples_per_class, args.seed, args.hybrid_prob, tuple(args.languages))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.output, index=False, encoding="utf-8")
    print(f"Dataset salvo em {args.output} ({len(df)} amostras, hybrid_prob={args.hybrid_prob})")
    print(df.groupby(["lang", "label"]).size())
    print(f"Híbridos: {(df['hybrid'] != 'none').mean():.0%} das premissas")


if __name__ == "__main__":
    main()
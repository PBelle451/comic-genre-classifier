"""
Gera um dataset sintético de sinopses de quadrinhos rotuladas por gênero,
combinando templates de frase com bancos de vocabulário específicos de cada
gênero: super-herói, terror/horror, ficção científica, mangá/fantasia.
"""

import argparse
import random
from pathlib import Path

import pandas as pd

GENRES = ["super-heroi", "terror", "ficcao-cientifica", "manga-fantasia"]

VOCAB = {
    "super-heroi": {
        "protagonista": [
            "um vigilante mascarado", "uma heroína com poderes cósmicos",
            "um jovem que acabou de ganhar superpoderes", "um agente sobre-humano do governo",
            "uma equipe de heróis amadores", "um justiceiro movido a vingança",
            "uma cientista transformada em heroína", "um veterano herói aposentado",
        ],
        "antagonista": [
            "um vilão que quer dominar a cidade", "uma organização secreta de supervilões",
            "seu arqui-inimigo de longa data", "uma máquina de guerra fora de controle",
            "um clone maligno de si mesmo", "um bilionário corrupto com um exército de robôs",
        ],
        "cenario": [
            "em uma metrópole tomada pelo caos", "nas ruas de uma cidade à beira do colapso",
            "no topo de um arranha-céu em chamas", "durante uma invasão em grande escala",
            "em um laboratório secreto no subsolo da cidade",
        ],
        "objetivo": [
            "salvar a cidade antes que seja tarde demais",
            "impedir uma catástrofe que ameaça milhões de vidas",
            "proteger sua identidade secreta enquanto luta pela justiça",
            "recuperar o controle de seus próprios poderes",
            "unir uma equipe dispersa para enfrentar a ameaça final",
        ],
    },
    "terror": {
        "protagonista": [
            "uma família que acaba de se mudar", "um grupo de amigos em uma viagem de fim de semana",
            "uma investigadora do paranormal", "um zelador solitário",
            "uma criança que enxerga o que os adultos não veem", "um padre enviado para um exorcismo",
        ],
        "antagonista": [
            "uma entidade que habita as paredes da casa", "um culto sinistro escondido na floresta",
            "um espírito preso entre dois mundos", "uma maldição transmitida por gerações",
            "uma criatura que só aparece à meia-noite", "um vizinho com um segredo aterrorizante",
        ],
        "cenario": [
            "em uma mansão vitoriana abandonada", "em uma cidade isolada no interior",
            "em um hospital psiquiátrico desativado", "numa floresta onde ninguém retorna",
            "em um porão que ninguém ousa visitar",
        ],
        "objetivo": [
            "sobreviver até o amanhecer", "descobrir a verdade antes de perder a sanidade",
            "quebrar uma maldição antes que seja tarde demais",
            "escapar de um lugar que não os deixa partir",
            "proteger a família de uma presença que não vai embora",
        ],
    },
    "ficcao-cientifica": {
        "protagonista": [
            "a tripulação de uma nave de exploração", "uma inteligência artificial recém-desperta",
            "um engenheiro colonial em Marte", "uma soldado clonada geneticamente",
            "um viajante do tempo perdido na linha errada", "um cientista que descobriu vida alienígena",
        ],
        "antagonista": [
            "uma inteligência artificial rebelde", "uma civilização alienígena invasora",
            "um governo autoritário que controla a colônia", "uma anomalia espacial desconhecida",
            "um vírus sintético que reescreve o DNA humano", "uma corporação que manipula a linha do tempo",
        ],
        "cenario": [
            "a bordo de uma estação espacial à deriva", "em uma colônia distante nos confins da galáxia",
            "em uma Terra pós-apocalíptica dominada por máquinas", "durante uma viagem interestelar de décadas",
            "em uma cidade futurista dividida por castas tecnológicas",
        ],
        "objetivo": [
            "impedir o colapso da última colônia humana",
            "restaurar a linha do tempo antes que a história se apague",
            "decidir se a humanidade merece ser salva",
            "encontrar um novo lar antes que os recursos se esgotem",
            "escapar do controle da inteligência artificial que os governa",
        ],
    },
    "manga-fantasia": {
        "protagonista": [
            "um jovem guerreiro em treinamento", "uma princesa exilada de seu reino",
            "um estudante de uma escola de magia", "um espadachim errante sem passado",
            "uma feiticeira que busca vingança", "um grupo de aventureiros recém-formado",
        ],
        "antagonista": [
            "um dragão ancestral desperto por engano", "um imperador que deseja unificar os reinos pela força",
            "uma seita que cultua um deus esquecido", "um rival de infância transformado em inimigo",
            "uma sombra que consome a magia do mundo", "um torneio mortal disputado por clãs rivais",
        ],
        "cenario": [
            "em um reino dividido por guerras antigas", "em uma academia secreta de artes marciais",
            "nas montanhas onde vivem os últimos dragões", "durante um torneio que decide o destino do reino",
            "em uma floresta selada por magia proibida",
        ],
        "objetivo": [
            "reunir os fragmentos de uma espada lendária",
            "vencer o torneio e restaurar a honra de seu clã",
            "quebrar o selo que aprisiona seu verdadeiro poder",
            "reclamar o trono usurpado de sua família",
            "provar que é digno de se tornar o próximo mestre",
        ],
    },
}

TEMPLATES = [
    "{cenario_cap}, {protagonista} precisa enfrentar {antagonista} para {objetivo}.",
    "{protagonista_cap} encontra-se diante da missão de confrontar {antagonista} {cenario}, na tentativa de {objetivo}.",
    "Quando {antagonista} ameaça tudo o que conhecem, {protagonista} parte {cenario} para {objetivo}.",
    "{cenario_cap}, a missão é clara: {objetivo}. Mas {antagonista} não vai facilitar o caminho de {protagonista}.",
]


def capitalize_first(text: str) -> str:
    return text[0].upper() + text[1:] if text else text


def build_shared_pool() -> dict[str, list[str]]:
    """Pool com os valores de TODOS os gêneros para cada tipo de slot —
    usado para introduzir sobreposição de vocabulário entre gêneros."""
    pool: dict[str, list[str]] = {}
    for genre_vocab in VOCAB.values():
        for slot, values in genre_vocab.items():
            pool.setdefault(slot, [])
            pool[slot].extend(values)
    return {slot: sorted(set(values)) for slot, values in pool.items()}


SHARED_POOL = build_shared_pool()


def generate_sample(genre: str, rng: random.Random, overlap_prob: float = 0.0) -> str:
    vocab = VOCAB[genre]
    slots = {}
    for slot in ("protagonista", "antagonista", "cenario", "objetivo"):
        # Com probabilidade overlap_prob, puxa o valor do pool geral (qualquer
        # gênero) em vez do vocabulário específico deste gênero — isso cria
        # frases ambíguas de propósito, tornando a classificação mais difícil.
        source = SHARED_POOL[slot] if rng.random() < overlap_prob else vocab[slot]
        slots[slot] = rng.choice(source)

    template = rng.choice(TEMPLATES)
    return template.format(
        protagonista=slots["protagonista"],
        protagonista_cap=capitalize_first(slots["protagonista"]),
        antagonista=slots["antagonista"],
        cenario=slots["cenario"],
        cenario_cap=capitalize_first(slots["cenario"]),
        objetivo=slots["objetivo"],
    )


def generate_dataset(samples_per_class: int, seed: int, overlap_prob: float = 0.0) -> pd.DataFrame:
    rng = random.Random(seed)
    rows = []
    for genre in GENRES:
        seen = set()
        attempts = 0
        while len(seen) < samples_per_class and attempts < samples_per_class * 40:
            text = generate_sample(genre, rng, overlap_prob)
            attempts += 1
            if text in seen:
                continue
            seen.add(text)
            rows.append({"text": text, "label": genre})
    df = pd.DataFrame(rows)
    return df.sample(frac=1, random_state=seed).reset_index(drop=True)


def main():
    parser = argparse.ArgumentParser(description="Gera dataset sintético de sinopses de quadrinhos")
    parser.add_argument("--samples-per-class", type=int, default=150)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--overlap-prob",
        type=float,
        default=0.3,
        help="Probabilidade de um slot vir do pool geral (sobreposição entre gêneros)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parents[2] / "data" / "raw" / "comics_synthetic.csv",
    )
    args = parser.parse_args()

    df = generate_dataset(args.samples_per_class, args.seed, args.overlap_prob)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.output, index=False, encoding="utf-8")
    print(f"Dataset salvo em {args.output} ({len(df)} amostras, overlap_prob={args.overlap_prob})")
    print(df["label"].value_counts())


if __name__ == "__main__":
    main()
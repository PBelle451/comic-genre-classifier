"""
Gera um dataset sintético de sinopses de quadrinhos rotuladas por gênero,
combinando templates de frase com bancos de vocabulário específicos de cada
gênero: super-herói, terror/horror, ficção científica, mangá/fantasia.

Suporta várias línguas (hoje: português "pt" e inglês "en"). Cada língua tem
seu próprio banco de vocabulário e seus próprios templates; os RÓTULOS de
gênero são os mesmos em todas, e o dataset ganha uma coluna "lang".
"""

import argparse
import random
from pathlib import Path

import pandas as pd

GENRES = ["super-heroi", "terror", "ficcao-cientifica", "manga-fantasia"]

# ---------------------------------------------------------------------------
# Português
# ---------------------------------------------------------------------------
VOCAB_PT = {
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

TEMPLATES_PT = [
    "{cenario_cap}, {protagonista} precisa enfrentar {antagonista} para {objetivo}.",
    "{protagonista_cap} encontra-se diante da missão de confrontar {antagonista} {cenario}, na tentativa de {objetivo}.",
    "Quando {antagonista} ameaça tudo o que conhecem, {protagonista} parte {cenario} para {objetivo}.",
    "{cenario_cap}, a missão é clara: {objetivo}. Mas {antagonista} não vai facilitar o caminho de {protagonista}.",
]

# ---------------------------------------------------------------------------
# Inglês
# Convenções para manter a gramática correta em qualquer combinação de slots:
#   - protagonista e antagonista são sempre sintagmas no SINGULAR (concordância
#     do verbo nos templates);
#   - objetivo é um verbo no infinitivo SEM "to" (o template acrescenta o "to"
#     quando precisa);
#   - sem apóstrofos ("clan's" viraria dois tokens, "clan" e "s", no tokenizador).
# ---------------------------------------------------------------------------
VOCAB_EN = {
    "super-heroi": {
        "protagonista": [
            "a masked vigilante", "a heroine with cosmic powers",
            "a teenager who just gained superpowers", "a superhuman government agent",
            "a team of amateur heroes", "a vigilante driven by revenge",
            "a scientist turned heroine", "a retired veteran hero",
        ],
        "antagonista": [
            "a villain who wants to dominate the city", "a secret organization of supervillains",
            "an old arch-nemesis", "a war machine out of control",
            "an evil clone of the hero", "a corrupt billionaire with an army of robots",
        ],
        "cenario": [
            "in a metropolis gripped by chaos", "on the streets of a city on the brink of collapse",
            "atop a burning skyscraper", "during a large-scale invasion",
            "in a secret laboratory beneath the city",
        ],
        "objetivo": [
            "save the city before it is too late",
            "stop a catastrophe that threatens millions of lives",
            "protect a secret identity while fighting for justice",
            "regain control of their own powers",
            "unite a scattered team to face the final threat",
        ],
    },
    "terror": {
        "protagonista": [
            "a family that has just moved in", "a group of friends on a weekend trip",
            "a paranormal investigator", "a lonely caretaker",
            "a child who sees what adults cannot", "a priest sent to perform an exorcism",
        ],
        "antagonista": [
            "an entity that lives inside the walls of the house", "a sinister cult hidden in the forest",
            "a spirit trapped between two worlds", "a curse passed down through generations",
            "a creature that only appears at midnight", "a neighbor with a terrifying secret",
        ],
        "cenario": [
            "in an abandoned Victorian mansion", "in an isolated small town",
            "in a decommissioned psychiatric hospital", "in a forest from which no one returns",
            "in a basement no one dares to visit",
        ],
        "objetivo": [
            "survive until dawn", "uncover the truth before losing their sanity",
            "break a curse before it is too late",
            "escape from a place that will not let them leave",
            "protect the family from a presence that will not go away",
        ],
    },
    "ficcao-cientifica": {
        "protagonista": [
            "the crew of an exploration ship", "a newly awakened artificial intelligence",
            "a colonial engineer on Mars", "a genetically cloned soldier",
            "a time traveler lost on the wrong timeline", "a scientist who discovered alien life",
        ],
        "antagonista": [
            "a rogue artificial intelligence", "an invading alien civilization",
            "an authoritarian government that controls the colony", "an unknown space anomaly",
            "a synthetic virus that rewrites human DNA", "a corporation that manipulates the timeline",
        ],
        "cenario": [
            "aboard a drifting space station", "in a distant colony at the edge of the galaxy",
            "on a post-apocalyptic Earth ruled by machines", "during a decades-long interstellar voyage",
            "in a futuristic city divided by technological castes",
        ],
        "objetivo": [
            "prevent the collapse of the last human colony",
            "restore the timeline before history is erased",
            "decide whether humanity deserves to be saved",
            "find a new home before resources run out",
            "escape the control of the artificial intelligence that governs them",
        ],
    },
    "manga-fantasia": {
        "protagonista": [
            "a young warrior in training", "an exiled princess",
            "a student at a school of magic", "a wandering swordsman with no past",
            "a sorceress seeking revenge", "a newly formed party of adventurers",
        ],
        "antagonista": [
            "an ancient dragon awakened by mistake", "an emperor who wants to unite the kingdoms by force",
            "a cult that worships a forgotten god", "a childhood rival turned enemy",
            "a shadow that devours the magic of the world", "a deadly tournament fought between rival clans",
        ],
        "cenario": [
            "in a kingdom divided by ancient wars", "in a secret martial arts academy",
            "in the mountains where the last dragons live",
            "during a tournament that decides the fate of the kingdom",
            "in a forest sealed by forbidden magic",
        ],
        "objetivo": [
            "gather the fragments of a legendary sword",
            "win the tournament and restore the honor of their clan",
            "break the seal that imprisons their true power",
            "reclaim the usurped throne of their family",
            "prove worthy of becoming the next master",
        ],
    },
}

# As CHAVES dos placeholders continuam em português (protagonista, cenario...)
# porque são nomes internos do código, iguais para todas as línguas.
TEMPLATES_EN = [
    "{cenario_cap}, {protagonista} must face {antagonista} in order to {objetivo}.",
    "{protagonista_cap} is tasked with confronting {antagonista} {cenario}, in an attempt to {objetivo}.",
    "{cenario_cap}, {protagonista} sets out to {objetivo} as {antagonista} closes in.",
    "{cenario_cap}, the mission is clear: {objetivo}. But {antagonista} will not make it easy for {protagonista}.",
]

# ---------------------------------------------------------------------------
# Registro de línguas: cada código aponta para o vocabulário e os templates
# daquela língua. Para adicionar uma nova (ex: "es"), basta criar VOCAB_ES e
# TEMPLATES_ES e registrá-los aqui — o resto do código já é genérico.
# ---------------------------------------------------------------------------
LANGUAGES = ["pt", "en"]
VOCAB_BY_LANG = {"pt": VOCAB_PT, "en": VOCAB_EN}
TEMPLATES_BY_LANG = {"pt": TEMPLATES_PT, "en": TEMPLATES_EN}


def capitalize_first(text: str) -> str:
    """Deixa só a primeira letra maiúscula (usado quando a frase do slot
    aparece no início da sentença, ex: 'em uma mansão...' -> 'Em uma mansão...')."""
    return text[0].upper() + text[1:] if text else text


def build_shared_pool(vocab: dict) -> dict[str, list[str]]:
    """Junta os valores de TODOS os gêneros de UMA língua em um único pool, por
    tipo de slot.

    Ex: pool["antagonista"] passa a conter os antagonistas de super-herói,
    terror, ficção científica E mangá/fantasia, todos juntos. É esse pool que
    generate_sample() usa quando decide "roubar" um valor de outro gênero, para
    criar sobreposição de vocabulário (veja overlap_prob abaixo).
    """
    pool: dict[str, list[str]] = {}
    for genre_vocab in vocab.values():
        for slot, values in genre_vocab.items():
            pool.setdefault(slot, [])
            pool[slot].extend(values)
    return {slot: sorted(set(values)) for slot, values in pool.items()}


# Um pool por língua, construído uma única vez na importação do módulo. A
# sobreposição acontece só DENTRO da mesma língua: uma frase em inglês nunca
# "rouba" um pedaço em português (isso geraria frases híbridas, não realistas).
SHARED_POOLS = {lang: build_shared_pool(vocab) for lang, vocab in VOCAB_BY_LANG.items()}


def generate_sample(genre: str, rng: random.Random, overlap_prob: float = 0.0, lang: str = "pt") -> str:
    """Monta UMA sinopse sintética para o gênero e a língua pedidos.

    Para cada um dos 4 "slots" da frase (protagonista, antagonista, cenário,
    objetivo), sorteia um valor — normalmente do vocabulário do próprio
    gênero, mas com probabilidade `overlap_prob` sorteia do pool compartilhado
    (ou seja, de qualquer gênero, na MESMA língua). Depois escolhe um template
    aleatório daquela língua e encaixa os valores sorteados nele.
    """
    vocab = VOCAB_BY_LANG[lang][genre]
    shared_pool = SHARED_POOLS[lang]
    slots = {}
    for slot in ("protagonista", "antagonista", "cenario", "objetivo"):
        # Com probabilidade overlap_prob, puxa o valor do pool geral (qualquer
        # gênero) em vez do vocabulário específico deste gênero — isso cria
        # frases ambíguas de propósito, tornando a classificação mais difícil.
        source = shared_pool[slot] if rng.random() < overlap_prob else vocab[slot]
        slots[slot] = rng.choice(source)

    template = rng.choice(TEMPLATES_BY_LANG[lang])
    # Alguns templates usam a versão capitalizada (quando o slot abre a frase)
    # e outros a versão normal (quando o slot vem no meio) — por isso mandamos
    # as duas variantes de protagonista/cenário no .format().
    return template.format(
        protagonista=slots["protagonista"],
        protagonista_cap=capitalize_first(slots["protagonista"]),
        antagonista=slots["antagonista"],
        cenario=slots["cenario"],
        cenario_cap=capitalize_first(slots["cenario"]),
        objetivo=slots["objetivo"],
    )


def generate_dataset(
    samples_per_class: int, seed: int, overlap_prob: float = 0.0, languages=("pt",)
) -> pd.DataFrame:
    """Gera o dataset completo: `samples_per_class` frases ÚNICAS para cada
    combinação (língua, gênero), depois embaralha tudo junto num único
    DataFrame com as colunas: text, label (gênero) e lang (língua).

    Ex: com languages=("pt", "en") e samples_per_class=150 -> 2 x 4 x 150 = 1200
    linhas, perfeitamente balanceadas entre línguas e gêneros."""
    rng = random.Random(seed)  # RNG próprio (não usa random global) -> reprodutível
    rows = []
    for lang in languages:
        for genre in GENRES:
            seen = set()  # já gerados para esta (língua, gênero), evita repetição
            attempts = 0
            # Fica gerando até bater a meta de amostras ÚNICAS, com um teto de
            # tentativas para não entrar em loop infinito caso o vocabulário
            # esgote as combinações possíveis antes de atingir samples_per_class.
            while len(seen) < samples_per_class and attempts < samples_per_class * 40:
                text = generate_sample(genre, rng, overlap_prob, lang)
                attempts += 1
                if text in seen:
                    continue  # frase repetida, sorteia de novo
                seen.add(text)
                rows.append({"text": text, "label": genre, "lang": lang})
    df = pd.DataFrame(rows)
    # Embaralha as linhas (senão o CSV ficaria com todo super-herói primeiro,
    # depois todo terror, etc. — ruim para treino, mesmo com shuffle=True no
    # DataLoader depois, é mais seguro já entregar embaralhado).
    return df.sample(frac=1, random_state=seed).reset_index(drop=True)


def main():
    parser = argparse.ArgumentParser(description="Gera dataset sintético de sinopses de quadrinhos")
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
        help="Línguas a gerar (padrão: todas as registradas)",
    )
    parser.add_argument("--seed", type=int, default=42)  # mesma seed = mesmo dataset sempre
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

    df = generate_dataset(args.samples_per_class, args.seed, args.overlap_prob, tuple(args.languages))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.output, index=False, encoding="utf-8")
    print(f"Dataset salvo em {args.output} ({len(df)} amostras, overlap_prob={args.overlap_prob})")
    print(df.groupby(["lang", "label"]).size())


if __name__ == "__main__":
    main()
"""
Conteúdo das premissas (só DADOS, nenhuma lógica — a lógica fica em
data_generation.py).

Estrutura:
  SUBGENRES[língua][gênero][subgênero] = {roles, settings, threats, goals, twists}
    roles    -> lista de (gênero_gramatical, texto), sempre COM artigo. "f"/"m"
                => o gerador antepõe um nome próprio e usa o papel como aposto
                ("Marina Tavares, a perita forense,"); o gênero só escolhe o
                banco de nomes. None => papel coletivo, sem nome ("uma equipe
                de heróis").
    settings -> onde acontece (já com a preposição: "nas ruas de...")
    threats  -> a ameaça, como sintagma nominal no SINGULAR ("uma rede de...")
    goals    -> o objetivo, verbo no infinitivo ("desmascarar o esquema...")
    twists   -> reviravolta, uma ORAÇÃO completa que cabe depois de "mas"/"e"
  FLAVOR[língua][gênero]  -> frases-tempero usadas nos HÍBRIDOS: aparecem numa
                             premissa de OUTRO gênero, criando mistura coerente.
  NAMES[língua]           -> nomes e sobrenomes para os personagens.
  TEMPLATES[língua]       -> moldes de frase que combinam as peças acima.

Regras para manter a gramática correta em qualquer combinação (há testes que
conferem várias delas):
  - sem vírgulas dentro de roles/settings/threats/goals/twists (os templates
    é que decidem a pontuação);
  - sem apóstrofos (o tokenizador quebraria "clan's" em "clan" + "s");
  - heróis e ameaças sempre no singular; sem pronomes que marquem gênero
    (ele/ela, o/a) referindo-se ao herói, já que o gênero varia por papel.
"""

GENRES = ["super-heroi", "terror", "ficcao-cientifica", "manga-fantasia"]

SUBGENRES = {
    # ------------------------------------------------------------------
    # PORTUGUÊS
    # ------------------------------------------------------------------
    "pt": {
        "super-heroi": {
            "noir-urbano": {
                "roles": [
                    ("f", "a vigilante mascarada"),
                    ("m", "o detetive aposentado"),
                    ("f", "a jornalista investigativa"),
                    ("m", "o ex-policial expulso da corporação"),
                    (None, "um grupo de justiceiros de bairro"),
                ],
                "settings": [
                    "nos becos do porto de Baía Sombria",
                    "no distrito financeiro de Nova Aurora",
                    "sob a chuva constante de Porto Negro",
                    "nos telhados de Cidade Cinzenta",
                ],
                "threats": [
                    "uma rede de tráfico de armas comandada pelo Barão",
                    "um prefeito corrupto protegido por mercenários",
                    "uma gangue que usa tecnologia militar roubada",
                    "um assassino em série que deixa cartas de baralho nas cenas dos crimes",
                ],
                "goals": [
                    "desmascarar o esquema antes das eleições",
                    "proteger uma testemunha-chave até o julgamento",
                    "recuperar um arquivo que incrimina metade da cidade",
                    "descobrir quem financia os crimes",
                ],
                "twists": [
                    "as pistas levam a alguém do próprio departamento de polícia",
                    "o maior aliado vem escondendo um segredo",
                    "cada prova encontrada desaparece sem deixar rastro",
                    "alguém vem seguindo cada passo desde o início",
                ],
            },
            "cosmico": {
                "roles": [
                    ("m", "o guardião de uma estrela moribunda"),
                    ("f", "a embaixadora de um planeta destruído"),
                    ("f", "a soldada de uma frota intergaláctica"),
                    ("m", "o último herói de uma raça extinta"),
                    (None, "uma equipe de heróis de mundos diferentes"),
                ],
                "settings": [
                    "na órbita de uma estrela em colapso",
                    "a bordo da estação orbital Zênite",
                    "entre as ruínas do planeta Kharos",
                    "no coração da Nebulosa Escarlate",
                ],
                "threats": [
                    "um devorador de mundos com fome insaciável",
                    "um império galáctico em expansão",
                    "uma entidade cósmica que reescreve a realidade",
                    "um exército de clones do antigo imperador",
                ],
                "goals": [
                    "salvar a Terra da aniquilação",
                    "reunir as relíquias que sustentam o universo",
                    "impedir o colapso da última estrela viva",
                    "convencer os povos livres a lutar juntos",
                ],
                "twists": [
                    "o poder que todos buscam está dentro de um dos próprios heróis",
                    "o inimigo é um antigo aliado de outra era",
                    "a ameaça foi criada pelos próprios guardiões do universo",
                    "a profecia aponta para um traidor entre os heróis",
                ],
            },
            "adolescente": {
                "roles": [
                    ("f", "a estudante do ensino médio que acabou de ganhar poderes"),
                    ("m", "o aluno bolsista com superforça"),
                    ("f", "a atleta que descobriu um dom perigoso"),
                    ("m", "o garoto que vira sombra quando sente medo"),
                    (None, "um clube de estudantes com superpoderes"),
                ],
                "settings": [
                    "no Colégio Estrela do Norte",
                    "na pequena cidade de Vale Verde",
                    "durante o campeonato estadual de ciências",
                    "no bairro operário de Vila Nova",
                ],
                "threats": [
                    "um professor com planos de dominação mundial",
                    "uma gangue de universitários com armaduras experimentais",
                    "uma corporação que sequestra adolescentes com habilidades",
                    "um vilão que se alimenta dos poderes dos outros",
                ],
                "goals": [
                    "esconder o segredo dos pais e dos amigos",
                    "dominar os poderes antes do baile de formatura",
                    "libertar os colegas sequestrados",
                    "descobrir a origem da mutação",
                ],
                "twists": [
                    "o melhor amigo guarda um segredo parecido",
                    "o diretor da escola sabe de tudo desde o início",
                    "os poderes ficam mais fortes a cada mentira contada",
                    "alguém muito próximo já trabalha para o inimigo",
                ],
            },
        },
        "terror": {
            "casa-assombrada": {
                "roles": [
                    ("f", "a corretora de imóveis"),
                    ("m", "o pai de uma família recém-mudada"),
                    ("f", "a médium aposentada"),
                    ("m", "o zelador noturno"),
                    (None, "um casal de recém-casados"),
                ],
                "settings": [
                    "na mansão abandonada da família Albuquerque",
                    "num casarão colonial isolado",
                    "no velho sobrado da rua das Acácias",
                    "numa pousada fechada há décadas",
                ],
                "threats": [
                    "um espírito que habita as paredes",
                    "uma presença que imita a voz dos mortos",
                    "uma maldição selada por um antigo morador",
                    "uma criança fantasma que nunca sai do porão",
                ],
                "goals": [
                    "sobreviver até o amanhecer",
                    "descobrir o que aconteceu com os antigos moradores",
                    "quebrar a maldição antes da próxima lua cheia",
                    "escapar de uma casa que não deixa ninguém partir",
                ],
                "twists": [
                    "as portas se fecham sozinhas toda vez que alguém tenta sair",
                    "as vozes nas paredes conhecem segredos que ninguém contou",
                    "o espelho do corredor mostra quem será a próxima vítima",
                    "um dos moradores já não é mais humano",
                ],
            },
            "folk-rural": {
                "roles": [
                    ("f", "a professora recém-chegada ao vilarejo"),
                    ("m", "o policial da cidade vizinha"),
                    ("f", "a antropóloga que estuda lendas locais"),
                    ("m", "o pescador viúvo"),
                    (None, "um grupo de amigos em viagem de acampamento"),
                ],
                "settings": [
                    "no vilarejo isolado de São Judas do Mato",
                    "numa floresta de onde ninguém retorna",
                    "na ilha de Pedra Velha",
                    "entre os canaviais da Fazenda Boa Esperança",
                ],
                "threats": [
                    "um culto que oferece sacrifícios à mata",
                    "uma criatura que caça em noites de neblina",
                    "uma festa tradicional que cobra sangue",
                    "uma maldição que passa de geração em geração",
                ],
                "goals": [
                    "sair do vilarejo antes do festival de inverno",
                    "salvar uma criança prometida ao culto",
                    "descobrir por que os moradores desaparecem",
                    "enterrar o segredo do vilarejo de vez",
                ],
                "twists": [
                    "todos os moradores parecem saber o que vai acontecer",
                    "o guia que os trouxe sempre fez parte do ritual",
                    "a lenda local é mais antiga do que o próprio vilarejo",
                    "as vítimas voltam todas as noites",
                ],
            },
            "psicologico": {
                "roles": [
                    ("f", "a psiquiatra de um hospital desativado"),
                    ("m", "o escritor em crise criativa"),
                    ("f", "a estudante assombrada por sonhos recorrentes"),
                    ("m", "o porteiro de um prédio sem moradores"),
                    (None, "uma dupla de colegas de quarto"),
                ],
                "settings": [
                    "no edifício Solar das Sombras",
                    "num hospital psiquiátrico fechado",
                    "numa cidade onde todos os relógios pararam",
                    "num apartamento no décimo terceiro andar",
                ],
                "threats": [
                    "uma voz que sussurra os piores medos",
                    "um vizinho que sabe tudo sobre a rotina de todos",
                    "um duplo idêntico que aparece nos espelhos",
                    "uma memória que não pertence a ninguém",
                ],
                "goals": [
                    "provar que não está perdendo a sanidade",
                    "descobrir quem está por trás das perseguições",
                    "escapar de um ciclo que se repete toda noite",
                    "encontrar a saída de um lugar que muda de forma",
                ],
                "twists": [
                    "a realidade só muda quando ninguém está olhando",
                    "as gravações mostram coisas que nunca aconteceram",
                    "o diário encontrado foi escrito pela própria pessoa",
                    "ninguém mais parece perceber o que está acontecendo",
                ],
            },
        },
        "ficcao-cientifica": {
            "opera-espacial": {
                "roles": [
                    ("f", "a capitã da nave Aurora Boreal"),
                    ("m", "o engenheiro-chefe da estação Órion"),
                    ("f", "a diplomata da Federação Terrana"),
                    ("m", "o contrabandista de uma frota rebelde"),
                    (None, "a tripulação da nave de exploração Meridiano"),
                ],
                "settings": [
                    "a bordo da cargueira Calypso",
                    "na fronteira do setor Kepler",
                    "em um posto avançado na lua de Titã",
                    "durante uma travessia de décadas em hibernação",
                ],
                "threats": [
                    "uma frota alienígena em rota de colisão",
                    "uma inteligência artificial que tomou o controle da nave",
                    "um império que escraviza colônias inteiras",
                    "uma anomalia no espaço-tempo que devora planetas",
                ],
                "goals": [
                    "alertar a Federação antes da invasão",
                    "encontrar um novo lar para os colonos",
                    "restaurar os motores antes do impacto",
                    "negociar a paz com uma civilização desconhecida",
                ],
                "twists": [
                    "o sinal de socorro foi enviado do futuro",
                    "um dos tripulantes é um agente infiltrado",
                    "os alienígenas parecem entender cada palavra dita",
                    "o mapa estelar foi adulterado por alguém de dentro",
                ],
            },
            "cyberpunk": {
                "roles": [
                    ("f", "a hacker de uma favela vertical"),
                    ("m", "o detetive de androides"),
                    ("f", "a mercenária com implantes ilegais"),
                    ("m", "o engenheiro de memórias digitais"),
                    (None, "uma gangue de rebeldes conectados"),
                ],
                "settings": [
                    "na megacidade corporativa de Neo-Santos",
                    "no distrito de neon de Vila Pixel",
                    "dentro de uma rede neural proibida",
                    "nas torres da corporação Helix",
                ],
                "threats": [
                    "uma megacorporação que vende memórias",
                    "uma IA que controla ruas inteiras",
                    "um vírus que apaga a consciência dos usuários",
                    "um senhor do crime com um exército de ciborgues",
                ],
                "goals": [
                    "roubar o código-fonte que controla a cidade",
                    "libertar uma consciência presa na rede",
                    "expor o experimento secreto da corporação",
                    "desaparecer da rede antes que a corporação feche o cerco",
                ],
                "twists": [
                    "os implantes guardam uma memória de outra pessoa",
                    "o código foi escrito por alguém que já morreu",
                    "a própria corporação quer que o plano dê certo",
                    "o hacker mais procurado da rede nunca existiu",
                ],
            },
            "pos-apocaliptico": {
                "roles": [
                    ("f", "a sobrevivente de um abrigo subterrâneo"),
                    ("m", "o mensageiro entre as últimas cidades"),
                    ("f", "a engenheira de uma cidade murada"),
                    ("m", "o ex-soldado do antigo governo"),
                    (None, "uma caravana de refugiados"),
                ],
                "settings": [
                    "nas planícies áridas além do Muro Leste",
                    "na cidade murada de Último Refúgio",
                    "sob as ruínas de uma metrópole inundada",
                    "nas estradas radioativas do Cinturão Seco",
                ],
                "threats": [
                    "um regime que racionaliza o ar e a água",
                    "um bando de saqueadores com armas antigas",
                    "uma tempestade tóxica que avança a cada dia",
                    "uma máquina de guerra que ainda patrulha o deserto",
                ],
                "goals": [
                    "levar uma semente rara até o último jardim",
                    "encontrar a nascente que ainda não foi contaminada",
                    "reativar o antigo sistema de purificação",
                    "cruzar o deserto antes da próxima tempestade",
                ],
                "twists": [
                    "o governo sabe da existência de um planeta habitável",
                    "o mapa foi desenhado por quem causou o colapso",
                    "o último abrigo seguro é uma mentira",
                    "o inimigo mais perigoso está dentro do próprio grupo",
                ],
            },
        },
        "manga-fantasia": {
            "fantasia-epica": {
                "roles": [
                    ("m", "o jovem escudeiro do rei"),
                    ("f", "a princesa exilada do reino de Valoria"),
                    ("m", "o mago aprendiz da Torre de Cristal"),
                    ("f", "a caçadora de dragões"),
                    (None, "uma companhia de aventureiros recém-formada"),
                ],
                "settings": [
                    "no reino de Eldoria",
                    "nas montanhas geladas de Karn-Dur",
                    "na floresta encantada de Sylvanir",
                    "nas muralhas da cidade de Altaluz",
                ],
                "threats": [
                    "um dragão ancestral despertado por engano",
                    "um imperador que quer unir os reinos pela força",
                    "uma feiticeira que drena a magia do mundo",
                    "um exército de mortos-vivos comandado por um lich",
                ],
                "goals": [
                    "reunir os fragmentos de uma espada lendária",
                    "recuperar o trono usurpado da família",
                    "selar o portal antes da lua sangrenta",
                    "provar que a profecia estava errada",
                ],
                "twists": [
                    "a profecia fala de alguém do próprio grupo",
                    "o mentor sempre serviu ao inimigo",
                    "a espada exige um sacrifício de quem a empunha",
                    "o verdadeiro inimigo ainda nem mostrou o rosto",
                ],
            },
            "isekai": {
                "roles": [
                    ("m", "o estudante transportado para outro mundo"),
                    ("f", "a balconista de loja de conveniência invocada como heroína"),
                    ("m", "o programador que renasceu como mago"),
                    ("f", "a jogadora profissional presa num jogo de realidade virtual"),
                    (None, "uma turma inteira transportada para um reino mágico"),
                ],
                "settings": [
                    "no reino mágico de Arvandel",
                    "na guilda de aventureiros da cidade de Lumeria",
                    "no mundo em guerra de Ashtara",
                    "numa academia de heróis invocados",
                ],
                "threats": [
                    "um Rei Demônio que reina há mil anos",
                    "uma guilda que explora heróis invocados",
                    "uma deusa que esconde a verdade sobre a invocação",
                    "um exército de monstros que cresce a cada eclipse",
                ],
                "goals": [
                    "encontrar o caminho de volta para casa",
                    "dominar a habilidade especial recebida na invocação",
                    "reunir aliados antes da batalha final",
                    "descobrir por que a invocação escolheu justamente essa alma",
                ],
                "twists": [
                    "a divindade que realizou a invocação mentiu sobre tudo",
                    "voltar para casa exige abandonar a magia",
                    "o líder dos inimigos também veio do mundo original",
                    "a habilidade especial cobra um pedaço da memória de quem a usa",
                ],
            },
            "torneio-shonen": {
                "roles": [
                    ("m", "o jovem lutador de uma vila pobre"),
                    ("f", "a espadachim de um clã rival"),
                    ("m", "o discípulo do mestre lendário"),
                    ("f", "a herdeira de uma técnica proibida"),
                    (None, "uma equipe de lutadores iniciantes"),
                ],
                "settings": [
                    "no Grande Torneio das Cinco Nações",
                    "no dojo secreto da Montanha Nuvem",
                    "nas arenas subterrâneas de Ferrovale",
                    "no templo da Lua Partida",
                ],
                "threats": [
                    "um campeão invicto há dez anos",
                    "um clã que rouba técnicas de outros mestres",
                    "um rival de infância transformado em inimigo",
                    "uma seita que luta com um poder demoníaco",
                ],
                "goals": [
                    "vencer o torneio e honrar o clã",
                    "dominar a técnica final do mestre",
                    "salvar a vila com o prêmio da competição",
                    "provar o próprio valor perante o conselho",
                ],
                "twists": [
                    "o mestre escondeu a verdadeira fonte do poder",
                    "o torneio é uma fachada para um ritual sombrio",
                    "a técnica final cobra a vida de quem a usa",
                    "o adversário mais forte luta para proteger alguém",
                ],
            },
        },
    },
    # ------------------------------------------------------------------
    # INGLÊS (mesma estrutura e mesmo conteúdo narrativo, escrito em inglês)
    # ------------------------------------------------------------------
    "en": {
        "super-heroi": {
            "noir-urbano": {
                "roles": [
                    ("f", "a masked vigilante"),
                    ("m", "a retired detective"),
                    ("f", "an investigative journalist"),
                    ("m", "a disgraced ex-cop"),
                    (None, "a neighborhood vigilante group"),
                ],
                "settings": [
                    "in the harbor alleys of Shadow Bay",
                    "in the financial district of New Aurora",
                    "in the constant rain of Port Noir",
                    "on the rooftops of Gray City",
                ],
                "threats": [
                    "an arms trafficking ring run by the Baron",
                    "a corrupt mayor protected by mercenaries",
                    "a gang using stolen military technology",
                    "a serial killer who leaves playing cards at every crime scene",
                ],
                "goals": [
                    "expose the scheme before the election",
                    "protect a key witness until the trial",
                    "recover a file that incriminates half the city",
                    "find out who is funding the crimes",
                ],
                "twists": [
                    "the clues lead to someone inside the police department",
                    "the closest ally has been hiding a secret",
                    "every piece of evidence disappears without a trace",
                    "someone has been following every step from the start",
                ],
            },
            "cosmico": {
                "roles": [
                    ("m", "the guardian of a dying star"),
                    ("f", "the ambassador of a destroyed planet"),
                    ("f", "a soldier of an intergalactic fleet"),
                    ("m", "the last hero of an extinct race"),
                    (None, "a team of heroes from different worlds"),
                ],
                "settings": [
                    "in orbit around a collapsing star",
                    "aboard the Zenith orbital station",
                    "among the ruins of the planet Kharos",
                    "in the heart of the Scarlet Nebula",
                ],
                "threats": [
                    "a world devourer with an endless hunger",
                    "an expanding galactic empire",
                    "a cosmic entity that rewrites reality",
                    "an army of clones of the old emperor",
                ],
                "goals": [
                    "save Earth from annihilation",
                    "gather the relics that hold the universe together",
                    "prevent the collapse of the last living star",
                    "convince the free peoples to fight together",
                ],
                "twists": [
                    "the power everyone seeks lies inside one of the heroes",
                    "the enemy is an old ally from another age",
                    "the threat was created by the guardians of the universe themselves",
                    "the prophecy points to a traitor among the heroes",
                ],
            },
            "adolescente": {
                "roles": [
                    ("f", "a high school student who just gained powers"),
                    ("m", "a scholarship student with super strength"),
                    ("f", "an athlete who discovered a dangerous gift"),
                    ("m", "a boy who turns into a shadow when afraid"),
                    (None, "a student club with superpowers"),
                ],
                "settings": [
                    "at Northern Star High School",
                    "in the small town of Green Valley",
                    "during the state science championship",
                    "in the working-class district of Vila Nova",
                ],
                "threats": [
                    "a teacher with plans for world domination",
                    "a gang of college students in experimental armor",
                    "a corporation that kidnaps gifted teenagers",
                    "a villain who feeds on the powers of others",
                ],
                "goals": [
                    "hide the secret from parents and friends",
                    "master the powers before the prom",
                    "free the kidnapped classmates",
                    "discover the origin of the mutation",
                ],
                "twists": [
                    "the best friend is hiding a similar secret",
                    "the principal has known everything from the start",
                    "the powers grow stronger with every lie told",
                    "someone very close is already working for the enemy",
                ],
            },
        },
        "terror": {
            "casa-assombrada": {
                "roles": [
                    ("f", "a real estate agent"),
                    ("m", "the father of a family that just moved in"),
                    ("f", "a retired medium"),
                    ("m", "a night caretaker"),
                    (None, "a pair of newlyweds"),
                ],
                "settings": [
                    "in the abandoned mansion of the Albuquerque family",
                    "in an isolated colonial manor",
                    "in the old townhouse on Acacia Street",
                    "in an inn closed for decades",
                ],
                "threats": [
                    "a spirit that lives inside the walls",
                    "a presence that imitates the voices of the dead",
                    "a curse sealed by a former resident",
                    "a ghost child who never leaves the basement",
                ],
                "goals": [
                    "survive until dawn",
                    "find out what happened to the former residents",
                    "break the curse before the next full moon",
                    "escape from a house that lets no one leave",
                ],
                "twists": [
                    "the doors slam shut every time someone tries to leave",
                    "the voices in the walls know secrets nobody ever told",
                    "the mirror in the hallway shows who will be the next victim",
                    "one of the residents is no longer human",
                ],
            },
            "folk-rural": {
                "roles": [
                    ("f", "a schoolteacher newly arrived in the village"),
                    ("m", "a police officer from the neighboring town"),
                    ("f", "an anthropologist who studies local legends"),
                    ("m", "a widowed fisherman"),
                    (None, "a group of friends on a camping trip"),
                ],
                "settings": [
                    "in the isolated village of Saint Jude of the Woods",
                    "in a forest from which no one returns",
                    "on the island of Old Stone",
                    "among the cane fields of Hope Farm",
                ],
                "threats": [
                    "a cult that offers sacrifices to the forest",
                    "a creature that hunts on foggy nights",
                    "a traditional festival that demands blood",
                    "a curse passed down through generations",
                ],
                "goals": [
                    "leave the village before the winter festival",
                    "save a child promised to the cult",
                    "find out why the villagers keep disappearing",
                    "bury the secret of the village for good",
                ],
                "twists": [
                    "every villager seems to know what will happen",
                    "the guide who brought them was part of the ritual all along",
                    "the local legend is older than the village itself",
                    "the victims return every night",
                ],
            },
            "psicologico": {
                "roles": [
                    ("f", "a psychiatrist at a decommissioned hospital"),
                    ("m", "a writer in a creative crisis"),
                    ("f", "a student haunted by recurring dreams"),
                    ("m", "the doorman of a building with no tenants"),
                    (None, "a pair of roommates"),
                ],
                "settings": [
                    "in the Shadow Manor building",
                    "in a closed psychiatric hospital",
                    "in a city where all the clocks stopped",
                    "in an apartment on the thirteenth floor",
                ],
                "threats": [
                    "a voice that whispers their worst fears",
                    "a neighbor who knows every detail of their daily routine",
                    "an identical double that appears in the mirrors",
                    "a memory that belongs to no one",
                ],
                "goals": [
                    "prove they are not losing their mind",
                    "find out who is behind the stalking",
                    "escape a cycle that repeats every night",
                    "find the exit from a place that keeps changing shape",
                ],
                "twists": [
                    "reality only changes when nobody is looking",
                    "the recordings show things that never happened",
                    "the diary they found was written by themselves",
                    "nobody else seems to notice what is happening",
                ],
            },
        },
        "ficcao-cientifica": {
            "opera-espacial": {
                "roles": [
                    ("f", "the captain of the starship Aurora Borealis"),
                    ("m", "the chief engineer of Orion station"),
                    ("f", "a diplomat of the Terran Federation"),
                    ("m", "a smuggler of a rebel fleet"),
                    (None, "the crew of the exploration ship Meridian"),
                ],
                "settings": [
                    "aboard the freighter Calypso",
                    "on the border of the Kepler sector",
                    "at an outpost on the moon of Titan",
                    "during a decades-long journey in hibernation",
                ],
                "threats": [
                    "an alien fleet on a collision course",
                    "an artificial intelligence that took control of the ship",
                    "an empire that enslaves entire colonies",
                    "a spacetime anomaly that devours planets",
                ],
                "goals": [
                    "warn the Federation before the invasion",
                    "find a new home for the colonists",
                    "restore the engines before impact",
                    "negotiate peace with an unknown civilization",
                ],
                "twists": [
                    "the distress signal was sent from the future",
                    "one of the crew members is an undercover agent",
                    "the aliens seem to understand every word spoken",
                    "the star map was tampered with by someone on the inside",
                ],
            },
            "cyberpunk": {
                "roles": [
                    ("f", "a hacker from a vertical slum"),
                    ("m", "an android detective"),
                    ("f", "a mercenary with illegal implants"),
                    ("m", "a digital memory engineer"),
                    (None, "a gang of connected rebels"),
                ],
                "settings": [
                    "in the corporate megacity of Neo Santos",
                    "in the neon district of Pixel Town",
                    "inside a forbidden neural network",
                    "in the towers of the Helix corporation",
                ],
                "threats": [
                    "a megacorporation that sells memories",
                    "an AI that controls entire streets",
                    "a virus that erases the consciousness of its users",
                    "a crime lord with an army of cyborgs",
                ],
                "goals": [
                    "steal the source code that controls the city",
                    "free a consciousness trapped in the network",
                    "expose the secret experiment of the corporation",
                    "vanish from the network before the corporation closes in",
                ],
                "twists": [
                    "the implants hold a memory of someone else",
                    "the code was written by someone who is already dead",
                    "the corporation itself wants the plan to succeed",
                    "the most wanted hacker on the network never existed",
                ],
            },
            "pos-apocaliptico": {
                "roles": [
                    ("f", "a survivor of an underground bunker"),
                    ("m", "a messenger between the last cities"),
                    ("f", "an engineer of a walled city"),
                    ("m", "a former soldier of the old government"),
                    (None, "a caravan of refugees"),
                ],
                "settings": [
                    "on the arid plains beyond the Eastern Wall",
                    "in the walled city of Last Refuge",
                    "beneath the ruins of a flooded metropolis",
                    "on the radioactive roads of the Dry Belt",
                ],
                "threats": [
                    "a regime that rations air and water",
                    "a band of raiders with old weapons",
                    "a toxic storm that advances every day",
                    "a war machine that still patrols the desert",
                ],
                "goals": [
                    "carry a rare seed to the last garden",
                    "find the spring that has not been contaminated",
                    "reactivate the old purification system",
                    "cross the desert before the next storm",
                ],
                "twists": [
                    "the government knows about a habitable planet",
                    "the map was drawn by whoever caused the collapse",
                    "the last safe shelter is a lie",
                    "the most dangerous enemy is inside the group itself",
                ],
            },
        },
        "manga-fantasia": {
            "fantasia-epica": {
                "roles": [
                    ("m", "the young squire of the king"),
                    ("f", "the exiled princess of the kingdom of Valoria"),
                    ("m", "an apprentice mage of the Crystal Tower"),
                    ("f", "a dragon hunter"),
                    (None, "a newly formed company of adventurers"),
                ],
                "settings": [
                    "in the kingdom of Eldoria",
                    "in the frozen mountains of Karn Dur",
                    "in the enchanted forest of Sylvanir",
                    "on the walls of the city of Brightspire",
                ],
                "threats": [
                    "an ancient dragon awakened by mistake",
                    "an emperor who wants to unite the kingdoms by force",
                    "a sorceress who drains the magic of the world",
                    "an army of the undead commanded by a lich",
                ],
                "goals": [
                    "gather the fragments of a legendary sword",
                    "reclaim the usurped throne of the family",
                    "seal the portal before the blood moon",
                    "prove that the prophecy was wrong",
                ],
                "twists": [
                    "the prophecy speaks of someone in the group itself",
                    "the mentor has always served the enemy",
                    "the sword demands a sacrifice from whoever wields it",
                    "the true enemy has not even shown their face yet",
                ],
            },
            "isekai": {
                "roles": [
                    ("m", "a student transported to another world"),
                    ("f", "a convenience store clerk summoned as a hero"),
                    ("m", "a programmer reborn as a mage"),
                    ("f", "a professional gamer trapped in a virtual reality game"),
                    (None, "an entire class transported to a magical kingdom"),
                ],
                "settings": [
                    "in the magical kingdom of Arvandel",
                    "in the adventurers guild of the city of Lumeria",
                    "in the war-torn world of Ashtara",
                    "in an academy for summoned heroes",
                ],
                "threats": [
                    "a Demon King who has ruled for a thousand years",
                    "a guild that exploits summoned heroes",
                    "a goddess who hides the truth about the summoning",
                    "an army of monsters that grows with every eclipse",
                ],
                "goals": [
                    "find the way back home",
                    "master the special ability received in the summoning",
                    "gather allies before the final battle",
                    "find out why the summoning chose this very soul",
                ],
                "twists": [
                    "the deity who performed the summoning lied about everything",
                    "going home requires giving up magic",
                    "the leader of the enemies also came from the original world",
                    "the special ability takes a piece of the memory of whoever uses it",
                ],
            },
            "torneio-shonen": {
                "roles": [
                    ("m", "a young fighter from a poor village"),
                    ("f", "a swordswoman of a rival clan"),
                    ("m", "a disciple of the legendary master"),
                    ("f", "an heir to a forbidden technique"),
                    (None, "a team of novice fighters"),
                ],
                "settings": [
                    "in the Grand Tournament of the Five Nations",
                    "in the secret dojo of Cloud Mountain",
                    "in the underground arenas of Ironvale",
                    "in the temple of the Broken Moon",
                ],
                "threats": [
                    "a champion undefeated for ten years",
                    "a clan that steals techniques from other masters",
                    "a childhood rival turned enemy",
                    "a sect that fights with a demonic power",
                ],
                "goals": [
                    "win the tournament and honor the clan",
                    "master the final technique of the master",
                    "save the village with the prize of the competition",
                    "prove their worth before the council",
                ],
                "twists": [
                    "the master hid the true source of the power",
                    "the tournament is a front for a dark ritual",
                    "the final technique costs the life of whoever uses it",
                    "the strongest opponent fights to protect someone",
                ],
            },
        },
    },
}

# Frases-tempero dos HÍBRIDOS: independentes do cenário, escritas para
# combinar com qualquer premissa de outro gênero (ex: um "toque" de terror
# dentro de uma história de ficção científica).
FLAVOR = {
    "pt": {
        "super-heroi": [
            "Em meio a tudo isso, pessoas comuns começam a manifestar superpoderes instáveis.",
            "Um herói mascarado surge nas sombras, e ninguém sabe de que lado o forasteiro está.",
            "Uma mutação misteriosa concede habilidades extraordinárias a quem entra em contato com ela.",
            "A identidade secreta de um dos envolvidos pode mudar o rumo de tudo.",
        ],
        "terror": [
            "Algo sobrenatural passa a se alimentar do medo de todos ao redor.",
            "Pesadelos coletivos começam a se tornar reais durante a noite.",
            "Uma presença invisível observa cada passo, esperando a hora de atacar.",
            "Cada vítima desaparece sem deixar rastros, e ninguém ousa falar sobre isso.",
        ],
        "ficcao-cientifica": [
            "Aos poucos, descobre-se que a realidade pode ser apenas uma simulação.",
            "Uma inteligência artificial observa tudo e aprende com cada erro humano.",
            "Sinais de uma tecnologia avançada demais indicam que não estão sozinhos.",
            "Uma linha do tempo alternativa começa a invadir o presente.",
        ],
        "manga-fantasia": [
            "Uma magia antiga e proibida volta a despertar depois de séculos.",
            "Uma profecia esquecida começa a se cumprir, passo a passo.",
            "Criaturas lendárias que todos julgavam extintas voltam a ser avistadas.",
            "Um pacto selado com um espírito ancestral cobra o seu preço.",
        ],
    },
    "en": {
        "super-heroi": [
            "Meanwhile, ordinary people begin to manifest unstable superpowers.",
            "A masked hero emerges from the shadows, and nobody knows whose side the stranger is on.",
            "A mysterious mutation grants extraordinary abilities to anyone who comes into contact with it.",
            "The secret identity of one of those involved could change everything.",
        ],
        "terror": [
            "Something supernatural begins to feed on the fear of everyone around.",
            "Collective nightmares start to become real at night.",
            "An invisible presence watches every step, waiting for the right moment to strike.",
            "Every victim vanishes without a trace, and nobody dares to talk about it.",
        ],
        "ficcao-cientifica": [
            "Little by little, it becomes clear that reality may be only a simulation.",
            "An artificial intelligence watches everything and learns from every human mistake.",
            "Signs of a technology far too advanced suggest that they are not alone.",
            "An alternate timeline begins to invade the present.",
        ],
        "manga-fantasia": [
            "An ancient and forbidden magic awakens once more after centuries.",
            "A forgotten prophecy begins to come true, step by step.",
            "Legendary creatures believed extinct are sighted again.",
            "A pact sealed with an ancestral spirit demands its price.",
        ],
    },
}

# Nomes próprios dos personagens. São neutros em relação ao gênero literário
# (um nome não indica terror ou ficção científica), então servem de "ruído"
# saudável: o modelo precisa aprender a ignorá-los.
NAMES = {
    "pt": {
        "f": ["Marina", "Helena", "Beatriz", "Clara", "Larissa", "Iara", "Valentina", "Júlia", "Nara", "Sofia", "Luíza", "Aline"],
        "m": ["Caio", "Rafael", "Davi", "Theo", "Otávio", "Murilo", "Bento", "Henrique", "Lucas", "Heitor", "Gael", "Enzo"],
        "surnames": ["Vasconcelos", "Brandão", "Albuquerque", "Tavares", "Moura", "Siqueira", "Penha", "Cordeiro", "Falcão", "Medeiros", "Andrade", "Campos"],
    },
    "en": {
        "f": ["Helena", "Clara", "Nora", "Iris", "Tessa", "Maya", "Lena", "Rosa", "Alice", "Ingrid", "Brünhilde"],
        "m": ["Marcus", "Elias", "Theo", "Victor", "Jonah", "Silas", "Rafael", "Dorian", "Felix", "Ivan", "Hal", "Clark", "Bruce", "Peter"],
        "surnames": ["Hale", "Brandt", "Okafor", "Voss", "Marlowe", "Quinn", "Reyes", "Calloway", "Ashford", "Moreau", "Whitaker", "Novak", "Wayne", "Kent", "Jordan"],
    },
}

# Moldes de frase. As CHAVES dos placeholders são nomes internos do código
# (hero, setting, threat, goal, twist) e iguais para todas as línguas; o
# sufixo _cap indica a versão com a primeira letra maiúscula (início de frase).
TEMPLATES = {
    "pt": [
        "{setting_cap}, {hero} precisa {goal}. Só que {twist}.",
        "{hero_cap} enfrenta {threat} {setting} com um único objetivo: {goal}.",
        "Quando {threat} surge {setting}, {hero} larga tudo para {goal}.",
        "{setting_cap}, {threat} ameaça tudo. {hero_cap} tenta {goal}, mas {twist}.",
        "Para {goal}, {hero} terá de enfrentar {threat} {setting}.",
        "{hero_cap} nunca imaginou encontrar {threat} {setting}. Agora a missão é {goal}, e {twist}.",
    ],
    "en": [
        "{setting_cap}, {hero} must {goal}. But {twist}.",
        "{hero_cap} faces {threat} {setting} with a single goal: to {goal}.",
        "When {threat} appears {setting}, {hero} drops everything to {goal}.",
        "{setting_cap}, {threat} threatens everything. {hero_cap} tries to {goal}, but {twist}.",
        "To {goal}, {hero} will have to face {threat} {setting}.",
        "{hero_cap} never expected to find {threat} {setting}. Now the mission is to {goal}, and {twist}.",
    ],
}

LANGUAGES = list(SUBGENRES.keys())
# Comic Genre Classifier

Classificador de gênero/tema de quadrinhos a partir de texto (sinopses/descrições),
usando embeddings treinados do zero e uma rede neural em PyTorch. Dataset gerado
sinteticamente para os gêneros: **super-herói, terror/horror, ficção científica e
mangá/fantasia**.

Foi feito usando a linguagem Python com o ‘framework’ PyTorch para o processamento e treinamento de dados e FastAPI para a criação da API.

## Estrutura do projeto

```
comic-genre-classifier/
├── data/
│   ├── raw/          # dataset sintético gerado (etapa 2)
│   └── processed/    # dados tokenizados/prontos para treino
├── models/            # checkpoints do modelo treinado
├── notebooks/         # exploração e experimentos
├── src/
│   └── comic_classifier/
│       └── static/
│            └── index.html       # tela para poder inserir os textos
│       ├── data_generation.py   # geração do dataset sintético (etapa 2)
│       ├── preprocessing.py     # tokenização e vocabulário (etapa 3)
│       ├── model.py             # arquitetura da rede (etapa 4)
│       ├── train.py             # loop de treino e avaliação (etapa 5)
│       └── api.py               # serviço FastAPI (etapa 6)
├── tests/
│    └── test_api.py                # Realiza testes do api.py
│    └── test_data_generation.py    # Realiza testes da geração de dados.
│    └── test_model.py              # Realiza testes do modelo     
│    └── test_preprocessing.py      # Realiza testes de pré-processamento.
├── requirements.txt
├── Dockerfile  # Configuração do ambiente (etapa 1)
└── README.md
```

## Setup local
Só leia o Dockerfile que ele faz toda a configuração automaticamente

```bash
docker build -t comic-genre-classifier .
docker run -p 8000:8000 comic-genre-classifier
```

## Roteiro do projeto

1.  Configurar ambiente
2.  Gerar dataset sintético
3.  Pré-processar e construir vocabulário
4.  Construir a rede neural
5.  Treinar e avaliar
6.  Realizar testes
7. Empacotar como API (FastAPI + Docker)

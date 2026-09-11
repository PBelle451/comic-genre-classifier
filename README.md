# Comic Genre Classifier

Classificador de gênero/tema de quadrinhos a partir de texto (sinopses/descrições),
usando embeddings treinados do zero e uma rede neural em PyTorch. Dataset gerado
sinteticamente para os gêneros: **super-herói, terror/horror, ficção científica e
mangá/fantasia**.

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
│       ├── data_generation.py   # geração do dataset sintético (etapa 2)
│       ├── preprocessing.py     # tokenização e vocabulário (etapa 3)
│       ├── model.py             # arquitetura da rede (etapa 4)
│       ├── train.py             # loop de treino e avaliação (etapa 5)
│       └── api.py               # serviço FastAPI (etapa 6)
├── tests/
├── requirements.txt
└── README.md
```

## Setup local

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Roteiro do projeto

1. ✅ Configurar ambiente
2. ⬜ Gerar dataset sintético
3. ⬜ Pré-processar e construir vocabulário
4. ⬜ Construir a rede neural
5. ⬜ Treinar e avaliar
6. ⬜ Empacotar como API (FastAPI + Docker)

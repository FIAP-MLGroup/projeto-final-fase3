# Medições de Radar API

API para registro e consulta de medições de radar de veículos.

## O que a API faz?
Esta API permite registrar medições de velocidade de veículos (placa, localização, velocidade, data/hora) e consultar os registros salvos em um banco de dados relacional.

## Dependências
- Python 3.11
- FastAPI
- SQLModel
- SQLAlchemy
- Pydantic-Settings

## Como executar
1. Instale as dependências (recomenda-se ambiente virtual):
   ```bash
   pip install fastapi sqlmodel sqlalchemy pydantic-settings
   ```
2. Defina a variável de ambiente `DATABASE_URL` para conexão no banco PostgreSQL. É possível definir tanto usando o arquivo .env como diretamente via variável de ambiente:
   ```bash
   export DATABASE_URL=postgresql+asyncpg://<user>:<pass>@<ip>:<port>/<database_name>
   ```
3. Rode o servidor:
   ```bash
   uvicorn app-api:app --reload
   ```

## Endpoints
- `GET /healthz` — Health check (verifica se a API está online)
- `POST /medicoes` — Registra uma nova medição de radar
- `GET /medicoes` — Lista medições cadastradas (parâmetro opcional: `limit`)

## Variáveis de ambiente
- `DATABASE_URL`: string de conexão do banco de dados (ex: `postgresql+asyncpg://<user>:<pass>@<ip>:<port>/<database_name>`)

## Exemplo de chamada POST
```bash
curl -X POST http://localhost:8000/medicoes \
  -H 'Content-Type: application/json' \
  -d '{
    "placa": "QNA3053",
    "latitude": -22.953702,
    "longitude": -43.375778,
    "velocidade": 20,
    "timestamp_deteccao": "2025-07-23 09:11"
  }'
```

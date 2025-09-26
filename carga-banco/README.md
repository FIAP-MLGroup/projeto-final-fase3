# Programa de Carga de Dados

Este programa lê um arquivo CSV com medições de radar e envia os dados para a API de medições via requisições HTTP POST.

## O que o programa faz?
- Lê o arquivo `OCR_CETRIO_10klinhas.csv`.
- Para cada linha, gera uma data/hora aleatória baseada na data do registro.
- Envia os dados para o endpoint `/medicoes` da API (por padrão: `http://127.0.0.1:8000/medicoes`).

## Como executar
1. Instale as dependências:
   ```bash
   pip install pandas requests
   ```
2. Certifique-se de que a API de medições está rodando.
3. Execute o script:
   ```bash
   python carga.py
   ```

## Dependências
- pandas
- requests
- Python 3.11

O arquivo `OCR_CETRIO_10klinhas.csv` deve estar no mesmo diretório do script.

# Projeto de Análise Preditiva de Clonagem de Veículos

Este projeto utiliza técnicas de machine learning para detectar possíveis casos de clonagem de placas de veículos, apresentando os resultados em uma interface gráfica interativa construída com Streamlit.

## O que o programa faz?
- Lê dados de medições de radar de um banco de dados relacional.
- Processa os dados para identificar padrões suspeitos de clonagem de placas.
- Utiliza o modelo Isolation Forest para detectar anomalias.
- Exibe os resultados em mapas e tabelas interativas na interface web.

## Como executar
1. Instale as dependências:
   ```bash
   pip install streamlit pandas scikit-learn geopy pydeck
   ```
2. Configure o acesso ao banco de dados PostgreSQL no arquivo `.streamlit/secrets.toml`.
3. Execute o aplicativo:
   ```bash
   streamlit run predicao-clonagem-app.py
   ```

## Dependências
- streamlit
- pandas
- scikit-learn
- geopy
- pydeck
- Banco de dados PostgreSQL configurado

Acesse a interface gráfica pelo navegador, normalmente em `http://localhost:8501`.

# Assistente de Estudos

Este projeto é um assistente de estudos construído com [Dioxus](https://dioxuslabs.com/) (frontend em Rust) e uma API backend (por padrão, conectada a um endpoint local). O assistente permite que usuários enviem perguntas e recebam respostas, mantendo um histórico de conversas.

## Funcionalidades

- Interface web simples para interação com o assistente.
- Histórico de mensagens entre usuário e assistente.
- Integração com backend via API REST.

## Como rodar

1. **Clone o repositório:**
   ```sh
   git clone <url-do-repo>
   cd as
   ```

2. **Configure as variáveis de ambiente:**
   - Edite o arquivo `.env` para definir a URL da API e outras chaves necessárias.

3. **Rode o frontend:**
   - Certifique-se de ter o Rust instalado.
   - Execute:
     ```sh
     cargo run
     ```

4. **Rode o backend:**
   - Siga as instruções do backend (não incluídas neste repositório).
   - Se o backend for em Python (FastAPI), você pode rodar com [Uvicorn](https://www.uvicorn.org/):
     ```sh
     uvicorn main:app --reload
     ```
   - Certifique-se de estar na pasta correta e que o arquivo `main.py` contenha o objeto `app`.

## Estrutura dos arquivos

- `main.rs`: Código principal do frontend Dioxus.
- `.env`: Variáveis de ambiente (exemplo: URL da API, chaves).
- `style/style.css`: Estilos da interface.
- `README.md`: Este arquivo.

## Observações

- Altere a variável `API_URL` no `.env` para apontar para o backend desejado (local ou produção).
- Não compartilhe sua chave de API publicamente.

---
Projeto para fins educacionais.

## Licença

Este projeto está licenciado sob os termos da licença MIT.  
Consulte o arquivo `LICENSE` para mais detalhes.

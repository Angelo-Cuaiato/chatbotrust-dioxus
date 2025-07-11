from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv
from typing import Optional, List
import redis # Importe a biblioteca redis
import json # Importe a biblioteca json para serialização

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Inicializa a aplicação FastAPI
app = FastAPI()

# Configura o CORS para permitir requisições do seu frontend
# Em produção, você pode querer restringir as origens
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MUDANÇA AQUI: CONEXÃO OPCIONAL COM O REDIS ---
redis_url = os.getenv("REDIS_URL")
r = None  # Inicializa a conexão Redis como Nula
conversation_histories = {} # Dicionário para fallback

if redis_url:
    print("Conectando ao Redis...")
    try:
        # Conecta ao Redis se a URL for encontrada
        r = redis.from_url(redis_url, decode_responses=True)
        r.ping() # Verifica se a conexão foi bem-sucedida
        print("Conexão com o Redis bem-sucedida.")
    except redis.exceptions.ConnectionError as e:
        print(f"AVISO: Não foi possível conectar ao Redis: {e}. Usando memória local.")
        r = None
else:
    print("AVISO: REDIS_URL não encontrada. Usando memória local para o histórico (não persistente).")


# Inicializa o cliente da OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define o modelo de dados para a requisição (não precisa mais de 'subject')
class Question(BaseModel):
    question: str

# Define o modelo para uma única mensagem no histórico
class Message(BaseModel):
    role: str
    content: str

# Define o modelo de dados para a resposta, que agora é uma lista de mensagens
class Answer(BaseModel):
    history: List[Message]

# Dicionário agora só contém o prompt Geral
SUBJECT_PROMPTS = {
    "Geral": "Você é um assistente de estudos geral, pronto para ajudar com qualquer matéria de forma clara e objetiva.",
}

@app.post("/api/chat", response_model=Answer)
async def chat(question_data: Question):
    """
    Recebe uma pergunta, envia para a API da OpenAI e retorna a resposta.
    """
    question = question_data.question
    if not question:
        raise HTTPException(status_code=400, detail="Por favor, forneça uma pergunta válida.")

    # O sistema agora só tem um modo: "Geral"
    subject = "Geral"
    system_prompt = SUBJECT_PROMPTS[subject]

    # --- LÓGICA DE LEITURA DO HISTÓRICO ---
    history = []
    redis_key = f"history:{subject}" # A chave do histórico agora é fixa
    if r: # Se a conexão com o Redis existir
        stored_history = r.get(redis_key)
        if stored_history:
            history = json.loads(stored_history)
    else: # Senão, usa o dicionário em memória
        history = conversation_histories.get(subject, [])

    # Monta a lista de mensagens completa para enviar à API
    messages_to_send = [
        {"role": "system", "content": system_prompt}
    ] + history + [
        {"role": "user", "content": question}
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages_to_send,
            max_tokens=250
        )
        answer_text = response.choices[0].message.content.strip()

        # Adiciona a nova interação ao histórico
        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": answer_text})

        # --- LÓGICA DE GRAVAÇÃO DO HISTÓRICO ---
        if r: # Se a conexão com o Redis existir
            r.set(redis_key, json.dumps(history))
            r.expire(redis_key, 86400)
        else: # Senão, usa o dicionário em memória
            conversation_histories[subject] = history

        return Answer(history=history)
    except Exception as e:
        print(f"Erro: {e}")
        raise HTTPException(status_code=500, detail="Erro ao processar a solicitação.")

# Para rodar localmente, você usaria o uvicorn no terminal:
# uvicorn app:app --reload --port 5000
# O bloco if __name__ == '__main__' não é mais necessário para o deploy.

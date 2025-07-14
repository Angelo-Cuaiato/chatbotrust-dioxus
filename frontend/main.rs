use dioxus::prelude::*;
use reqwest::Client;
use serde::Deserialize;
use serde_json::json;

fn main() {
    launch(app);
}

// Define a estrutura para uma única mensagem do chat
#[derive(Clone, Deserialize, PartialEq)]
struct ChatMessage {
    role: String,
    content: String,
}

// Define a estrutura da resposta da API, que agora contém um histórico
#[derive(Deserialize)]
struct ApiResponse {
    history: Vec<ChatMessage>,
}

fn app() -> Element {
    let mut input = use_signal(String::new);
    let mut chat_history = use_signal(Vec::<ChatMessage>::new);

    rsx! {
        style { {include_str!("style/style.css")} }
        div {
            class: "container",
            h1 { "Assistente de Estudos" }

            textarea {
                class: "input-box",
                placeholder: "Digite sua pergunta...",
                value: "{input}",
                oninput: move |e| input.set(e.value()),
            }
            button {
                class: "send-button",
                onclick: move |_| {
                    let current_input = input.read().clone();
                    spawn(async move {
                        if let Ok(res) = send_question(&current_input).await {
                            chat_history.set(res);
                            input.set("".to_string());
                        }
                    });
                },
                "Enviar"
            }
            // --- MUDANÇA AQUI ---
            // A caixa de resposta agora itera sobre o histórico
            div {
                class: "response-box",
                // Itera sobre cada mensagem no histórico
                for message in chat_history.read().iter() {
                    // Aplica uma classe diferente para o usuário e para o assistente
                    div {
                        class: "chat-message {message.role}",
                        p { "{message.content}" }
                    }
                }
            }
        }
    }
}

// A função agora só recebe a pergunta como argumento.
async fn send_question(question: &str) -> Result<Vec<ChatMessage>, reqwest::Error> {
    let client = Client::new();
    let res = client.post("") // Muda para url de producao local ou online
        // O JSON enviado agora contém apenas a pergunta.
        .json(&json!({ "question": question }))
        .send()
        .await?;

    // Deserializa a resposta da API
    let data: ApiResponse = res.json().await?;
    // Retorna o histórico
    Ok(data.history)
}

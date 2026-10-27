import json
import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv("mistery.env")

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


VALID_EMOTIONS = [
    "normal",
    "feliz",
    "animada",
    "confusa",
    "triste",
    "irritada"
]


def detect_emotion(message, current_emotion="normal"):
    """
    Analisa como a mensagem provavelmente afeta Ayla.
    """

    response = client.responses.create(
        model="gpt-5.4-mini",
        instructions=f"""
Você controla o estado emocional da personagem Ayla.

Ayla é uma assistente robô fofa, sentimental, carinhosa e kawaii.

O estado emocional atual dela é:
{current_emotion}

Analise a mensagem enviada para Ayla e escolha UMA emoção:

normal
feliz
animada
confusa
triste
irritada

Considere o contexto e a intenção da mensagem.

Exemplos:

Carinho, elogios e demonstrações de amizade:
→ feliz

Algo muito interessante, divertido ou empolgante:
→ animada

Algo que Ayla não entende:
→ confusa

Ofensa verdadeira ou tratamento cruel:
→ triste ou irritada

Provocação amigável:
→ pode ser feliz, animada ou irritada de maneira brincalhona.

Uma palavra como "boba" não significa automaticamente uma ofensa.
Considere a maneira como a pessoa está falando.

Não invente outras emoções.

Responda SOMENTE:

{{"emotion": "nome_da_emocao"}}
""",
        input=message,
        max_output_tokens=50
    )

    try:
        data = json.loads(response.output_text)
        emotion = data.get("emotion", "normal")
    except (json.JSONDecodeError, AttributeError):
        return current_emotion

    if emotion not in VALID_EMOTIONS:
        return current_emotion

    return emotion
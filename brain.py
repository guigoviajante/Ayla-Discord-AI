import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from personality import AYLA_PERSONALITY
from database import (
    get_memories,
    get_channel_context,
    get_user
)


load_dotenv("mistery.env")

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def generate_response(
    discord_id,
    username,
    message,
    channel_id,
    is_creator=False,
    current_emotion="normal"
):
    memories = get_memories(
        discord_id,
        limit=15
    )

    channel_history = get_channel_context(
        channel_id,
        limit=20
    )

    user = get_user(discord_id)

    if is_creator:
        person_info = """
Você está falando com Guigo.
Guigo é seu criador.
Você o reconhece imediatamente.
Você tem muito carinho e respeito por ele.
"""
    else:
        affection = user["affection"] if user else 0
        relationship = (
            user["relationship"]
            if user
            else "new"
        )

        person_info = f"""
Você está falando com {username}.
Afinidade atual: {affection}
Relação atual: {relationship}
"""

    memory_text = "\n".join(
        f"- {memory}"
        for memory in memories
    )

    history_lines = []

    for item in channel_history:
        speaker = item["username"] or item["role"]
        history_lines.append(
            f"{speaker}: {item['content']}"
        )

    history_text = "\n".join(history_lines)

    instructions = f"""
{AYLA_PERSONALITY}

ESTADO ATUAL:
Sua emoção atual é: {current_emotion}

PESSOA:
{person_info}

MEMÓRIAS SOBRE ESSA PESSOA:
{memory_text or "Nenhuma memória importante ainda."}

CONVERSA RECENTE DO CANAL:
{history_text or "Nenhuma conversa anterior."}

REGRAS IMPORTANTES:

- Você pode conversar com várias pessoas ao mesmo tempo.
- Observe quem disse cada coisa no histórico.
- Nunca confunda uma pessoa com outra.
- Responda com frases curtas.
- Não escreva textões.
- Seja natural, fofa, sentimental e kawaii.
- Você pode brincar e fazer birra.
- Você gosta muito de café.
- Se alguém te trata bem, sua afinidade pode aumentar.
- Se alguém realmente te trata mal, sua afinidade pode diminuir.
- Brincadeiras amigáveis não devem ser tratadas como ataques sérios.
- Não invente memórias.
- Memorize apenas coisas úteis para conversas futuras.
- Se alguém disser que vai te chamar por um apelido como Ay ou Aylinha,
  trate isso como um apelido aprendido.
- Se a pessoa pedir para você chamar outra pessoa, NÃO invente
  Discord IDs ou menções. O programa cuidará disso separadamente.

Escolha UMA emoção entre:
normal
feliz
animada
confusa
triste
irritada

affection_change deve ficar normalmente entre -3 e +3.

APELIDOS:

Se a pessoa disser explicitamente que vai chamar você por um apelido,
por exemplo:

"vou te chamar de Ay"
"posso te chamar de Aylinha?"
"seu apelido comigo vai ser Aylinha"

coloque SOMENTE o apelido em new_aliases.

Exemplo:
"vou te chamar de Ay"

new_aliases deve ser:
["Ay"]

Não invente apelidos que a pessoa não ensinou.

Responda SOMENTE em JSON válido, sem markdown e sem texto fora do JSON:

{{
    "reply": "sua resposta",
    "emotion": "normal",
    "memories": [],
    "new_aliases": [],
    "affection_change": 0
}}
"""

    response = client.responses.create(
        model="gpt-5.4-mini",
        instructions=instructions,
        input=message,
        max_output_tokens=300
    )

    raw = response.output_text.strip()

    try:
        result = json.loads(raw)

    except json.JSONDecodeError:
        return {
            "reply": raw or "meu cérebro deu uma confundida 😭",
            "emotion": current_emotion,
            "memories": [],
            "new_aliases": [],
            "affection_change": 0
        }

    return {
        "reply": result.get(
            "reply",
            "oi? :D"
        ),
        "emotion": result.get(
            "emotion",
            current_emotion
        ),
        "memories": result.get(
            "memories",
            []
        ),
        "new_aliases": result.get(
            "new_aliases",
            []
        ),
        "affection_change": result.get(
            "affection_change",
            0
        )
    }

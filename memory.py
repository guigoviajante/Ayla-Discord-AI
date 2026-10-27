import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from database import connect


load_dotenv("mistery.env")

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def extract_memories(discord_id, message):
    """
    Analisa uma mensagem e decide se existe algo importante
    que Ayla deveria lembrar sobre essa pessoa.
    """

    response = client.responses.create(
        model="gpt-5.4-mini",
        instructions="""
Você é o sistema de memória da Ayla.

Analise a mensagem recebida e identifique somente informações
que seriam úteis para Ayla lembrar em conversas futuras.

Exemplos de coisas importantes:
- nome ou apelido da pessoa;
- apelidos que a pessoa deu para Ayla;
- gostos e preferências;
- animais de estimação;
- hobbies;
- acontecimentos pessoais importantes;
- relações entre pessoas;
- promessas ou planos relevantes;
- coisas que a pessoa explicitamente pediu para Ayla lembrar.

Não memorize mensagens banais como:
"oi", "kkkk", "sim", "não", "beleza", cumprimentos ou frases
sem informação útil para o futuro.

Não invente informações.

Responda SOMENTE com JSON neste formato:

{"memories": []}

ou:

{"memories": ["memória 1", "memória 2"]}
""",
        input=message,
        max_output_tokens=200
    )

    try:
        data = json.loads(response.output_text)
        memories = data.get("memories", [])
    except (json.JSONDecodeError, AttributeError):
        return []

    for memory in memories:
        save_memory(discord_id, memory)

    return memories


def save_memory(discord_id, memory):
    connection = connect()
    cursor = connection.cursor()

    # Evita salvar exatamente a mesma memória duas vezes
    cursor.execute("""
        SELECT id
        FROM memories
        WHERE discord_id = ?
        AND LOWER(memory) = LOWER(?)
    """, (
        discord_id,
        memory
    ))

    existing = cursor.fetchone()

    if existing is None:
        cursor.execute("""
            INSERT INTO memories (
                discord_id,
                memory,
                importance,
                created_at
            )
            VALUES (?, ?, ?, datetime('now'))
        """, (
            discord_id,
            memory,
            1
        ))

    connection.commit()
    connection.close()
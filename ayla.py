import os
import random
import asyncio
from datetime import datetime, timedelta
from pathlib import Path

import discord
from discord import app_commands
from discord.ext import tasks
from dotenv import load_dotenv

from database import (
    create_tables,
    remember_user,
    save_message,
    save_memory,
    change_affection,
    get_user,
    find_user_by_name,
    get_friends,
    get_emotion,
    set_emotion,
    update_activity,
    get_aliases,
    save_alias,
    can_call_user,
    mark_called,
    mark_ignored,
    reset_ignored,
)

from brain import generate_response


# ============================================================
# CONFIGURAÇÃO
# ============================================================

load_dotenv("mistery.env")

TOKEN = os.getenv("DISCORD_TOKEN")

GUIGO_ID = int(os.getenv("GUIGO_DISCORD_ID", "0"))

ASSETS = Path(__file__).parent / "assets"

EMOTION_IMAGES = {
    "normal": ASSETS / "ayla_normal.png",
    "feliz": ASSETS / "ayla_feliz.png",
    "animada": ASSETS / "ayla_animada.png",
    "confusa": ASSETS / "ayla_confusa.png",
    "triste": ASSETS / "ayla_triste.png",
    "irritada": ASSETS / "ayla_irritada.png"
}

create_tables()


# ============================================================
# DISCORD
# ============================================================

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(
    intents=intents
)

tree = app_commands.CommandTree(client)


# ============================================================
# ESTADO
# ============================================================

VALID_EMOTIONS = {
    "normal",
    "feliz",
    "animada",
    "confusa",
    "triste",
    "irritada"
}

ayla_emotion = get_emotion()

# Última atividade observada no Discord
last_server_activity = datetime.now()

# Último canal onde houve conversa
last_channel = None

# Impede Ayla de chamar alguém a cada 15 minutos
last_initiative = None

# Pessoas que Ayla chamou recentemente
recently_called = set()

# Pessoa -> horário em que Ayla tomou iniciativa.
# Se a pessoa não responder em 30 minutos, conta como ignorada.
pending_initiatives = {}

# Canal -> horário até quando Ayla considera
# que ainda está participando da conversa
active_conversations = {}

# Uma fila/lock por canal
channel_locks = {}


# ============================================================
# STATUS
# ============================================================

async def update_status():

    status_messages = {
        "normal": "☕ Tomando café",
        "feliz": "🌸 Feliz",
        "animada": "✨ Animada!!",
        "confusa": "❓ Confusa...",
        "triste": "🌧️ Triste :(",
        "irritada": "💢 Irritada >:("
    }

    activity = discord.CustomActivity(
        name=status_messages.get(
            ayla_emotion,
            "☕ Tomando café"
        )
    )

    await client.change_presence(
        status=discord.Status.online,
        activity=activity
    )


# ============================================================
# DETECTAR SE AYLA FOI CHAMADA
# ============================================================

def ayla_was_called(message):
    text = message.content.lower()

    if "ayla" in text:
        return True

    if client.user in message.mentions:
        return True

    if (
        message.reference
        and message.reference.resolved
        and isinstance(message.reference.resolved, discord.Message)
    ):
        referenced = message.reference.resolved

        if referenced.author.id == client.user.id:
            return True

        # As respostas com expressão são enviadas por webhooks Ayla-<emoção>.
        if (
            referenced.webhook_id is not None
            and referenced.author.name.lower().startswith("ayla")
        ):
            return True

    aliases = get_aliases(message.author.id)

    words = {
        word.strip(".,!?;:()[]{}\"'").lower()
        for word in text.split()
    }

    return any(alias.lower() in words for alias in aliases)


# ============================================================
# CONVERSA ATIVA
# ============================================================

def conversation_is_active(channel_id, user_id):
    key = (channel_id, user_id)
    expires = active_conversations.get(key)

    if expires is None:
        return False

    if datetime.now() >= expires:
        active_conversations.pop(key, None)
        return False

    return True


def activate_conversation(channel_id, user_id):
    active_conversations[(channel_id, user_id)] = (
        datetime.now() + timedelta(minutes=5)
    )


# ============================================================
# PEDIDO PARA CHAMAR OUTRA PESSOA
# ============================================================

async def try_call_person(message):

    text = message.content.lower()

    call_words = [
        "chama o ",
        "chama a ",
        "chame o ",
        "chame a "
    ]

    found = None

    for expression in call_words:
        if expression in text:
            found = expression
            break

    if not found:
        return False

    name = text.split(
        found,
        1
    )[1].strip()

    # Remove complementos comuns
    for separator in [
        " pra ",
        " para ",
        " aqui",
        ","
    ]:
        if separator in name:
            name = name.split(
                separator,
                1
            )[0]

    name = name.strip()

    if not name:
        return False

    target = find_user_by_name(name)

    if target is None:

        await message.reply(
            f"eu nem conheço {name} 😭",
            mention_author=False
        )

        return True

    affection = target["affection"]
    relationship = target["relationship"]

    # Guigo sempre pode ser chamado
    allowed = (
        relationship == "creator"
        or affection >= 25
    )

    if not allowed:

        await message.reply(
            f"eu mal conheço {target['nickname'] or target['username']} 😭",
            mention_author=False
        )

        return True

    await message.channel.send(
        f"<@{target['discord_id']}> VEM CÁÁÁ :D"
    )

    return True


# ============================================================
# EXPRESSÕES VISUAIS
# ============================================================

emotion_webhook_cache = {}


async def get_emotion_webhook(channel, emotion):
    cache_key = (channel.id, emotion)

    if cache_key in emotion_webhook_cache:
        return emotion_webhook_cache[cache_key]

    image_path = EMOTION_IMAGES.get(
        emotion,
        EMOTION_IMAGES["normal"]
    )

    if not image_path.exists():
        raise FileNotFoundError(
            f"Imagem não encontrada: {image_path}"
        )

    webhook_name = f"Ayla-{emotion}"
    webhooks = await channel.webhooks()
    webhook = discord.utils.get(webhooks, name=webhook_name)

    if webhook is None:
        webhook = await channel.create_webhook(
            name=webhook_name,
            avatar=image_path.read_bytes(),
            reason="Expressões visuais da Ayla"
        )

    emotion_webhook_cache[cache_key] = webhook
    return webhook


async def send_ayla_response(message, content, emotion):
    try:
        webhook = await get_emotion_webhook(
            message.channel,
            emotion
        )

        await webhook.send(
            content=f"**{message.author.display_name}:** {content}",
            username="Ayla",
            wait=True,
            allowed_mentions=discord.AllowedMentions.none()
        )

    except (
        discord.Forbidden,
        discord.HTTPException,
        FileNotFoundError,
        AttributeError
    ) as error:
        print(
            f"[AYLA] Expressão visual indisponível: {error}"
        )

        await message.reply(
            content,
            mention_author=False
        )


# ============================================================
# PROCESSAR CONVERSA
# ============================================================

async def process_ayla_message(message):

    global ayla_emotion

    discord_id = message.author.id
    username = message.author.name
    nickname = message.author.display_name

    is_creator = (
        discord_id == GUIGO_ID
    )

    # Salva mensagem no contexto coletivo
    save_message(
        discord_id=discord_id,
        role="user",
        content=message.content,
        channel_id=message.channel.id,
        username=nickname
    )

    # Pedido especial para chamar alguém
    called_someone = await try_call_person(
        message
    )

    if called_someone:
        return

    async with message.channel.typing():

        result = generate_response(
            discord_id=discord_id,
            username=nickname,
            message=message.content,
            channel_id=message.channel.id,
            is_creator=is_creator,
            current_emotion=ayla_emotion
        )

    response = result.get(
        "reply",
        "oi? :D"
    )

    # ========================================================
    # EMOÇÃO
    # ========================================================

    new_emotion = result.get(
        "emotion",
        ayla_emotion
    )

    if new_emotion in VALID_EMOTIONS:

        ayla_emotion = new_emotion

        set_emotion(
            ayla_emotion
        )

        await update_status()

    # ========================================================
    # MEMÓRIAS
    # ========================================================

    for memory in result.get(
        "memories",
        []
    ):

        if (
            isinstance(memory, str)
            and memory.strip()
        ):

            save_memory(
                discord_id,
                memory.strip()
            )

    # ========================================================
    # APELIDOS APRENDIDOS
    # ========================================================

    for alias in result.get("new_aliases", []):
        if isinstance(alias, str):
            alias = alias.strip()

            if alias:
                save_alias(
                    discord_id,
                    alias
                )

    # ========================================================
    # AFINIDADE
    # ========================================================

    affection_change = result.get(
        "affection_change",
        0
    )

    try:
        affection_change = int(
            affection_change
        )

    except (TypeError, ValueError):
        affection_change = 0

    # Evita GPT decidir mudanças absurdas
    affection_change = max(
        -3,
        min(3, affection_change)
    )

    if not is_creator:
        change_affection(
            discord_id,
            affection_change
        )

    # ========================================================
    # SALVA RESPOSTA
    # ========================================================

    save_message(
        discord_id=discord_id,
        role="assistant",
        content=response,
        channel_id=message.channel.id,
        username="Ayla"
    )

    # Responde com a expressão visual correspondente
    await send_ayla_response(
        message,
        response,
        ayla_emotion
    )

    activate_conversation(
        message.channel.id,
        message.author.id
    )

    update_activity()

    print(
        f"{nickname} -> Ayla | "
        f"emoção={ayla_emotion} | "
        f"afinidade={affection_change:+}"
    )


# ============================================================
# RECEBER MENSAGENS
# ============================================================

@client.event
async def on_message(message):

    global last_server_activity
    global last_channel

    if message.author.bot:
        return

    if not message.content.strip():
        return

    last_server_activity = datetime.now()
    last_channel = message.channel

    discord_id = message.author.id

    # Se Ayla havia chamado esta pessoa e ela voltou a falar,
    # a iniciativa recebeu resposta.
    if discord_id in pending_initiatives:
        pending_initiatives.pop(discord_id, None)
        reset_ignored(discord_id)

    remember_user(
        discord_id=discord_id,
        username=message.author.name,
        nickname=message.author.display_name,
        creator=(
            discord_id == GUIGO_ID
        )
    )

    called = ayla_was_called(
        message
    )

    active = conversation_is_active(
        message.channel.id,
        message.author.id
    )

    # Se Ayla não foi chamada e não está
    # participando da conversa, apenas observa.
    if not called and not active:
        return

    # Cria um lock específico para o canal
    if message.channel.id not in channel_locks:

        channel_locks[
            message.channel.id
        ] = asyncio.Lock()

    # Mensagens são processadas em ordem
    async with channel_locks[
        message.channel.id
    ]:

        try:

            await process_ayla_message(
                message
            )

        except Exception as error:

            print(
                f"ERRO NA AYLA: {error}"
            )

            await message.reply(
                "meu cérebro deu uma travadinha 😭",
                mention_author=False
            )


# ============================================================
# INICIATIVA DA AYLA
# ============================================================

@tasks.loop(minutes=1)
async def initiative_loop():

    global last_initiative

    # Marca como ignoradas as iniciativas sem resposta por 30 minutos.
    now = datetime.now()

    expired = [
        discord_id
        for discord_id, called_at in pending_initiatives.items()
        if now - called_at >= timedelta(minutes=30)
    ]

    for discord_id in expired:
        pending_initiatives.pop(discord_id, None)
        mark_ignored(discord_id)

    if last_channel is None:
        return

    silence = (
        datetime.now()
        - last_server_activity
    )

    # Ainda não passaram 15 minutos
    if silence < timedelta(minutes=15):
        return

    # Ayla já tentou conversar recentemente
    if (
        last_initiative is not None
        and datetime.now() - last_initiative
        < timedelta(minutes=30)
    ):
        return

    friends = get_friends(
        min_affection=25
    )

    if not friends:
        return

    available = [
        user
        for user in friends
        if (
            user["discord_id"] not in recently_called
            and can_call_user(user["discord_id"])
        )
    ]

    if not available:
        recently_called.clear()

        available = [
            user
            for user in friends
            if can_call_user(user["discord_id"])
        ]

        if not available:
            return

    person = random.choice(
        available
    )

    recently_called.add(
        person["discord_id"]
    )

    nickname = (
        person["nickname"]
        or person["username"]
    )

    possible_messages = [
        f"<@{person['discord_id']}> oii... cadê você? ;-;",
        f"<@{person['discord_id']}> vem conversar comigo :D",
        f"<@{person['discord_id']}> tô entediadaaa 😭",
        f"<@{person['discord_id']}> {nickname}!! ☕"
    ]

    await last_channel.send(
        random.choice(
            possible_messages
        )
    )

    mark_called(
        person["discord_id"]
    )

    pending_initiatives[
        person["discord_id"]
    ] = datetime.now()

    last_initiative = datetime.now()


@initiative_loop.before_loop
async def before_initiative():

    await client.wait_until_ready()


# ============================================================
# READY
# ============================================================

@client.event
async def on_ready():

    await tree.sync()
    await update_status()

    if not initiative_loop.is_running():
        initiative_loop.start()

    print("=" * 50)
    print(f"Ayla ONLINE: {client.user}")
    print(f"Humor: {ayla_emotion}")
    print("Memória: ONLINE")
    print("Iniciativa: ONLINE")
    print("Conversas coletivas: ONLINE")
    print("=" * 50)


# ============================================================
# COMANDO
# ============================================================

@tree.command(
    name="ayla",
    description="Chama a Ayla"
)
async def ayla(
    interaction: discord.Interaction
):

    await interaction.response.send_message(
        "Oi! :D"
    )


# ============================================================
# START
# ============================================================

client.run(TOKEN)
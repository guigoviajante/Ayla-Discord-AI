# Ayla — AI Discord Companion

🇺🇸 **English** | [🇧🇷 Português](README.pt-BR.md)

## Description

Ayla has always been a project that I wanted to create ever since I discovered the existence of APIs. For a long time, however, the project remained archived because I did not have enough programming experience to build what I had imagined.

Over time, I continued learning programming and understanding how APIs, databases, and different parts of an application could work together. Today, after a lot of coffee and many sleepless nights, I finally managed to make the Ayla project work. As a bonus, I was able to turn an idea that had been archived for a long time into a functional project for my CS50x final project.

Ayla is an AI-powered companion that lives inside a Discord server. The main idea behind the project was not simply to create another chatbot that receives a question and returns an answer. I wanted Ayla to feel more like a character that exists inside the server. She has her own personality, can remember information about different users, develop different relationships with them, learn aliases, and express different emotional states.

## How Ayla Works

The project was developed in Python and integrates Discord, the OpenAI API, and an SQLite database.

When someone sends a message to Ayla on Discord, the program identifies the user and collects information that can be useful for generating her response. This includes previous memories about that person, their relationship with Ayla, Ayla's current emotional state, and recent messages from the Discord channel.

This context is then sent to the AI together with Ayla's personality instructions. Instead of only returning a message, the AI returns structured information containing Ayla's response, her new emotional state, memories that should be saved, aliases that may have been learned, and possible changes in her affinity with the user.

This allows the rest of the Python application to decide what should be stored and how Ayla should appear on Discord.

## Memory and Relationships

One of the most important parts of Ayla is her persistent memory system.

Each Discord user is identified using their Discord ID. Ayla can store memories separately for each person, which prevents information about one user from being confused with information about another user.

The SQLite database stores users, messages, memories, aliases, emotional information, and data related to Ayla's interactions. Because this information is persistent, restarting the bot does not mean Ayla has to completely forget the people she has met.

Ayla also has an affinity system. Her relationship with a person can change depending on their interactions. This information is included as context when generating future responses, allowing her behavior to be different depending on who she is talking to.

I also added a special identification for myself as Ayla's creator. When the program recognizes my Discord ID, Ayla knows that she is talking to Guigo and can use that information naturally during the conversation.

## Emotions and Visual Expressions

Ayla can have different emotional states: normal, happy, excited, confused, sad, and irritated.

Her current emotion can affect the way she responds. The emotion is also represented visually on Discord. The project contains different images of Ayla for each emotional state, and Discord webhooks are used to display the appropriate expression when she sends a message.

Her Discord status can also change according to her current emotion. For example, when she is in her normal state, her status references drinking coffee, which is part of her personality.

This system was created because I wanted Ayla's emotions to be visible instead of existing only inside the text of her responses.

## Aliases and Conversations

Users can teach Ayla aliases. For example, if someone tells her that they will call her "Aylinha", the alias can be stored and later recognized by the program as another way of calling Ayla.

The bot also keeps conversations active for a limited period. This means that after initially calling Ayla, the user does not need to type her name at the beginning of every single message in the conversation.

Another feature is Ayla's initiative system. After a period without activity, she can choose to call someone with whom she already has a relationship. The system includes controls to prevent her from repeatedly calling the same person and tracks situations where her attempts to start a conversation are ignored.

## Project Files

`ayla.py` is the main file of the project. It handles the Discord client, messages, active conversations, emotional status, visual expressions, user interactions, and Ayla's initiative system. It connects the other parts of the project and controls how Ayla behaves inside Discord.

`brain.py` is responsible for generating Ayla's responses. It communicates with the OpenAI API and combines Ayla's personality, memories, recent conversation context, relationship information, and current emotion. It requests a structured JSON response so that the program can process not only what Ayla says, but also changes to memories, aliases, affinity, and emotions.

`database.py` manages the SQLite database. It creates and accesses the tables used to store users, memories, messages, aliases, emotional state, relationships, and information required by the initiative system.

`personality.py` contains the instructions that define Ayla as a character. This includes her personality, way of speaking, emotional behavior, relationship with users, memory rules, and her special relationship with her creator. Keeping the personality separate from the main Discord code makes it easier to modify Ayla's character without changing the rest of the application.

The `assets` directory contains Ayla's visual expressions. There are separate images for her normal, happy, excited, confused, sad, and irritated states.

`ayla.db` is the SQLite database used to persist Ayla's information between executions. It is created and used locally and is not included in this public repository.

The project also uses an environment file locally to store private credentials such as the OpenAI API key and Discord bot token. This file is excluded through `.gitignore` so that private credentials are not included in the submitted project.

## Design Decisions

One of the main design decisions was separating Ayla's systems instead of putting the entire project into a single Python file. Discord interaction, AI processing, persistent storage, personality, and visual assets have different responsibilities. Separating them made the project easier to understand and modify as it became more complex.

Another important decision was to use Discord IDs instead of usernames as the main identifier for users. Usernames can change, while Discord IDs provide a more reliable way to associate memories and relationships with the correct person.

I also decided that Ayla should not depend entirely on the AI model for persistence. Important information is stored locally in SQLite and then provided as context when necessary. This gives the application control over what information persists between conversations.

This project is the first functional version of Ayla. There are still many ideas that I would like to explore in future versions, but the objective of this version was to create the foundation: a Discord companion capable of maintaining a personality, remembering people, developing relationships, and expressing emotions over time.


## Authorship and Assistance

Ayla is a project of my own authorship, including its original concept, idea, character, objectives, and development.

During the project, I used AI as a support tool to help identify and understand errors that I was having difficulty finding on my own. I also used AI to assist me in organizing and reviewing the text of this README.

English is not my first language and I am not yet fluent, so I used Google Translate to assist me with the English translation and review of this documentation.

## Installation and local setup

1. Install Python 3.10 or newer and create a virtual environment (recommended).
2. Install dependencies with `python -m pip install -r requirements.txt`.
3. Copy `mistery.env.example` to `mistery.env` and fill in your own `DISCORD_TOKEN`, `OPENAI_API_KEY` and `GUIGO_DISCORD_ID` (numeric Discord user ID). Do **not** upload `mistery.env`.
4. Configure the Discord bot's **Message Content Intent** in the Discord Developer Portal and grant the permissions needed for the bot and webhooks in your test server.
5. Start the bot with `python ayla.py`. A local SQLite database will be created automatically.

The application requires access to the Discord and OpenAI services; API use may incur charges. Do not upload user conversations or local databases to a public repository.

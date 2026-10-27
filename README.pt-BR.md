# Ayla — Companheira Virtual com IA para Discord

[🇺🇸 English](README.md) | 🇧🇷 **Português**

## Descrição

A Ayla sempre foi um projeto que eu quis criar desde que descobri a existência das APIs. Durante muito tempo, porém, o projeto permaneceu arquivado porque eu ainda não tinha experiência suficiente em programação para construir aquilo que havia imaginado.

Com o passar do tempo, continuei aprendendo programação e entendendo como APIs, bancos de dados e diferentes partes de uma aplicação poderiam funcionar em conjunto. Hoje, depois de muito café e várias noites sem dormir, finalmente consegui fazer o projeto Ayla funcionar. Como bônus, consegui transformar uma ideia que estava arquivada havia muito tempo em um projeto funcional para o meu trabalho final do CS50x.

Ayla é uma companheira virtual com inteligência artificial que vive dentro de um servidor do Discord. A ideia principal do projeto não era simplesmente criar mais um chatbot que recebe uma pergunta e devolve uma resposta. Eu queria que Ayla parecesse mais uma personagem que realmente existe dentro do servidor. Ela possui personalidade própria, consegue lembrar informações sobre diferentes usuários, desenvolver relacionamentos distintos com eles, aprender apelidos e expressar diferentes estados emocionais.

## Como a Ayla funciona

O projeto foi desenvolvido em Python e integra o Discord, a API da OpenAI e um banco de dados SQLite.

Quando alguém envia uma mensagem para Ayla no Discord, o programa identifica o usuário e reúne informações que podem ser úteis para gerar sua resposta. Isso inclui memórias anteriores sobre aquela pessoa, seu relacionamento com Ayla, o estado emocional atual da personagem e mensagens recentes do canal do Discord.

Esse contexto é enviado à inteligência artificial junto com as instruções que definem a personalidade da Ayla. Em vez de retornar apenas uma mensagem, a IA devolve informações estruturadas contendo a resposta da Ayla, seu novo estado emocional, memórias que devem ser armazenadas, apelidos que podem ter sido aprendidos e possíveis alterações em sua afinidade com o usuário.

Isso permite que o restante da aplicação em Python determine quais informações devem ser armazenadas e como Ayla deve se apresentar no Discord.

## Memória e relacionamentos

Uma das partes mais importantes da Ayla é seu sistema de memória persistente.

Cada usuário do Discord é identificado por meio de seu ID. Ayla consegue armazenar memórias separadamente para cada pessoa, evitando que informações de um usuário sejam confundidas com as de outro.

O banco de dados SQLite armazena usuários, mensagens, memórias, apelidos, informações emocionais e dados relacionados às interações da Ayla. Como essas informações são persistentes, reiniciar o bot não significa que Ayla precise esquecer completamente as pessoas que conheceu.

Ayla também possui um sistema de afinidade. Seu relacionamento com uma pessoa pode mudar dependendo das interações entre elas. Essas informações são incluídas no contexto utilizado para gerar respostas futuras, permitindo que seu comportamento seja diferente dependendo de com quem está conversando.

Também adicionei uma identificação especial para mim como criador da Ayla. Quando o programa reconhece meu ID do Discord, Ayla sabe que está conversando com Guigo e consegue utilizar essa informação naturalmente durante a conversa.

## Emoções e expressões visuais

Ayla pode apresentar diferentes estados emocionais: normal, feliz, animada, confusa, triste e irritada.

Sua emoção atual pode influenciar a maneira como responde. Além disso, essa emoção também é representada visualmente no Discord. O projeto contém diferentes imagens da Ayla para cada estado emocional, e webhooks do Discord são utilizados para exibir a expressão correspondente quando ela envia uma mensagem.

O status da Ayla no Discord também pode mudar conforme sua emoção atual. Por exemplo, quando ela está em seu estado normal, seu status faz referência a tomar café, algo que faz parte de sua personalidade.

Esse sistema foi criado porque eu queria que as emoções da Ayla fossem visíveis, em vez de existirem apenas no texto de suas respostas.

## Apelidos e conversas

Os usuários podem ensinar apelidos à Ayla. Por exemplo, se alguém disser que vai chamá-la de "Aylinha", esse apelido poderá ser armazenado e posteriormente reconhecido pelo programa como outra maneira de chamar Ayla.

O bot também mantém as conversas ativas por um período limitado. Isso significa que, depois de chamar Ayla inicialmente, o usuário não precisa digitar o nome dela no início de cada mensagem durante a conversa.

Outra funcionalidade é o sistema de iniciativa da Ayla. Após um período sem atividade, ela pode decidir chamar alguém com quem já possui um relacionamento. O sistema inclui mecanismos para impedir que ela chame repetidamente a mesma pessoa e acompanha situações em que suas tentativas de iniciar uma conversa são ignoradas.

## Arquivos do projeto

`ayla.py` é o arquivo principal do projeto. Ele gerencia o cliente do Discord, as mensagens, as conversas ativas, o status emocional, as expressões visuais, as interações com os usuários e o sistema de iniciativa da Ayla. Esse arquivo conecta as diferentes partes do projeto e controla como Ayla se comporta dentro do Discord.

`brain.py` é responsável por gerar as respostas da Ayla. Ele se comunica com a API da OpenAI e combina a personalidade da personagem, suas memórias, o contexto recente da conversa, as informações de relacionamento e sua emoção atual. O arquivo solicita uma resposta estruturada em JSON para que o programa consiga processar não apenas aquilo que Ayla diz, mas também alterações nas memórias, nos apelidos, na afinidade e nas emoções.

`database.py` gerencia o banco de dados SQLite. Ele cria e acessa as tabelas utilizadas para armazenar usuários, memórias, mensagens, apelidos, estados emocionais, relacionamentos e informações necessárias para o sistema de iniciativa.

`personality.py` contém as instruções que definem Ayla como personagem. Isso inclui sua personalidade, maneira de falar, comportamento emocional, relacionamento com os usuários, regras de memória e sua relação especial com seu criador. Manter a personalidade separada do código principal do Discord facilita modificar a personagem sem precisar alterar o restante da aplicação.

O diretório `assets` contém as expressões visuais da Ayla. Existem imagens separadas para seus estados normal, feliz, animada, confusa, triste e irritada.

`ayla.db` é o banco de dados SQLite utilizado para manter as informações da Ayla entre diferentes execuções. Esse arquivo é utilizado localmente e não é distribuído no repositório público.

O projeto também utiliza um arquivo de ambiente local para armazenar credenciais privadas, como a chave da API da OpenAI e o token do bot do Discord. Esse arquivo é excluído do versionamento por meio do `.gitignore`, para evitar que credenciais privadas sejam incluídas no projeto publicado.

## Decisões de desenvolvimento

Uma das principais decisões de desenvolvimento foi separar os sistemas da Ayla em vez de colocar todo o projeto em um único arquivo Python. A interação com o Discord, o processamento da inteligência artificial, o armazenamento persistente, a personalidade e os recursos visuais possuem responsabilidades diferentes. Separar esses componentes tornou o projeto mais fácil de compreender e modificar conforme ele se tornou mais complexo.

Outra decisão importante foi utilizar os IDs do Discord em vez dos nomes de usuário como identificadores principais. Os nomes de usuário podem mudar, enquanto os IDs do Discord oferecem uma maneira mais confiável de associar memórias e relacionamentos às pessoas corretas.

Também decidi que Ayla não deveria depender inteiramente do modelo de inteligência artificial para manter suas informações. Os dados importantes são armazenados localmente no SQLite e posteriormente fornecidos como contexto quando necessário. Isso permite que a aplicação tenha controle sobre quais informações permanecem armazenadas entre diferentes conversas.

Este projeto representa a primeira versão funcional da Ayla. Ainda existem muitas ideias que gostaria de explorar em versões futuras, mas o objetivo desta versão foi construir sua base: uma companheira virtual para Discord capaz de manter uma personalidade, lembrar das pessoas, desenvolver relacionamentos e expressar emoções ao longo do tempo.

## Autoria e assistência

Ayla é um projeto de minha autoria, incluindo seu conceito original, ideia, personagem, objetivos e desenvolvimento.

Durante o projeto, utilizei inteligência artificial como ferramenta de apoio para ajudar a identificar e compreender erros que eu estava tendo dificuldade em encontrar sozinho. Também utilizei IA para me auxiliar na organização e revisão do texto deste README.

## Instalação e configuração local

1. Instale o Python 3.10 ou superior e, de preferência, crie um ambiente virtual.
2. Instale as dependências com `python -m pip install -r requirements.txt`.
3. Copie `mistery.env.example` para `mistery.env` e preencha seus próprios `DISCORD_TOKEN`, `OPENAI_API_KEY` e `GUIGO_DISCORD_ID` (ID numérico do usuário no Discord). **Não publique** o `mistery.env`.
4. Ative a opção **Message Content Intent** do bot no Portal de Desenvolvedores do Discord e conceda as permissões necessárias para o bot e os webhooks no servidor de testes.
5. Execute `python ayla.py`. Um banco SQLite local será criado automaticamente.

A aplicação precisa de acesso aos serviços do Discord e da OpenAI; o uso da API pode gerar custos. Não publique conversas de usuários ou bancos de dados locais.

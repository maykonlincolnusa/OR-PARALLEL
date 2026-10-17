# Guia prático — Bionic / LM Studio no OR PARALLEL

Este guia acompanha o projeto. A ideia é aprender modificando uma aplicação real, não decorando menus.

## O que já está configurado

- Projeto conectado: `OR PARALLEL`
- Modelo escolhido: `Llama 3.2 3B Instruct Q4_K_M`
- API local: `http://localhost:1235/v1`
- Carregamento de modelos sob demanda: ativado
- Aplicação: `http://127.0.0.1:8765`

## Quatro áreas importantes

1. **Projeto** — mostra a pasta e os arquivos que o agente pode analisar.
2. **Sessão** — espaço em que o agente conversa e trabalha no projeto.
3. **Modelo** — seleciona qual inteligência responderá; para este projeto, use o Llama local.
4. **API de modelos locais** — permite que o `server.py` converse com o Llama.

## Primeiro exercício no chat do Bionic

Depois que o Llama terminar de baixar:

1. Volte ao aplicativo.
2. Clique em **Criar sessão**.
3. Selecione o projeto **OR PARALLEL**.
4. No seletor **Modelo**, escolha `Llama 3.2 3B Instruct`.
5. Envie este prompt:

> Leia o README.md e o web/app.js. Explique em linguagem simples como um acontecimento muda o horário, as métricas e a memória de um habitante. Não altere nenhum arquivo ainda.

Esse prompt é propositalmente de leitura. Ele mostra como pedir ao agente para compreender o projeto antes de autorizar alterações.

## Segundo exercício

Quando a explicação estiver clara, envie:

> Encontre no web/app.js a lista de habitantes. Sugira um nono habitante, com nome, profissão, personalidade, cor e memória inicial. Mostre a alteração proposta, mas aguarde minha confirmação antes de editar.

## Como saber se está usando o modelo local

- O seletor de modelo deve mostrar o Llama baixado.
- A página do OR PARALLEL deve mostrar **Llama conectado** no canto superior.
- Em **Configurações → API de modelos locais**, os registros mostrarão chamadas a `/v1/chat/completions`.
- O projeto continua funcionando sem internet depois que o modelo está armazenado no Mac.

## Regra de aprendizado

Sempre use esta sequência:

1. Peça para o agente **ler e explicar**.
2. Peça uma **proposta de alteração**.
3. Revise a proposta.
4. Autorize a edição.
5. Execute e verifique visualmente.

Isso permite aprender o raciocínio, o código e o resultado em vez de apenas aceitar alterações automáticas.

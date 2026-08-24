# Rotina: resumo diário do grupo do Cowork Ilha do Silício

**Este arquivo é a fonte da verdade do prompt.** A tarefa agendada aponta pra cá.
Mudou a regra? Muda aqui, não na cópia do agendador.

Roda todo dia às **08:00** (BRT). Publica no grupo o resumo do que rolou
**desde o último resumo publicado** — normalmente é só o dia anterior, mas se a
rotina passou dias sem rodar, ela cobre o buraco sozinha em vez de fingir que
não houve nada.

> A tarefa agendada só dispara com o app do Claude aberto, e um dia perdido não
> é reposto: no próximo lançamento ela roda **uma vez**. Por isso a janela é
> ancorada no último resumo, não no calendário. Foi o que engoliu os resumos de
> 21 e 23/08/2026.

## Passo a passo

1. `cd ~/Downloads/ilha-do-silicio`
2. Atualiza o acervo com o que o webhook capturou:
   `python3 rotinas/sync_acervo.py --frase "$(cat ~/.ilha-frase)"`
   - Se ele listar nome novo desconhecido, veja se é apelido de quem já está no
     acervo. Só mapeie em `rotinas/pessoas.json` **com prova** (a pessoa se
     apresentando, nome de perfil que é prefixo exato do da agenda). Sem prova,
     deixa separado: pessoa duplicada é feio, pessoa fundida errado é mentira.
3. Lê as mensagens da JANELA: decifra com `rotinas/decifrar.mjs` num arquivo
   temporário FORA do repositório e apaga o arquivo no fim.
   A janela **não é "ontem"**, é *desde o último resumo publicado até ontem*. O
   marco está no próprio acervo: a última mensagem do "Andre Turra" que começa
   com o cartão `(Claudinho)`. Pega tudo o que veio depois dela.
   Se não achar cartão nenhum, cai pra ontem.
4. Sorteia quem assina: `python3 rotinas/personas_ilha.py` — devolve o
   personagem do dia, a voz e amostras de tom.
5. Escreve o resumo (regras abaixo) num arquivo temporário.
6. Manda: `python3 rotinas/enviar.py <arquivo>`
7. Commita o `acervo/dados.enc` atualizado e dá push. É isso que mantém a
   página do acervo em dia.

## Quando NÃO mandar

Menos de **5 mensagens úteis** na janela: não manda nada. Um grupo tem
direito a dia parado, e resumo de dia vazio treina todo mundo a ignorar o canal —
aí o resumo que importa passa despercebido junto.

## Como escrever

- **Primeira linha é sempre o cartão** que o `personas_ilha.py` devolve, com o
  `(Claudinho)`. Sai do WhatsApp pessoal do Turra: sem a plaquinha o grupo acha
  que é ele escrevendo.
- **Não narrar o truque.** Nunca "hoje eu sou a Maricota". Dizer quem o
  personagem é, o cartão já faz. Explicar que é uma encenação mata a piada.
- **Nada de frase pronta.** O que está no `personas_ilha.py` é AMOSTRA DE TOM.
  Escreve linha nova naquela voz, todo dia.
- **Assunto, não cronologia.** Agrupa por tema com emoji e um título curto em
  negrito. O que rendeu mais vem primeiro, e diz quem falou.
- **Nome de quem falou** em cada bloco, pra pessoa saber com quem puxar assunto.
- **O conteúdo sai intacto.** A voz enfeita a moldura, nunca o dado: número,
  link, valor e combinado vão do jeito que foram ditos.
- Fecha na voz do personagem.
- Tamanho: cabe numa tela de celular sem susto. 5 blocos é muito.

## O que o resumo procura

Nesta ordem: combinado que ficou de pé (lugar, dia, hora), pedido de ajuda que
ninguém respondeu, decisão sobre o espaço físico, vaga/freela/indicação,
material que alguém compartilhou e vale achar depois. Piada boa entra se
rendeu — o grupo é de gente, não é ata de reunião.

## Se falhar

Se a Z-API recusar o envio ou o sync quebrar, **não tenta de novo em loop**:
avisa o Turra no privado dele (self-chat, número 5548991392889) em UMA mensagem
dizendo o que quebrou. O grupo não precisa ver erro de robô.

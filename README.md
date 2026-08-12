# Ilha do Silício — página de cadastro

Landing page estática com formulário que grava direto numa planilha do Google Sheets.
Zero servidor, zero mensalidade.

```
Navegador → GitHub Pages (index.html) → POST → Apps Script (Web App) → Google Sheets
```

| Peça | Serviço | Custo |
|---|---|---|
| Hospedagem | GitHub Pages | grátis |
| Backend | Google Apps Script | grátis |
| Banco | Google Sheets | grátis |

---

## Como colocar no ar

### 0. Preencher o e-mail de contato (LGPD)

Em [`privacidade.html`](privacidade.html), troque `[SEU E-MAIL AQUI]` por um e-mail real e apague o
bloco de aviso laranja. A lei exige um canal para pedidos de acesso e exclusão — sem isso, não
divulgue a página.

### 1. A planilha

Já está definida no script, pelo ID:
[Ilha do Silício — Cadastros](https://docs.google.com/spreadsheets/d/1z8oxhUYd0h_mUDu35_S9UFWhjOS2y2C4N-IWb53JX6o/edit).
Não precisa criar aba nem cabeçalho: o script faz isso sozinho no primeiro envio.

Para trocar de planilha, mude a constante `PLANILHA_ID` no topo do `Codigo.gs`.

### 2. Publicar o Apps Script

1. Na planilha: **Extensões › Apps Script**.
2. Apague o conteúdo do `Código.gs` e cole tudo de [`apps-script/Codigo.gs`](apps-script/Codigo.gs).
3. *(Opcional)* preencha `NOTIFICAR_EMAIL` com seu e-mail para receber aviso a cada cadastro.
4. Salve (⌘S) e clique em **Implantar › Nova implantação**.
5. Engrenagem ⚙️ ao lado de "Selecione o tipo" → **App da Web**.
6. Configure exatamente assim:
   - **Executar como:** `Eu (seu@email.com)`
   - **Quem pode acessar:** `Qualquer pessoa` ← precisa ser este, senão a página recebe erro
7. **Implantar** → autorize o acesso (aparece "Google não verificou este app" → *Avançado* → *Acessar projeto sem título*; é seu próprio script).
8. Copie a **URL do app da Web** — ela termina em `/exec`.

> Teste rápido: cole essa URL no navegador. Deve aparecer `{"ok":true,"servico":"ilha-do-silicio",...}`.

### 3. Ligar a página no script

Em [`index.html`](index.html), troque a linha do topo do `<script>`:

```js
const ENDPOINT = "COLE_AQUI_A_URL_DO_APPS_SCRIPT";
```

pela URL `/exec` que você copiou. Commit e push:

```bash
git add index.html && git commit -m "Configura endpoint do Apps Script" && git push
```

### 4. Ativar o GitHub Pages

No repositório: **Settings › Pages › Source: Deploy from a branch › Branch: `main` / `/ (root)` › Save**.

Em ~1 minuto a página fica no ar. A URL aparece nessa mesma tela.

---

## Manutenção

**Mudar campos do formulário.** Edite o `index.html` (o HTML do campo + o objeto `payload` no JS)
e adicione a coluna correspondente em `COLUNAS` e no `appendRow` do `Codigo.gs`.
Se mexer no `Codigo.gs`, é preciso **Implantar › Gerenciar implantações › ✏️ › Versão: Nova versão**
— senão a versão antiga continua rodando.

**Domínio próprio.** Settings › Pages › Custom domain, e aponte um CNAME para `SEU-USUARIO.github.io`.

**Spam.** Já tem honeypot (campo escondido `website`). Se aparecer lixo mesmo assim,
o caminho é trocar por um Cloudflare Turnstile — grátis também.

**Backup.** Arquivo › Fazer download › CSV na própria planilha.

**Pedido de exclusão (LGPD).** Apague a linha da pessoa na planilha e confirme por e-mail.
As colunas `Aceitou os termos` e `Versão dos termos` existem para provar o consentimento —
não apague essas colunas.

**Link do grupo.** Está na constante `GRUPO_WHATSAPP`, no `<script>` do `index.html`.
Se o convite for revogado, é lá que se troca.

---

## Estrutura

```
index.html             página + formulário + validação (arquivo único, sem dependências)
privacidade.html       termos de uso e política de privacidade (LGPD)
apps-script/Codigo.gs  script que recebe o POST e grava a linha
```

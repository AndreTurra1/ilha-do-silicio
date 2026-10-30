#!/usr/bin/env python3
"""
Soma ao acervo o que o webhook capturou desde a última rodada, e refecha o .enc.

Fluxo: decifra o acervo atual -> pergunta à caixa do hub o que veio DEPOIS da
última mensagem que ele tem -> mescla -> cifra de volta. O repositório nunca
guarda o acervo em claro, nem por um instante: o JSON intermediário mora fora
da pasta do repo e é apagado no fim.

De onde vem o dado novo: a CAIXA do hub zap-turra (desde 29/10/2026). O hub recebe
o webhook do WhatsApp pessoal do Turra e guarda as mensagens deste grupo numa caixa
só da Ilha; aqui se busca com a chave da Ilha em ~/.ilha-zap (ZAP_HUB_URL e
ZAP_HUB_CHAVE, fora do repo). De 20/08 a 29/10 o grupo vinha do Supabase de outra
operação; isso acabou e o acervo já tem tudo até a virada.

Dedupe: o export do WhatsApp não tem id de mensagem, o webhook tem. Então a
chave de igualdade é (dia, hora até o minuto, autor, texto), que é o que as duas
fontes têm em comum. Na fronteira entre export e webhook isso pode encostar
duas mensagens idênticas do mesmo minuto e a segunda some; é uma perda aceitável
perto de duplicar o dia inteiro da virada.

Uso:
  python3 rotinas/sync_acervo.py --frase "$(cat ~/.ilha-frase)" [--dry-run]
"""
import argparse
import datetime
import json
import os
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(AQUI)
ENC = os.path.join(REPO, "acervo", "dados.enc")
GRUPO = "120363427898397650-group"
DOTENV = os.path.expanduser("~/.ilha-zap")
BRT = datetime.timezone(datetime.timedelta(hours=-3))

# mesma ordem de TIPOS do build_acervo.py
TIPOS = ["texto", "imagem", "video", "audio", "figurinha", "gif", "documento", "sistema"]
# a Z-API nomeia diferente do export
DE_ZAPI = {"texto": "texto", "imagem": "imagem", "video": "video",
           "audio": "audio", "documento": "documento", "outro": "figurinha"}


def env():
    e = dict(os.environ)
    if os.path.exists(DOTENV):
        for linha in open(DOTENV, encoding="utf-8"):
            if "=" in linha and not linha.startswith("#"):
                k, _, v = linha.strip().partition("=")
                e.setdefault(k, v.strip().strip('"'))
    return e


# payload da Z-API -> tipo, igual ao que o webhook gravava antes (o dedupe depende disso)
MIDIAS = [("image", "imagem"), ("video", "video"), ("audio", "audio"),
          ("document", "documento"), ("sticker", "outro")]


def conteudo(p):
    if isinstance(p.get("text"), dict):
        return "texto", p["text"].get("message")
    for k in ("buttonsResponseMessage", "listResponseMessage"):
        if isinstance(p.get(k), dict):
            return "texto", p[k].get("message") or p[k].get("title")
    for k, tipo in MIDIAS:
        if isinstance(p.get(k), dict):
            m = p[k]
            return tipo, m.get("caption") or m.get("title") or m.get("documentTitle")
    return "outro", None


def hub(desde):
    """Mensagens do grupo na caixa do hub desde `desde` (ISO), no formato das linhas antigas."""
    e = env()
    ms = int(datetime.datetime.fromisoformat(desde).timestamp() * 1000)
    req = urllib.request.Request(
        e["ZAP_HUB_URL"].rstrip("/") + f"/caixa?desde={ms}",
        headers={"Authorization": "Bearer " + e["ZAP_HUB_CHAVE"],
                 # a Cloudflare barra o User-Agent padrão do Python (erro 1010)
                 "User-Agent": "ilha-acervo/1"})
    with urllib.request.urlopen(req, timeout=90) as r:
        payloads = json.loads(r.read().decode())["mensagens"]
    linhas = []
    for p in payloads:
        if p.get("type") and p["type"] != "ReceivedCallback":
            continue
        if p.get("isNewsletter") or p.get("isStatusReply"):
            continue
        n = int(p.get("momment") or 0)
        quando = datetime.datetime.fromtimestamp((n if n >= 1e12 else n * 1000) / 1000, datetime.timezone.utc)
        tipo, texto = conteudo(p)
        linhas.append({"ocorrido_em": quando.isoformat(), "autor_nome": p.get("senderName") or p.get("chatName"),
                       "texto": texto, "tipo": tipo, "de_mim": p.get("fromMe") is True})
    return linhas


def canonizar(d):
    """Funde os nomes da mesma pessoa e devolve quantos nomes sobraram sem mapa.

    O export traz o nome SALVO NA AGENDA do Turra e o webhook traz o nome de PERFIL
    da pessoa. Sem isto, "Zuccao 8000" e "Gabriel Zucco" viram duas pessoas no filtro
    da busca, e a partir de hoje TODO MUNDO duplica, porque as duas fontes convivem.

    A tabela é escrita à mão (rotinas/pessoas.json), com a prova em cada linha. Casar
    por semelhança de nome foi descartado: "Kochiski" × "Kochinski" difere por uma
    letra e "Bruno Fabricio" × "Fabricio Feitosa" se parecem sem serem, comprovadamente,
    a mesma pessoa. Nome sem mapa fica em paz, separado, e é reportado pra tabela
    ser mantida — nunca fundido no chute.
    """
    tabela = json.load(open(os.path.join(AQUI, "pessoas.json"), encoding="utf-8"))
    de_para = {}
    for pessoa in tabela["pessoas"]:
        for v in pessoa["variantes"]:
            de_para[v] = pessoa["nome"]
        de_para[pessoa["nome"]] = pessoa["nome"]

    novos, indice = [], {}
    for antigo in d["autores"]:
        canon = de_para.get(antigo, antigo)
        if canon not in indice:
            indice[canon] = len(novos)
            novos.append(canon)
    remap = [indice[de_para.get(a_, a_)] for a_ in d["autores"]]
    for m in d["msgs"]:
        m[2] = remap[m[2]]
    fundidos = len(d["autores"]) - len(novos)
    d["autores"] = novos
    return fundidos, [a_ for a_ in novos if a_ not in de_para]


def node(script, *args):
    subprocess.run([ "node", os.path.join(AQUI, script), *args ],
                   check=True, stdout=subprocess.DEVNULL)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frase", required=True)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    tmp = tempfile.mkdtemp(prefix="ilha-acervo-")
    claro = os.path.join(tmp, "dados.json")
    try:
        node("decifrar.mjs", ENC, claro, a.frase)
        d = json.load(open(claro, encoding="utf-8"))

        # última mensagem que o acervo já tem, em ISO, pra pedir só o que veio depois
        ultimo = max((m[0], m[1]) for m in d["msgs"])
        desde = f"{ultimo[0]}T{ultimo[1]}:00-03:00"
        novas = hub(desde)
        print(f"acervo tem {len(d['msgs'])} até {ultimo[0]} {ultimo[1]}; hub devolveu {len(novas)}")

        vistas = {(m[0], m[1], d["autores"][m[2]], m[3]) for m in d["msgs"]}
        ja_conhecidos = set(d["autores"])
        estreantes = set()
        autores = {a_: i for i, a_ in enumerate(d["autores"])}
        somadas = 0
        for n in novas:
            # `ocorrido_em` é UTC e `dia` já vem em BRT do webhook: usar os dois crus
            # colocava mensagem das 19:47 no acervo como 22:47, dentro do dia certo.
            # Aqui os dois saem da MESMA conversão, que é a única forma de não
            # reabrir esse buraco na próxima fonte de dado.
            quando = datetime.datetime.fromisoformat(
                n["ocorrido_em"].replace("Z", "+00:00")).astimezone(BRT)
            dia, hora = quando.strftime("%Y-%m-%d"), quando.strftime("%H:%M")
            autor = "Andre Turra" if n["de_mim"] else (n.get("autor_nome") or "?")
            texto = n.get("texto") or ""
            chave = (dia, hora, autor, texto)
            if chave in vistas:
                continue
            vistas.add(chave)
            if autor not in autores:
                autores[autor] = len(d["autores"])
                d["autores"].append(autor)
            if autor not in ja_conhecidos:
                estreantes.add(autor)
            tipo = DE_ZAPI.get(n.get("tipo") or "texto", "texto")
            d["msgs"].append([dia, hora, autores[autor], texto, TIPOS.index(tipo)])
            somadas += 1

        d["msgs"].sort(key=lambda x: (x[0], x[1]))
        fundidos, sem_mapa = canonizar(d)
        if fundidos:
            print(f"identidade: {fundidos} nomes fundidos em quem já estava no acervo")
        novatos = sorted(estreantes & set(sem_mapa))
        if novatos:
            print(f"⚠️  nome(s) novo(s) sem entrada em rotinas/pessoas.json: "
                  + ", ".join(novatos))
            print("    Se for apelido de quem já está no acervo, mapeia lá (com a "
                  "prova) e roda de novo; se for gente nova mesmo, ignora.")
        reais = [m for m in d["msgs"] if TIPOS[m[4]] != "sistema"]
        dias = sorted({m[0] for m in reais})
        d["gerado_em"] = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
        d["fonte"] = "export do WhatsApp + webhook (hub zap-turra desde 29/10/2026)"
        d["resumo"] = {"total": len(d["msgs"]), "uteis": len(reais), "pessoas": len(d["autores"]),
                       "primeiro_dia": dias[0], "ultimo_dia": dias[-1], "dias": len(dias)}

        if not somadas and not fundidos:
            print("nada novo e nenhuma identidade a corrigir. acervo intacto.")
            return
        print(f"+{somadas} mensagens novas → {d['resumo']['total']} no total, até {dias[-1]}")
        if a.dry_run:
            print("(dry-run: não regravei o .enc)")
            return
        json.dump(d, open(claro, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
        node("cifrar.mjs", claro, ENC, a.frase)
        print(f"{ENC} regravado. Falta commitar e dar push.")
    finally:
        for f in os.listdir(tmp):
            os.remove(os.path.join(tmp, f))
        os.rmdir(tmp)


if __name__ == "__main__":
    main()

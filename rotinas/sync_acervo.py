#!/usr/bin/env python3
"""
Soma ao acervo o que o webhook capturou desde a última rodada, e refecha o .enc.

Fluxo: decifra o acervo atual -> pergunta ao Supabase o que veio DEPOIS da
última mensagem que ele tem -> mescla -> cifra de volta. O repositório nunca
guarda o acervo em claro, nem por um instante: o JSON intermediário mora fora
da pasta do repo e é apagado no fim.

De onde vem o dado novo: `atlas_fact_wpp_mensagem` do Supabase da H2Jobs, onde
o webhook `zapi-mensagens` grava o grupo desde 20/08/2026 (allowlist com
`papel: "acervo"`, que existe pra deixar claro que este chat não alimenta NADA
da H2Jobs). É provisório: quando a Ilha tiver instância Z-API própria, só esta
função muda de fonte.

Dedupe: o export do WhatsApp não tem id de mensagem, o webhook tem. Então a
chave de igualdade é (dia, hora até o minuto, autor, texto), que é o que as duas
fontes têm em comum. Na fronteira entre export e webhook isso pode encostar
duas mensagens idênticas do mesmo minuto e a segunda some; é uma perda aceitável
perto de duplicar o dia inteiro da virada.

Uso:
  python3 rotinas/sync_acervo.py --frase "$(cat ~/.ilha-frase)" [--dry-run]
"""
import argparse
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
DOTENV = os.path.expanduser("~/Downloads/H2JOBS/GITHUB H2JOBS/h2jobs-atlas/.env.local")

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


def supabase(desde):
    e = env()
    # o .env.local do Atlas nomeia como NEXT_PUBLIC_ (é o front que consome); a
    # service role key não tem prefixo público, e é ela que enxerga a tabela com RLS
    base = e.get("SUPABASE_URL") or e["NEXT_PUBLIC_SUPABASE_URL"]
    url = base.rstrip("/") + "/rest/v1/atlas_fact_wpp_mensagem?" + urllib.parse.urlencode({
        "select": "ocorrido_em,dia,autor_nome,texto,tipo,de_mim",
        "chat_id": f"eq.{GRUPO}",
        "ocorrido_em": f"gte.{desde}",
        "order": "ocorrido_em.asc",
        "limit": "5000",
    })
    req = urllib.request.Request(url)
    req.add_header("apikey", e["SUPABASE_SERVICE_ROLE_KEY"])
    req.add_header("Authorization", "Bearer " + e["SUPABASE_SERVICE_ROLE_KEY"])
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read().decode())


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
        novas = supabase(desde)
        print(f"acervo tem {len(d['msgs'])} até {ultimo[0]} {ultimo[1]}; Supabase devolveu {len(novas)}")

        vistas = {(m[0], m[1], d["autores"][m[2]], m[3]) for m in d["msgs"]}
        autores = {a_: i for i, a_ in enumerate(d["autores"])}
        somadas = 0
        for n in novas:
            hora = n["ocorrido_em"][11:16]
            autor = "Andre Turra" if n["de_mim"] else (n.get("autor_nome") or "?")
            texto = n.get("texto") or ""
            chave = (n["dia"], hora, autor, texto)
            if chave in vistas:
                continue
            vistas.add(chave)
            if autor not in autores:
                autores[autor] = len(d["autores"])
                d["autores"].append(autor)
            tipo = DE_ZAPI.get(n.get("tipo") or "texto", "texto")
            d["msgs"].append([n["dia"], hora, autores[autor], texto, TIPOS.index(tipo)])
            somadas += 1

        if not somadas:
            print("nada novo. acervo intacto.")
            return

        d["msgs"].sort(key=lambda x: (x[0], x[1]))
        reais = [m for m in d["msgs"] if TIPOS[m[4]] != "sistema"]
        dias = sorted({m[0] for m in reais})
        import datetime
        d["gerado_em"] = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
        d["fonte"] = "export do WhatsApp + webhook zapi-mensagens"
        d["resumo"] = {"total": len(d["msgs"]), "uteis": len(reais), "pessoas": len(d["autores"]),
                       "primeiro_dia": dias[0], "ultimo_dia": dias[-1], "dias": len(dias)}

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

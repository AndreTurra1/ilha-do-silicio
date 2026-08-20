#!/usr/bin/env python3
"""
Lê o .txt que o WhatsApp exporta do grupo e devolve as mensagens em JSON.

Por que existe: a Z-API NÃO lê histórico ("Does not work in multi device version"),
então tudo que aconteceu antes do webhook entrar no ar só chega por export manual.
Este script é a porta desse material pro acervo. Depois do webhook ligado, o
ingestor do dia a dia usa o MESMO formato de saída, pra não existirem dois esquemas.

Formato de cada linha do export (iOS):
    [DD/MM/AAAA, HH:MM:SS] Autor: texto
com marcas invisíveis (U+200E/U+200F) espalhadas e mensagem podendo ocupar
várias linhas até a próxima que comece com data.

Uso:
  python3 rotinas/parse_export.py "<arquivo.txt>" --json acervo/mensagens.json
  python3 rotinas/parse_export.py "<arquivo.txt>" --stats
"""
import argparse
import json
import re
import unicodedata

# marcas de direção que o WhatsApp intercala e que quebram qualquer regex ingênua
INVISIVEIS = dict.fromkeys(map(ord, "‎‏‪‬⁦⁧⁨⁩"), None)

CABECA = re.compile(r"^\[(\d{2})/(\d{2})/(\d{4}), (\d{2}):(\d{2}):(\d{2})\]\s(.+?):\s?(.*)$")

# anexos e eventos de sistema: viram tipo próprio, não poluem a busca como texto
ANEXOS = {
    "figurinha omitida": "figurinha",
    "imagem ocultada": "imagem",
    "vídeo omitido": "video",
    "áudio ocultado": "audio",
    "documento omitido": "documento",
    "GIF omitido": "gif",
    "sticker omitted": "figurinha",
    "image omitted": "imagem",
}
SISTEMA = (
    "criou o grupo", "adicionou", "entrou usando o link", "saiu", "removeu",
    "mudou o nome do grupo", "mudou a descrição", "mudou a imagem do grupo",
    "fixou uma mensagem", "As mensagens e ligações são protegidas",
    "mudou as configurações", "agora é adm", "alterou o assunto",
    "Você criou o grupo", "criou este grupo", "desafixou",
)


def limpar(s):
    return (s or "").translate(INVISIVEIS).replace("\r", "").strip()


def parse(caminho):
    msgs = []
    atual = None
    with open(caminho, encoding="utf-8") as fh:
        for bruto in fh:
            linha = bruto.translate(INVISIVEIS).replace("\r", "").rstrip("\n")
            m = CABECA.match(linha)
            if not m:
                # continuação da mensagem anterior (texto com quebra de linha)
                if atual is not None and linha.strip():
                    atual["texto"] += "\n" + linha.strip()
                continue
            if atual is not None:
                msgs.append(atual)
            d, mo, a, h, mi, s, autor, texto = m.groups()
            atual = {
                "data": f"{a}-{mo}-{d}",
                "hora": f"{h}:{mi}:{s}",
                "autor": limpar(autor),
                "texto": limpar(texto),
                "tipo": "texto",
            }
    if atual is not None:
        msgs.append(atual)

    for x in msgs:
        t = x["texto"]
        for marca, tipo in ANEXOS.items():
            if marca in t:
                x["tipo"] = tipo
                break
        else:
            if any(k in t for k in SISTEMA):
                x["tipo"] = "sistema"
        x["links"] = re.findall(r"https?://[^\s]+", t)
    return msgs


def stats(msgs):
    from collections import Counter
    reais = [m for m in msgs if m["tipo"] != "sistema"]
    por_dia = Counter(m["data"] for m in reais)
    print(f"mensagens: {len(msgs)} (úteis: {len(reais)}, sistema: {len(msgs)-len(reais)})")
    print(f"período: {min(por_dia)} → {max(por_dia)}  ({len(por_dia)} dias com conversa)")
    print(f"pessoas: {len(set(m['autor'] for m in reais))}")
    print("\ntipos:", dict(Counter(m["tipo"] for m in msgs)))
    print("\ntop 15 quem mais fala:")
    for autor, n in Counter(m["autor"] for m in reais).most_common(15):
        print(f"  {n:5}  {autor}")
    print("\núltimos 10 dias:")
    for dia in sorted(por_dia)[-10:]:
        print(f"  {dia}  {por_dia[dia]:4} msgs")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("arquivo")
    ap.add_argument("--json", help="grava o resultado neste caminho")
    ap.add_argument("--stats", action="store_true")
    a = ap.parse_args()
    msgs = parse(a.arquivo)
    if a.json:
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump(msgs, fh, ensure_ascii=False, indent=1)
        print(f"{len(msgs)} mensagens → {a.json}")
    if a.stats or not a.json:
        stats(msgs)


if __name__ == "__main__":
    main()

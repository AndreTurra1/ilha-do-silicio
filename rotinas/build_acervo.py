#!/usr/bin/env python3
"""
Monta o acervo pesquisável do grupo a partir do export do WhatsApp.

Saída: acervo/dados.json (formato compacto) que o `cifrar.mjs` transforma no
.enc que vai pro repositório. A página historico.html decifra no navegador.

Formato compacto: em vez de um objeto por mensagem com as chaves repetidas 3 mil
vezes, vai uma LISTA POSICIONAL [dia, hora, indice_do_autor, texto, tipo]. Corta
o arquivo em mais da metade antes de comprimir, e a página remonta na leitura.

Uso:
  python3 rotinas/build_acervo.py "<export.txt>" [--saida acervo/dados.json]
"""
import argparse
import datetime
import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parse_export import parse  # noqa: E402

TIPOS = ["texto", "imagem", "video", "audio", "figurinha", "gif", "documento", "sistema"]


def montar(msgs, fonte):
    autores = [a for a, _ in Counter(m["autor"] for m in msgs).most_common()]
    idx_autor = {a: i for i, a in enumerate(autores)}
    idx_tipo = {t: i for i, t in enumerate(TIPOS)}

    linhas = []
    for m in msgs:
        linhas.append([
            m["data"],
            m["hora"][:5],                      # segundo não serve pra nada aqui
            idx_autor[m["autor"]],
            m["texto"],
            idx_tipo.get(m["tipo"], 0),
        ])
    linhas.sort(key=lambda x: (x[0], x[1]))

    reais = [l for l in linhas if TIPOS[l[4]] != "sistema"]
    dias = sorted({l[0] for l in reais})
    return {
        "v": 1,
        "gerado_em": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "fonte": fonte,
        "autores": autores,
        "tipos": TIPOS,
        "msgs": linhas,
        "resumo": {
            "total": len(linhas),
            "uteis": len(reais),
            "pessoas": len(autores),
            "primeiro_dia": dias[0] if dias else None,
            "ultimo_dia": dias[-1] if dias else None,
            "dias": len(dias),
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("export")
    ap.add_argument("--saida", default="acervo/dados.json")
    a = ap.parse_args()

    msgs = parse(a.export)
    fonte = f"export do WhatsApp, {os.path.basename(a.export)}"
    dados = montar(msgs, fonte)

    os.makedirs(os.path.dirname(a.saida) or ".", exist_ok=True)
    with open(a.saida, "w", encoding="utf-8") as fh:
        json.dump(dados, fh, ensure_ascii=False, separators=(",", ":"))

    r = dados["resumo"]
    print(f"{a.saida}: {r['total']} mensagens · {r['pessoas']} pessoas · "
          f"{r['primeiro_dia']} → {r['ultimo_dia']} ({r['dias']} dias)")


if __name__ == "__main__":
    main()

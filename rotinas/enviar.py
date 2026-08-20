#!/usr/bin/env python3
"""
Manda mensagem no grupo do Cowork Ilha do Silício pela Z-API.

A mensagem sai do WhatsApp PESSOAL do Turra (instância "Turra - Wpp Pessoal"),
então toda mensagem daqui carrega a plaquinha "(Claudinho)" na primeira linha:
sem isso o grupo acha que é ele escrevendo. Ver rotinas/personas_ilha.py.

Credenciais: ZAPI_INSTANCE_ID / ZAPI_TOKEN / ZAPI_CLIENT_TOKEN do ambiente ou do
.env.local do h2jobs-atlas (fora do git). É a MESMA instância do H2Jobs, o que é
provisório: a ideia é a Ilha ganhar instância própria depois.

Uso:
  python3 rotinas/enviar.py mensagem.txt --dry-run
  python3 rotinas/enviar.py mensagem.txt
  python3 rotinas/enviar.py mensagem.txt --daqui-a 600   # espera 10 min e manda
"""
import argparse
import json
import os
import time
import urllib.request

GRUPO = "120363427898397650-group"   # Cowork Ilha do Silício 🏝️🤖
DOTENV = os.path.expanduser(
    "~/Downloads/H2JOBS/GITHUB H2JOBS/h2jobs-atlas/.env.local")


def env():
    e = dict(os.environ)
    if os.path.exists(DOTENV):
        for linha in open(DOTENV, encoding="utf-8"):
            if "=" in linha and not linha.startswith("#"):
                k, _, v = linha.strip().partition("=")
                e.setdefault(k, v.strip().strip('"'))
    return e


def enviar(texto, dry=False):
    e = env()
    iid, tok, ct = e["ZAPI_INSTANCE_ID"], e["ZAPI_TOKEN"], e["ZAPI_CLIENT_TOKEN"]
    if dry:
        print(f"[dry-run] iria pro grupo {GRUPO}, {len(texto)} caracteres:\n")
        print(texto)
        return
    url = f"https://api.z-api.io/instances/{iid}/token/{tok}/send-text"
    corpo = json.dumps({"phone": GRUPO, "message": texto}).encode()
    req = urllib.request.Request(url, data=corpo, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Client-Token", ct)
    with urllib.request.urlopen(req, timeout=60) as r:
        print(json.loads(r.read().decode() or "{}"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("arquivo")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--daqui-a", type=int, default=0, help="segundos de espera antes de mandar")
    a = ap.parse_args()
    texto = open(a.arquivo, encoding="utf-8").read().rstrip("\n")
    if a.daqui_a:
        print(f"esperando {a.daqui_a}s…", flush=True)
        time.sleep(a.daqui_a)
    enviar(texto, a.dry_run)


if __name__ == "__main__":
    main()

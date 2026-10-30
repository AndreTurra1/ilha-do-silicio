#!/usr/bin/env python3
"""
Manda mensagem no grupo do Cowork Ilha do Silício (ou, com --para-turra, no self-chat
do Turra, pra avisar que algo quebrou) pelo hub zap-turra.

A mensagem sai do WhatsApp PESSOAL do Turra (instância "Turra - Wpp Pessoal"),
então toda mensagem daqui carrega a plaquinha "(Claudinho)" na primeira linha:
sem isso o grupo acha que é ele escrevendo. Ver rotinas/personas_ilha.py.

Credenciais: ZAP_HUB_URL / ZAP_HUB_CHAVE (a chave da Ilha no hub) e ZAP_TURRA (o número
dele) em ~/.ilha-zap, fora do repo. O hub guarda a credencial da Z-API; a Ilha nunca vê.

Uso:
  python3 rotinas/enviar.py mensagem.txt --dry-run
  python3 rotinas/enviar.py mensagem.txt
  python3 rotinas/enviar.py mensagem.txt --daqui-a 600   # espera 10 min e manda
  python3 rotinas/enviar.py erro.txt --para-turra         # aviso de falha, só pro Turra
"""
import argparse
import json
import os
import time
import urllib.request

GRUPO = "120363427898397650-group"   # Cowork Ilha do Silício 🏝️🤖
DOTENV = os.path.expanduser("~/.ilha-zap")


def env():
    e = dict(os.environ)
    if os.path.exists(DOTENV):
        for linha in open(DOTENV, encoding="utf-8"):
            if "=" in linha and not linha.startswith("#"):
                k, _, v = linha.strip().partition("=")
                e.setdefault(k, v.strip().strip('"'))
    return e


def enviar(texto, dry=False, para_turra=False):
    e = env()
    destino = e["ZAP_TURRA"] if para_turra else GRUPO
    if dry:
        print(f"[dry-run] iria pra {'o Turra' if para_turra else 'o grupo'} ({destino}), {len(texto)} caracteres:\n")
        print(texto)
        return
    url = e["ZAP_HUB_URL"].rstrip("/") + "/send-text"
    corpo = json.dumps({"phone": destino, "message": texto}).encode()
    req = urllib.request.Request(url, data=corpo, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", "Bearer " + e["ZAP_HUB_CHAVE"])
    req.add_header("User-Agent", "ilha-enviar/1")   # a Cloudflare barra o padrão do Python
    with urllib.request.urlopen(req, timeout=60) as r:
        print(json.loads(r.read().decode() or "{}"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("arquivo")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--daqui-a", type=int, default=0, help="segundos de espera antes de mandar")
    ap.add_argument("--para-turra", action="store_true", help="manda pro self-chat do Turra, não pro grupo")
    a = ap.parse_args()
    texto = open(a.arquivo, encoding="utf-8").read().rstrip("\n")
    if a.daqui_a:
        print(f"esperando {a.daqui_a}s…", flush=True)
        time.sleep(a.daqui_a)
    enviar(texto, a.dry_run, a.para_turra)


if __name__ == "__main__":
    main()

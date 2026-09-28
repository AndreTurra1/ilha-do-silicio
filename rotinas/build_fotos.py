"""Gera as fotos da página a partir do acervo de fotos das edições.

Fonte da verdade: acervo/fotos/catalogo.json (um item por arquivo do Google Fotos,
com o link original). Os originais (HEIC/MOV) moram em acervo/fotos/originais/,
fora do git: o repo é público e eles pesam GB.

Para cada item com "web", sai:
  fotos/web/<nome>.jpg   1600px no lado maior, pra abrir em tela cheia
  fotos/mini/<nome>.jpg   720px, a que aparece na grade

Sempre SEM EXIF: a foto de celular carrega GPS, e uma das edições foi numa casa.

Uso: python3 rotinas/build_fotos.py
"""
import json
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageOps

RAIZ = Path(__file__).resolve().parent.parent
ACERVO = RAIZ / "acervo" / "fotos"
ORIG = ACERVO / "originais"
SAIDA = {"web": (RAIZ / "fotos" / "web", 1600, 80), "mini": (RAIZ / "fotos" / "mini", 720, 74)}


def fonte(item, tmp):
    """Devolve um JPG em resolução cheia: converte HEIC ou tira o frame do vídeo."""
    arq = ORIG / item["edicao"] / item["arquivo"]
    destino = Path(tmp) / (item["web"]["nome"] + ".jpg")
    if arq.suffix.upper() == ".MOV":
        dur = float(subprocess.check_output(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", arq]))
        t = dur * item["web"]["frame"]
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{t:.2f}", "-i", arq,
                        "-frames:v", "1", "-q:v", "2", "-pix_fmt", "yuvj420p", destino], check=True)
    else:
        subprocess.run(["sips", "-s", "format", "jpeg", arq, "--out", destino],
                       check=True, capture_output=True)
    return destino


def main():
    cat = json.loads((ACERVO / "catalogo.json").read_text())
    for pasta, _, _ in SAIDA.values():
        pasta.mkdir(parents=True, exist_ok=True)
    feitos = 0
    with tempfile.TemporaryDirectory() as tmp:
        for item in cat["itens"]:
            if not item.get("web"):
                continue
            im = ImageOps.exif_transpose(Image.open(fonte(item, tmp))).convert("RGB")
            for pasta, lado, q in SAIDA.values():
                c = im.copy()
                c.thumbnail((lado, lado), Image.LANCZOS)
                # sem exif=: o Pillow não grava metadado nenhum
                c.save(pasta / (item["web"]["nome"] + ".jpg"), "JPEG", quality=q, optimize=True, progressive=True)
            feitos += 1
    print(f"{feitos} fotos geradas em fotos/web e fotos/mini")


if __name__ == "__main__":
    main()

# Acervo de fotos das edições

Fotos e vídeos das edições presenciais do Cowork Ilha do Silício, com o link original de cada
arquivo no Google Fotos (abre na conta andreht666@gmail.com, dona dos arquivos).

| Peça | Onde |
|---|---|
| Catálogo (fonte da verdade) | [`catalogo.json`](catalogo.json) |
| Originais HEIC/MOV | `acervo/fotos/originais/<data>/`, **só local**, fora do git (repo público, ~3 GB) |
| Versões da página | `fotos/web/` (1600px) e `fotos/mini/` (720px), sem EXIF/GPS |
| Gerador | [`rotinas/build_fotos.py`](../../rotinas/build_fotos.py) |

Itens pessoais e prints do mesmo dia (comprovantes de Pix, saldo, videochamada, prints de app)
ficaram **fora** do acervo de propósito. Os comprovantes de Pix têm nome de quem pagou.

## Nova edição

1. No Google Fotos, buscar a data, selecionar o dia e baixar (Shift+D).
2. Copiar os arquivos do evento pra `originais/<AAAA-MM-DD>/`.
3. Adicionar os itens no `catalogo.json` com o link `https://photos.google.com/photo/<id>`.
   Quem vai pra página ganha o bloco `web` (`frame` = ponto do vídeo, de 0 a 1).
4. `python3 rotinas/build_fotos.py` e colocar as `<li>` na seção `#edicoes` do `index.html`.

## 1ª edição: 03/09/2026 · Apartamento com varanda e vista pro mar

| Hora | Tipo | Arquivo | O que é | Página | Google Fotos |
|---|---|---|---|---|---|
| 15:03:30 | vídeo 51.7s | `IMG_2743.MOV` | Galera trabalhando na mesa da sala | ✅ `2026-09-03_mesa` | [abrir](https://photos.google.com/photo/AF1QipMWb0L2RQIDFmTFKkOAmKcMLpJdsCon0yUoqXTD) |
| 17:27:37 | foto | `IMG_2745.HEIC` | Notebook na mesa, sala com vista pro mar | ✅ `2026-09-03_sala-vista` | [abrir](https://photos.google.com/photo/AF1QipO86a23alcRjCsiimfdxrCl9HQ0qCs5rf95m6hg) |
| 17:27:41 | foto | `IMG_2746.HEIC` | Sala com vista (variação) | não | [abrir](https://photos.google.com/photo/AF1QipMSTUotMUTeWlvu3WyeXT2M59Jhiuf8v5tbeA6H) |
| 17:27:44 | foto | `IMG_2747.HEIC` | Sala com vista (variação) | não | [abrir](https://photos.google.com/photo/AF1QipPpup8Us3DpgZLGUbpceBt2COV-11Ckg_eIswga) |
| 17:27:45 | foto | `IMG_2748.HEIC` | Sala com vista (variação) | não | [abrir](https://photos.google.com/photo/AF1QipPIVR5SEOgzXHqI0-z5XsqR-9trmsUN8eHm0Rd-) |
| 17:34:19 | foto | `IMG_2749.HEIC` | Selfie da galera na varanda, fim de tarde | ✅ `2026-09-03_varanda-selfie` | [abrir](https://photos.google.com/photo/AF1QipNfU4s6YfK3H-3757U1KIfB--3Whj-Wi4mVh3zQ) |
| 17:57:04 | vídeo 75.2s | `IMG_2751.MOV` | Resenha na varanda | ✅ `2026-09-03_varanda-resenha` | [abrir](https://photos.google.com/photo/AF1QipOJose-2OY6I_XVvHRZYsxgdSRWWAeQnJKOryZQ) |
| 17:58:55 | vídeo 0.9s | `IMG_2752.MOV` | Clipe de 1s, sem conteúdo | não: sem conteúdo | [abrir](https://photos.google.com/photo/AF1QipMh7ceISXDyGHJZlcRt_BCwYXTT83XBElgxv-Vl) |
| 17:58:59 | foto | `IMG_2753.HEIC` | Pôr do sol na varanda, gente trabalhando | ✅ `2026-09-03_por-do-sol` | [abrir](https://photos.google.com/photo/AF1QipPn68VCb1kFVxY8Sm5POxlWnjJKUY7EaN9Fcqfw) |
| 19:38:48 | vídeo 38.0s | `IMG_2756.MOV` | Chegada à noite, rua e prédio | não | [abrir](https://photos.google.com/photo/AF1QipMafylaamZE37ceFmimmDGtQmrhrtsQkyQD2c3h) |
| 19:57:21 | foto | `IMG_2757.HEIC` | Churrasco na cozinha | ✅ `2026-09-03_churrasco` | [abrir](https://photos.google.com/photo/AF1QipMlSaBe3_TUm7vrXIHfZh8Z3j3j66q7JguKqjac) |
| 21:34:26 | vídeo 21.7s | `IMG_2758.MOV` | Vídeo tremido, rosto de perto | não: tremido | [abrir](https://photos.google.com/photo/AF1QipMMce23lBylL6sf-zgLIkypuJcyNM0laa7ptepq) |
| 22:01:58 | vídeo 76.5s | `IMG_2759.MOV` | Galera na cozinha à noite | ✅ `2026-09-03_cozinha` | [abrir](https://photos.google.com/photo/AF1QipPVpb1c1CHgISzq0ALttjQ4i4bgxEH6nyp2utfX) |
| 22:03:59 | foto | `IMG_2760.HEIC` | Sala à noite | não | [abrir](https://photos.google.com/photo/AF1QipOSRu0hE56xu-Svff_yxHDr6NjIASCB5DKoqugv) |
| 22:04:00 | foto | `IMG_2761.HEIC` | Balcão da cozinha à noite | não: reserva: a grade da 1ª edição fecha em 7 | [abrir](https://photos.google.com/photo/AF1QipOXUtePXqM-NcIQl3PBOuO0f5goE_oQs2YkGavi) |
| 22:31:36 | vídeo 1.3s | `IMG_2762.MOV` | Clipe de 1s escuro | não: sem conteúdo | [abrir](https://photos.google.com/photo/AF1QipNB1YtansBpCxFnQmflU7aIEv0_8YubYb5aBf0S) |
| 23:21:52 | vídeo 12.3s | `IMG_2763.MOV` | Brincadeira com a panela | não | [abrir](https://photos.google.com/photo/AF1QipOlgQuoLBbm9Z-cODfRAZAKd-Y8VGZZUmyoAEv-) |

## 2ª edição: 18/09/2026 · Casa com piscina e área gourmet

| Hora | Tipo | Arquivo | O que é | Página | Google Fotos |
|---|---|---|---|---|---|
| 14:20:03 | foto | `IMG_3031.HEIC` | Entrada da casa | ✅ `2026-09-18_entrada` | [abrir](https://photos.google.com/photo/AF1QipOZ4yORyQu45KfEIzFdNWGiKn3sjAUeKI9eGVxC) |
| 14:20:05 | vídeo 12.7s | `IMG_3032.MOV` | Chegada de carro | não: placa do carro aparece | [abrir](https://photos.google.com/photo/AF1QipO1o07Kg5QfbIS7pnWA--M2CgJ6uO8ZvzLyPZUM) |
| 14:20:33 | vídeo 32.4s | `IMG_3033.MOV` | Chegada de carro | não: placa do carro aparece | [abrir](https://photos.google.com/photo/AF1QipOUyDR4QbYS8SOgEfoc3Mwhmz56nnyhWILNb0Iw) |
| 14:21:38 | vídeo 78.3s | `IMG_3034.MOV` | Tour pela casa | não | [abrir](https://photos.google.com/photo/AF1QipNQuOqNQBVAgfmGDkIXCEgumGRHBMluN8brSehI) |
| 15:09:49 | foto | `10291F1A-B7BB-48E1-B18B-82B1F0F33F8D.jpg` | Galera trabalhando na área gourmet, piscina na frente | ✅ `2026-09-18_piscina-trabalho` | [abrir](https://photos.google.com/photo/AF1QipODjSxYoABkY36RGFAEwPlkpkEtxmCvzTtUKyoF) |
| 16:00:49 | vídeo 184.3s | `IMG_3037.MOV` | Trabalho no notebook, depoimento | não: tela com dado de trabalho | [abrir](https://photos.google.com/photo/AF1QipPBiapgD5aJ3Hcqpcj5nhw1doLuBosDZ_6uPmC3) |
| 16:22:09 | vídeo 44.2s | `IMG_3039.MOV` | Casa e deck | ✅ `2026-09-18_casa` | [abrir](https://photos.google.com/photo/AF1QipO9gzDxgdZ9Z94IOPzeu00Z16I-1dT-2hZlhdwU) |
| 17:16:17 | foto | `IMG_3040.HEIC` | Cookie do lanche | não | [abrir](https://photos.google.com/photo/AF1QipPWEicH3mlP3flymo5K-u5MG1uUlyvOMVR7tgcR) |
| 17:56:21 | foto | `IMG_3041.HEIC` | Casa com a piscina, galera na varanda | ✅ `2026-09-18_casa-piscina` | [abrir](https://photos.google.com/photo/AF1QipNZ9G87PNinukZz2n49x-f6zo2dMcEbS1x25fmJ) |
| 17:56:23 | vídeo 6.5s | `IMG_3042.MOV` | Galera no balcão da área gourmet | ✅ `2026-09-18_area-gourmet` | [abrir](https://photos.google.com/photo/AF1QipPO6QIBqnH88h3AJCOFGwY5xB1LPpzM1b6iCs4G) |
| 22:23:52 | vídeo 133.8s | `IMG_3043.MOV` | Resenha da noite, panela rodando | ✅ `2026-09-18_resenha` | [abrir](https://photos.google.com/photo/AF1QipOt1cI5782ivb-KpYemvb3EfXfWBTGbthZXDZT9) |

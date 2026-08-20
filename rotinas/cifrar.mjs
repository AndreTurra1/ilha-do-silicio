/**
 * Cifra o acervo pra ele poder morar num repositório PÚBLICO sem virar
 * conversa de 51 pessoas indexada no Google.
 *
 * Por que cifrar em vez de só "esconder": GitHub Pages serve tudo que está no
 * repo, e o repo da Ilha é público. Página com senha em JavaScript não protege
 * nada, porque o dado continua baixável direto pela URL. Aqui o que vai pro git
 * é BYTE CIFRADO: sem a frase-senha do grupo, o arquivo não diz nada, nem pro
 * Google nem pra quem achar a URL.
 *
 * Roda no WebCrypto do Node de propósito: é a MESMA implementação que o
 * navegador usa pra decifrar, então não existe divergência de formato entre
 * quem escreve e quem lê.
 *
 * Formato do .enc:  salt(16) ‖ iv(12) ‖ AES-256-GCM( gzip(JSON) )
 * Chave: PBKDF2-SHA256, 310.000 voltas (piso recomendado pelo OWASP em 2023).
 *
 * Uso:  node rotinas/cifrar.mjs entrada.json saida.enc "frase-senha"
 */
import { readFileSync, writeFileSync } from "node:fs";
import { gzipSync } from "node:zlib";
import { webcrypto as crypto } from "node:crypto";

const [entrada, saida, frase] = process.argv.slice(2);
if (!entrada || !saida || !frase) {
  console.error('uso: node rotinas/cifrar.mjs <entrada.json> <saida.enc> "<frase-senha>"');
  process.exit(1);
}

const ITER = 310000;
const salt = crypto.getRandomValues(new Uint8Array(16));
const iv = crypto.getRandomValues(new Uint8Array(12));

const base = await crypto.subtle.importKey(
  "raw", new TextEncoder().encode(frase), "PBKDF2", false, ["deriveKey"]
);
const chave = await crypto.subtle.deriveKey(
  { name: "PBKDF2", salt, iterations: ITER, hash: "SHA-256" },
  base, { name: "AES-GCM", length: 256 }, false, ["encrypt"]
);

const claro = gzipSync(readFileSync(entrada), { level: 9 });
const cifrado = new Uint8Array(
  await crypto.subtle.encrypt({ name: "AES-GCM", iv }, chave, claro)
);

const saidaBuf = new Uint8Array(salt.length + iv.length + cifrado.length);
saidaBuf.set(salt, 0);
saidaBuf.set(iv, salt.length);
saidaBuf.set(cifrado, salt.length + iv.length);
writeFileSync(saida, saidaBuf);

const kb = n => (n / 1024).toFixed(0) + " KB";
console.log(`${saida}: ${kb(readFileSync(entrada).length)} → gzip ${kb(claro.length)} → cifrado ${kb(saidaBuf.length)} (PBKDF2 ${ITER.toLocaleString("pt-BR")} voltas)`);

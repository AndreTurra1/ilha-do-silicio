/**
 * Abre o .enc do acervo de volta pra JSON. Par do cifrar.mjs.
 *
 * Existe porque o acervo é INCREMENTAL e o repositório só guarda byte cifrado:
 * pra somar as mensagens de hoje é preciso reabrir o que já estava lá. Sem isto
 * a única base seria o .txt do export na pasta de Downloads do Turra, que é
 * exatamente o tipo de dependência que some sem avisar.
 *
 * Uso: node rotinas/decifrar.mjs acervo/dados.enc saida.json "<frase-senha>"
 */
import { readFileSync, writeFileSync } from "node:fs";
import { gunzipSync } from "node:zlib";
import { webcrypto as crypto } from "node:crypto";

const [entrada, saida, frase] = process.argv.slice(2);
if (!entrada || !saida || !frase) {
  console.error('uso: node rotinas/decifrar.mjs <entrada.enc> <saida.json> "<frase-senha>"');
  process.exit(1);
}

const buf = readFileSync(entrada);
const salt = buf.subarray(0, 16), iv = buf.subarray(16, 28), ct = buf.subarray(28);

const base = await crypto.subtle.importKey(
  "raw", new TextEncoder().encode(frase), "PBKDF2", false, ["deriveKey"]
);
const chave = await crypto.subtle.deriveKey(
  { name: "PBKDF2", salt, iterations: 310000, hash: "SHA-256" },
  base, { name: "AES-GCM", length: 256 }, false, ["decrypt"]
);

let claro;
try {
  claro = await crypto.subtle.decrypt({ name: "AES-GCM", iv }, chave, ct);
} catch {
  // GCM autentica: frase errada não devolve lixo, estoura aqui
  console.error("frase-senha não abre este acervo");
  process.exit(2);
}
writeFileSync(saida, gunzipSync(Buffer.from(claro)));
console.log(`${saida}: ${JSON.parse(readFileSync(saida, "utf8")).msgs.length} mensagens`);

/**
 * Ilha do Silício — recebedor de cadastros
 * Cole este arquivo em Extensões › Apps Script da planilha e publique como Web App.
 * Ver README.md na raiz do projeto para o passo a passo.
 */

// Planilha de destino: "Ilha do Silício — Cadastros".
// https://docs.google.com/spreadsheets/d/1z8oxhUYd0h_mUDu35_S9UFWhjOS2y2C4N-IWb53JX6o/edit
const PLANILHA_ID = '1z8oxhUYd0h_mUDu35_S9UFWhjOS2y2C4N-IWb53JX6o';

// Nome da aba onde os cadastros são gravados (criada sozinha se não existir).
const ABA = 'Cadastros';

// Deixe '' para não receber aviso. Com um e-mail aqui, cada cadastro dispara uma notificação.
const NOTIFICAR_EMAIL = '';

const COLUNAS = [
  'Data/Hora', 'Nome', 'E-mail', 'WhatsApp', 'Área', 'Empresa/Projeto',
  'Frequência', 'Instagram/LinkedIn', 'Como conheceu', 'Sobre',
  'Entrar no grupo', 'Aceitou os termos', 'Versão dos termos', 'Origem',
  'Quem indicou'
];

function doPost(e) {
  try {
    if (!e || !e.postData || !e.postData.contents) return json({ ok: false, erro: 'sem corpo' });

    const d = JSON.parse(e.postData.contents);

    // Honeypot: bot preencheu o campo escondido → responde ok e descarta.
    if (d.website) return json({ ok: true });

    if (!d.nome || !d.email) return json({ ok: false, erro: 'nome e e-mail obrigatórios' });

    // Consentimento é a base legal do tratamento (LGPD art. 7º, I): sem aceite, não grava.
    if (d.aceite !== 'Sim') return json({ ok: false, erro: 'aceite dos termos obrigatório' });

    // Trava contra duas gravações simultâneas montarem a mesma linha.
    const lock = LockService.getScriptLock();
    lock.waitLock(20000);
    try {
      const aba = getAba();
      aba.appendRow([
        new Date(),
        String(d.nome       || '').slice(0, 200),
        String(d.email      || '').slice(0, 200),
        String(d.whatsapp   || '').slice(0, 40),
        String(d.area       || '').slice(0, 100),
        String(d.empresa    || '').slice(0, 200),
        String(d.frequencia || '').slice(0, 100),
        String(d.social     || '').slice(0, 200),
        String(d.origem     || '').slice(0, 300),
        String(d.sobre      || '').slice(0, 2000),
        String(d.grupo      || '').slice(0, 10),
        String(d.aceite     || '').slice(0, 10),
        String(d.termos     || '').slice(0, 40),
        String(d.origemUrl  || '').slice(0, 300),
        String(d.indicacao  || '').slice(0, 200)
      ]);
    } finally {
      lock.releaseLock();
    }

    if (NOTIFICAR_EMAIL) {
      MailApp.sendEmail(
        NOTIFICAR_EMAIL,
        'Novo cadastro na Ilha do Silício: ' + d.nome,
        [
          'Nome: '       + (d.nome       || ''),
          'E-mail: '     + (d.email      || ''),
          'WhatsApp: '   + (d.whatsapp   || ''),
          'Área: '       + (d.area       || ''),
          'Empresa: '    + (d.empresa    || ''),
          'Frequência: ' + (d.frequencia || ''),
          'Social: '     + (d.social     || ''),
          'Conheceu: '   + (d.origem     || ''),
          'Indicado por: ' + (d.indicacao || ''),
          '',
          (d.sobre || '')
        ].join('\n')
      );
    }

    return json({ ok: true });
  } catch (err) {
    return json({ ok: false, erro: String(err) });
  }
}

// Health check: abrir a URL /exec no navegador deve mostrar {"ok":true,...}
function doGet() {
  return json({ ok: true, servico: 'ilha-do-silicio', cadastros: getAba().getLastRow() - 1 });
}

function getAba() {
  // openById em vez de getActiveSpreadsheet: funciona mesmo com o script avulso.
  const ss = SpreadsheetApp.openById(PLANILHA_ID);
  let aba = ss.getSheetByName(ABA) || ss.insertSheet(ABA);

  if (aba.getLastRow() === 0) {
    aba.appendRow(COLUNAS);
    aba.getRange(1, 1, 1, COLUNAS.length)
       .setFontWeight('bold')
       .setBackground('#111823')
       .setFontColor('#ffffff');
    aba.setFrozenRows(1);
    aba.setColumnWidths(1, COLUNAS.length, 160);
  } else {
    // Planilha antiga: completa o cabeçalho com as colunas que passaram a existir depois.
    const largura = aba.getLastColumn();
    if (largura < COLUNAS.length) {
      const faltam = COLUNAS.slice(largura);
      aba.getRange(1, largura + 1, 1, faltam.length)
         .setValues([faltam])
         .setFontWeight('bold')
         .setBackground('#111823')
         .setFontColor('#ffffff');
      aba.setColumnWidths(largura + 1, faltam.length, 160);
    }
  }
  return aba;
}

function json(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

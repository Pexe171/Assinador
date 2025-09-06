const test = require('node:test');
const assert = require('node:assert/strict');
const { formatMessage, getDaysUntilDue, formatDate, renderTemplate } = require('../utils');

test('formatMessage substitui placeholders', () => {
  const template = 'Olá {nome}!';
  const result = formatMessage(template, { nome: 'Maria' });
  assert.equal(result, 'Olá Maria!');
});

test('formatMessage preserva placeholder ausente', () => {
  const template = 'Olá {nome}!';
  const result = formatMessage(template, {});
  assert.equal(result, 'Olá {nome}!');
});

test('formatDate converte para formato brasileiro', () => {
  const result = formatDate('2024-02-03');
  assert.equal(result, '03/02/2024');
});

test('getDaysUntilDue calcula datas relativas', () => {
  const today = new Date();
  const yyyy = today.getFullYear();
  const mm = String(today.getMonth() + 1).padStart(2, '0');
  const dd = String(today.getDate()).padStart(2, '0');
  const todayStr = `${yyyy}-${mm}-${dd}`;
  assert.equal(getDaysUntilDue(todayStr), 'Hoje');

  const future = new Date(today.getTime() + 2 * 24 * 60 * 60 * 1000);
  const futureStr = future.toISOString().slice(0, 10);
  assert.equal(getDaysUntilDue(futureStr), 'Em 2 dia(s)');
});

test('getDaysUntilDue identifica data inválida', () => {
  assert.equal(getDaysUntilDue('abc'), 'Data inválida');
});

test('renderTemplate mescla cliente e vars', () => {
  const cliente = {
    id: '1',
    nome: 'João',
    cpf: '123',
    sexo: 'Masculino',
    empreendimento: 'Emp',
    construtora: 'MRV',
    carta: 'FGTS',
    criadoEm: '',
    atualizadoEm: ''
  };
  const texto = renderTemplate('Olá {{nome}} - {{taxa}}', cliente, { taxa: '5%' });
  assert.equal(texto.startsWith('Olá João - 5%'), true);
});

test('renderTemplate valida obrigatorios', () => {
  const cliente = {
    id: '1', nome: 'João', cpf: '123', sexo: 'Masculino', empreendimento: 'Emp', construtora: 'MRV', carta: 'FGTS', criadoEm: '', atualizadoEm: ''
  };
  assert.throws(() => renderTemplate('Valor {{valor}}', cliente, {}, ['valor']));
});

test('renderTemplate normaliza carta SBTE para SBPE', () => {
  const cliente = {
    id: '2', nome: 'Ana', cpf: '321', sexo: 'Feminino', empreendimento: 'Emp', construtora: 'Direcional', carta: 'SBTE', criadoEm: '', atualizadoEm: ''
  };
  const texto = renderTemplate('Carta {{carta}}', cliente, {});
  assert.equal(texto, 'Carta SBPE');
});

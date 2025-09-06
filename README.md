# Gestor de Contas WA

Gerenciador de clientes e contas de WhatsApp com envio de mensagens. O projeto utiliza [Electron](https://www.electronjs.org/) e [whatsapp-web.js](https://github.com/pedroslopez/whatsapp-web.js) para oferecer uma interface simples e multiplataforma.

## Funcionalidades
- Conexão de múltiplas contas de WhatsApp.
- Cadastro de clientes com telefone, data de compra e data de vencimento.
- Verificação automática se o número do cliente está disponível no WhatsApp.
- Envio de mensagens em massa para clientes selecionados.
- Controle de contas vendidas com cálculo automático de receitas. (Gráficos em manutenção.)
- Persistência de dados local com *electron-store*.
- Exibição da quantidade total de clientes e dos resultados filtrados na lista.

## Requisitos
- [Node.js](https://nodejs.org/) 18 ou superior.
- NPM ou Yarn.

## Instalação
```bash
npm install
```

## Uso
1. Inicie o aplicativo em modo desenvolvimento:
   ```bash
   npm start
   ```
2. No primeiro acesso de cada conta de WhatsApp, será exibido um QR Code para pareamento.
3. Cadastre clientes conforme necessário.

## Build
Gere binários para distribuição com:
```bash
npm run pack   # build sem empacotamento
npm run dist   # executáveis para a plataforma
```
Os artefatos são gerados em `dist_electron/`.

## Atualização
Gere um executável de atualização que substitui apenas os arquivos de código e preserva os dados do cliente. Existem duas formas:

- Pelo aplicativo: vá ao menu **Configurações** e clique em **Gerar Atualizador**.
- Pela linha de comando:

  ```bash
  npm run gerar-atualizador
  ```
O binário criado em `atualizador/atualizacoes/` deve ser enviado ao cliente. Ao executá-lo, basta informar a pasta da instalação antiga. O diretório `dados/` não é sobrescrito e o arquivo `versao.txt` é atualizado.

## Estrutura do Projeto
- `main.js` – processo principal do Electron e orquestração da aplicação.
- `whatsapp.js` – gestor de múltiplas sessões do WhatsApp.
- `renderer/` – interface gráfica.
- `utils.js` – funções auxiliares.

## Testes
Os utilitários possuem testes básicos executados com o runner nativo do Node.js:
```bash
npm test
```

## Licença
Distribuído sob a licença ISC. Consulte o arquivo `package.json` para detalhes.

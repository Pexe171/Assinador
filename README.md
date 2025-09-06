# Gerenciador de Contas WhatsApp

Aplicação em Electron para gerir múltiplas contas do WhatsApp com fila de mensagens por conta. Utiliza [Electron](https://www.electronjs.org/), [whatsapp-web.js](https://github.com/pedroslopez/whatsapp-web.js) e [qrcode](https://www.npmjs.com/package/qrcode) para oferecer uma interface simples de conexão.

## Funcionalidades
- Conexão de múltiplas contas de WhatsApp.
- Exibição do estado de cada conta (Conectado, Reconectando, Desconectado).
- Persistência local de dados com *electron-store*.

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

## Build
Gere binários para distribuição com:
```bash
npm run pack   # build sem empacotamento
npm run dist   # executáveis para a plataforma
```
Os artefatos são gerados em `dist_electron/`.

## Testes
Os utilitários possuem testes básicos executados com o runner nativo do Node.js:
```bash
npm test
```

## Licença
Distribuído sob a licença ISC. Consulte o arquivo `package.json` para detalhes.

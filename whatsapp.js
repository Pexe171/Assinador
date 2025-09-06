// whatsapp.js
const { Client, LocalAuth } = require('whatsapp-web.js');
const QRCode = require('qrcode');

const PUPPETEER_ARGS = [
    '--no-sandbox',
    '--disable-setuid-sandbox',
    '--disable-gpu',
    '--disable-dev-shm-usage',
    '--disable-extensions',
    '--single-process',
    '--no-zygote',
    '--renderer-process-limit=1'
];

const clientsManager = {
    clients: new Map(),
    mainWindow: null,
    store: null,

    start(mainWindow, electronStore) {
        this.mainWindow = mainWindow;
        this.store = electronStore;
        this.loadAccountsFromStore();
    },

    loadAccountsFromStore() {
        const accounts = this.store.get('whatsappAccounts', []);
        this.clients.clear();
        accounts.forEach(acc => {
            this.clients.set(acc.id, {
                name: acc.name,
                client: null,
                isReady: false,
                isInitializing: false,
                status: 'disconnected'
            });
        });
    },

    async initializeClient(accountId) {
        const clientState = this.clients.get(accountId);
        if (!clientState || clientState.isInitializing || clientState.client) {
            return;
        }

        clientState.isInitializing = true;
        this.updateAccountState(accountId, 'reconnecting');

        const waClient = new Client({
            authStrategy: new LocalAuth({
                clientId: accountId,
                dataPath: "sessions"
            }),
            puppeteer: {
                headless: true,
                args: PUPPETEER_ARGS
            }
        });

        clientState.client = waClient;

        waClient.on('qr', (qr) => {
            this.updateAccountState(accountId, 'reconnecting');
            QRCode.toDataURL(qr).then(url => {
                this.mainWindow.webContents.send('whatsapp-qr-code', accountId, url);
            });
        });

        waClient.on('ready', async () => {
            clientState.isReady = true;
            this.updateAccountState(accountId, 'connected');
        });

        waClient.on('disconnected', (reason) => {
            this.destroyClient(accountId, false);
        });

        try {
            await waClient.initialize();
        } catch (error) {
            await this.destroyClient(accountId, false);
        } finally {
            clientState.isInitializing = false;
        }
    },

    async destroyClient(accountId, fullRemove = false) {
        const clientState = this.clients.get(accountId);
        if (clientState?.client) {
            await clientState.client.destroy().catch(() => {});
            if (global.gc) {
                try { global.gc(); } catch (_) { /* ignore */ }
            }
        }

        if (fullRemove) {
            this.clients.delete(accountId);
        } else if (clientState) {
            clientState.client = null;
            clientState.isReady = false;
            clientState.isInitializing = false;
            this.updateAccountState(accountId, 'disconnected');
        }
        this.updateOverallState();
    },

    addAccount(account) {
        this.clients.set(account.id, {
            name: account.name,
            client: null,
            isReady: false,
            isInitializing: false,
            status: 'disconnected'
        });
        this.updateOverallState();
    },

    renameAccount(accountId, newName) {
        const clientState = this.clients.get(accountId);
        if(clientState) {
            clientState.name = newName;
            this.updateOverallState();
        }
    },

    async sendMessage(accountId, phoneNumber, message) {
        const clientState = this.clients.get(accountId);
        if (!clientState || !clientState.isReady) {
            throw new Error(`Conta WhatsApp ${clientState?.name || accountId} não está conectada.`);
        }
        const chatId = phoneNumber.endsWith('@c.us') ? phoneNumber : `${phoneNumber}@c.us`;
        await clientState.client.sendMessage(chatId, message);
    },

    updateAccountState(accountId, status) {
        const clientState = this.clients.get(accountId);
        if (clientState) {
            clientState.status = status;
            this.updateOverallState();
        }
    },

    updateOverallState() {
        if (this.mainWindow?.webContents) {
            this.mainWindow.webContents.send('whatsapp-state-change', this.getClientsState());
        }
    },

    getClientsState() {
        const stateArray = [];
        for (const [id, state] of this.clients.entries()) {
            stateArray.push({ id, name: state.name, status: state.status });
        }
        return stateArray;
    },

    getReadyClients() {
        const readyClients = new Map();
        for (const [id, state] of this.clients.entries()) {
            if (state.isReady && state.client) {
                readyClients.set(id, state.client);
            }
        }
        return readyClients;
    }
};

module.exports = { clientsManager };

// main.js
const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const Store = require('electron-store');
const { clientsManager } = require('./whatsapp');

// Schema da base de dados local
const schema = {
    whatsappAccounts: {
        type: 'array',
        default: [{ id: 'default', name: 'Conta Principal' }]
    },
    mrvClients: {
        type: 'array',
        default: []
    },
    direcionalClients: {
        type: 'array',
        default: []
    },
    olaCasaNovaClients: {
        type: 'array',
        default: []
    }
};

const store = new Store({ schema });
let mainWindow;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1280,
        height: 800,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            contextIsolation: true,
        },
        icon: path.join(__dirname, 'assets/icon.png')
    });

    // Ativa DevTools e redireciona logs para facilitar depuração
    mainWindow.webContents.openDevTools({ mode: 'detach' });

    const forwardLog = (level, args) => {
        if (mainWindow?.webContents) {
            const message = args
                .map(a => (a && a.stack) ? a.stack : a)
                .join(' ');
            mainWindow.webContents.send('debug-log', { level, message });
        }
    };

    ['log', 'warn', 'error'].forEach(level => {
        const original = console[level];
        console[level] = (...args) => {
            original.apply(console, args);
            forwardLog(level, args);
        };
    });

    process.on('uncaughtException', err => console.error('uncaughtException', err));
    process.on('unhandledRejection', reason => console.error('unhandledRejection', reason));

    // Inicia o gestor de contas WhatsApp
    clientsManager.start(mainWindow, store);

    mainWindow.loadFile(path.join(__dirname, 'renderer/index.html'));
    mainWindow.on('closed', () => { mainWindow = null; });
}

// Eventos do ciclo de vida da aplicação
app.whenReady().then(() => {
    createWindow();
});

app.on('window-all-closed', async () => {
    const accounts = store.get('whatsappAccounts');
    for (const account of accounts) {
        await clientsManager.destroyClient(account.id);
    }
    if (process.platform !== 'darwin') app.quit();
});

// --- Handlers de Contas WhatsApp ---
ipcMain.handle('get-whatsapp-accounts', () => {
    const accounts = store.get('whatsappAccounts');
    const states = clientsManager.getClientsState();
    return accounts.map(acc => {
        const state = states.find(s => s.id === acc.id);
        return { ...acc, status: state ? state.status : 'disconnected' };
    });
});

ipcMain.handle('add-whatsapp-account', (event, name) => {
    const accounts = store.get('whatsappAccounts');
    const newAccount = { id: `wa-${Date.now()}`, name };
    accounts.push(newAccount);
    store.set('whatsappAccounts', accounts);
    clientsManager.addAccount(newAccount);
    return newAccount;
});

ipcMain.handle('remove-whatsapp-account', async (event, accountId) => {
    let accounts = store.get('whatsappAccounts');
    accounts = accounts.filter(acc => acc.id !== accountId);
    store.set('whatsappAccounts', accounts);
    await clientsManager.destroyClient(accountId, true);
    return { success: true };
});

ipcMain.handle('rename-whatsapp-account', (event, accountId, newName) => {
    let accounts = store.get('whatsappAccounts');
    const account = accounts.find(acc => acc.id === accountId);
    if (account) {
        account.name = newName;
        store.set('whatsappAccounts', accounts);
        clientsManager.renameAccount(accountId, newName);
    }
    return { success: !!account };
});

ipcMain.on('request-qr-code', (event, accountId) => {
    clientsManager.initializeClient(accountId);
});

ipcMain.handle('disconnect-whatsapp', async (event, accountId) => {
    await clientsManager.destroyClient(accountId, false);
    return { success: true };
});

// --- Handlers de Clientes por Construtora ---
const companyKeys = {
    mrv: 'mrvClients',
    direcional: 'direcionalClients',
    ola: 'olaCasaNovaClients'
};

ipcMain.handle('get-clients', (event, company) => {
    const key = companyKeys[company];
    if (!key) return [];
    return store.get(key) || [];
});

ipcMain.handle('add-client', (event, company, data) => {
    const key = companyKeys[company];
    if (!key) return null;
    const clients = store.get(key) || [];
    const newClient = {
        id: `cli-${Date.now()}`,
        nome: data.nome,
        cpf: data.cpf,
        sexo: data.sexo,
        empreendimento: data.empreendimento,
        carta: data.carta,
        ficha: data.ficha,
        mensagens: []
    };
    clients.push(newClient);
    store.set(key, clients);
    return newClient;
});

ipcMain.handle('update-client', (event, company, id, data) => {
    const key = companyKeys[company];
    if (!key) return { success: false };
    const clients = store.get(key) || [];
    const idx = clients.findIndex(c => c.id === id);
    if (idx === -1) return { success: false };
    clients[idx] = { ...clients[idx], ...data };
    store.set(key, clients);
    return { success: true };
});

ipcMain.handle('delete-client', (event, company, id) => {
    const key = companyKeys[company];
    if (!key) return { success: false };
    let clients = store.get(key) || [];
    const initialLength = clients.length;
    clients = clients.filter(c => c.id !== id);
    store.set(key, clients);
    return { success: clients.length < initialLength };
});

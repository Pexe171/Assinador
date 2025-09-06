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

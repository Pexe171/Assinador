// preload.js
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  getWhatsAppAccounts: () => ipcRenderer.invoke('get-whatsapp-accounts'),
  addWhatsAppAccount: (name) => ipcRenderer.invoke('add-whatsapp-account', name),
  removeWhatsAppAccount: (accountId) => ipcRenderer.invoke('remove-whatsapp-account', accountId),
  renameWhatsAppAccount: (accountId, newName) => ipcRenderer.invoke('rename-whatsapp-account', accountId, newName),
  requestQRCode: (accountId) => ipcRenderer.send('request-qr-code', accountId),
  disconnectWhatsApp: (accountId) => ipcRenderer.invoke('disconnect-whatsapp', accountId),
  onWhatsAppStateChange: (callback) => ipcRenderer.on('whatsapp-state-change', (_event, accounts) => callback(accounts)),
  onWhatsAppQRCode: (callback) => ipcRenderer.on('whatsapp-qr-code', (_event, accountId, qr) => callback(accountId, qr)),
  getClients: (company) => ipcRenderer.invoke('get-clients', company),
  addClient: (company, data) => ipcRenderer.invoke('add-client', company, data),
  updateClient: (company, id, data) => ipcRenderer.invoke('update-client', company, id, data),
  deleteClient: (company, id) => ipcRenderer.invoke('delete-client', company, id),
  removeAllListeners: (channel) => ipcRenderer.removeAllListeners(channel)
});

// renderer.js

document.addEventListener('DOMContentLoaded', () => {
    const whatsappAccountsListEl = document.getElementById('whatsapp-accounts-list');
    const btnAddWhatsAppAccount = document.getElementById('btn-add-whatsapp-account');
    const modalOverlay = document.getElementById('custom-modal-overlay');

    /* Navegação principal */
    const navLinks = document.querySelectorAll('.navigation a');
    const viewsMap = {
        'nav-whatsapp-status': 'view-whatsapp-status',
        'nav-mrv': 'view-mrv',
        'nav-direcional': 'view-direcional',
        'nav-ola-casa-nova': 'view-ola-casa-nova'
    };
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            navLinks.forEach(l => l.classList.remove('active'));
            document.querySelectorAll('.content-view').forEach(v => v.classList.add('hidden'));
            link.classList.add('active');
            const viewId = viewsMap[link.id];
            if (viewId) document.getElementById(viewId).classList.remove('hidden');
        });
    });

    /* Sub-abas para construtoras */
    document.querySelectorAll('.sub-tabs').forEach(container => {
        container.addEventListener('click', (e) => {
            const btn = e.target.closest('.sub-tab');
            if (!btn) return;
            const parentCard = container.parentElement;
            container.querySelectorAll('.sub-tab').forEach(b => b.classList.remove('active'));
            parentCard.querySelectorAll('.sub-tab-content').forEach(c => c.classList.add('hidden'));
            btn.classList.add('active');
            const targetId = btn.dataset.target;
            const targetEl = parentCard.querySelector(`#${targetId}`);
            if (targetEl) targetEl.classList.remove('hidden');
        });
    });

    let whatsappAccountsMap = new Map();
    let currentModalConfirmCallback = null;

    function showModal(title, message, type = 'info', onConfirm = null) {
        modalOverlay.innerHTML = `
            <div class="modal-content">
                <h3 class="modal-title-text">${title}</h3>
                <p class="modal-message-text">${message.replace(/\n/g, '<br>')}</p>
                <div class="modal-actions">
                    <button id="modal-btn-confirm" class="btn-modal btn-modal-confirm" style="display: ${type === 'confirm' ? 'inline-block' : 'none'}">Sim</button>
                    <button id="modal-btn-cancel" class="btn-modal btn-modal-cancel" style="display: ${type === 'confirm' ? 'inline-block' : 'none'}">Não</button>
                    <button id="modal-btn-ok" class="btn-modal btn-modal-ok" style="display: ${type !== 'confirm' ? 'inline-block' : 'none'}">OK</button>
                </div>
            </div>
        `;
        currentModalConfirmCallback = onConfirm;
        document.getElementById('modal-btn-confirm').addEventListener('click', () => { if (currentModalConfirmCallback) currentModalConfirmCallback(); hideModal(); });
        document.getElementById('modal-btn-cancel').addEventListener('click', hideModal);
        document.getElementById('modal-btn-ok').addEventListener('click', () => { if (currentModalConfirmCallback) currentModalConfirmCallback(); hideModal(); });
        modalOverlay.classList.add('visible');
    }

    function showInputModal(title, message, placeholder, onConfirm) {
        modalOverlay.innerHTML = `
            <div class="modal-content">
                <h3 class="modal-title-text">${title}</h3>
                <p class="modal-message-text">${message}</p>
                <input type="text" id="modal-input-field" class="modal-input" placeholder="${placeholder}">
                <div class="modal-actions">
                    <button id="modal-input-confirm" class="btn-modal btn-modal-confirm">Confirmar</button>
                    <button id="modal-input-cancel" class="btn-modal btn-modal-cancel">Cancelar</button>
                </div>
            </div>
        `;
        const inputField = document.getElementById('modal-input-field');
        inputField.focus();
        document.getElementById('modal-input-confirm').addEventListener('click', () => {
            const value = inputField.value;
            if (value && value.trim() !== '') {
                onConfirm(value.trim());
                hideModal();
            }
        });
        inputField.addEventListener('keydown', (e) => { if (e.key === 'Enter') { document.getElementById('modal-input-confirm').click(); } });
        document.getElementById('modal-input-cancel').addEventListener('click', hideModal);
        modalOverlay.classList.add('visible');
    }

    function hideModal() {
        modalOverlay.classList.remove('visible');
        modalOverlay.innerHTML = '';
    }

    async function loadAndRenderWhatsAppAccounts() {
        const accounts = await window.electronAPI.getWhatsAppAccounts();
        whatsappAccountsMap.clear();
        accounts.forEach(acc => whatsappAccountsMap.set(acc.id, acc));
        renderWhatsAppAccounts();
    }

    function renderWhatsAppAccounts() {
        whatsappAccountsListEl.innerHTML = '';
        if (whatsappAccountsMap.size === 0) {
            whatsappAccountsListEl.innerHTML = `<p class="empty-list-message">Nenhuma conta de WhatsApp adicionada.</p>`;
            return;
        }

        whatsappAccountsMap.forEach(account => {
            const accountDiv = document.createElement('div');
            accountDiv.className = `account-item status-${account.status || 'disconnected'}`;
            accountDiv.dataset.accountId = account.id;

            let statusText = 'Desconectado';
            let statusIndicator = '<i class="fas fa-times-circle status-icon disconnected"></i>';
            if (account.status === 'connected') { statusText = 'Conectado'; statusIndicator = '<i class="fas fa-check-circle status-icon ready"></i>'; }
            if (account.status === 'reconnecting') { statusText = 'Reconectando'; statusIndicator = '<i class="fas fa-circle-notch fa-spin status-icon initializing"></i>'; }

            accountDiv.innerHTML = `
                <div class="account-header">
                    <strong class="account-name">${account.name}</strong>
                    <div class="account-status">${statusIndicator}<span>${statusText}</span></div>
                </div>
                <div class="account-body">
                    <div class="qr-code-container" id="qr-container-${account.id}"></div>
                </div>
                <div class="account-actions">
                    <button class="btn-connect" data-action="connect" ${account.status === 'connected' || account.status === 'reconnecting' ? 'disabled' : ''}><i class="fas fa-link"></i> Conectar</button>
                    <button class="btn-disconnect btn-danger" data-action="disconnect" ${account.status !== 'connected' ? 'disabled' : ''}><i class="fas fa-unlink"></i> Desconectar</button>
                    <button class="btn-rename" data-action="rename"><i class="fas fa-pencil-alt"></i> Renomear</button>
                    <button class="btn-delete-account btn-danger" data-action="delete"><i class="fas fa-trash"></i> Remover</button>
                </div>
            `;
            whatsappAccountsListEl.appendChild(accountDiv);
        });
    }

    btnAddWhatsAppAccount.addEventListener('click', () => {
        showInputModal('Adicionar Conta', 'Nome da nova conta:', 'Nome', async (name) => {
            const newAcc = await window.electronAPI.addWhatsAppAccount(name);
            whatsappAccountsMap.set(newAcc.id, { ...newAcc, status: 'disconnected' });
            renderWhatsAppAccounts();
        });
    });

    whatsappAccountsListEl.addEventListener('click', async (e) => {
        const action = e.target.closest('button')?.dataset.action;
        if (!action) return;
        const accountId = e.target.closest('.account-item').dataset.accountId;
        const account = whatsappAccountsMap.get(accountId);
        switch (action) {
            case 'connect':
                window.electronAPI.requestQRCode(accountId);
                break;
            case 'disconnect':
                await window.electronAPI.disconnectWhatsApp(accountId);
                break;
            case 'rename':
                showInputModal('Renomear Conta', 'Novo nome:', account.name, async (newName) => {
                    await window.electronAPI.renameWhatsAppAccount(accountId, newName);
                    account.name = newName;
                    renderWhatsAppAccounts();
                });
                break;
            case 'delete':
                showModal('Remover Conta', `Tem certeza que deseja remover "${account.name}"?`, 'confirm', async () => {
                    await window.electronAPI.removeWhatsAppAccount(accountId);
                    whatsappAccountsMap.delete(accountId);
                    renderWhatsAppAccounts();
                });
                break;
        }
    });

    window.electronAPI.onWhatsAppStateChange((accounts) => {
        accounts.forEach(acc => {
            const existing = whatsappAccountsMap.get(acc.id);
            if (existing) {
                existing.status = acc.status;
            }
        });
        renderWhatsAppAccounts();
    });

    window.electronAPI.onWhatsAppQRCode((accountId, qr) => {
        const container = document.getElementById(`qr-container-${accountId}`);
        if (container) {
            container.innerHTML = `<img src="${qr}" alt="QR Code">`;
        }
    });

    loadAndRenderWhatsAppAccounts();
});

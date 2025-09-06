// renderer.js

document.addEventListener('DOMContentLoaded', () => {
    const whatsappAccountsListEl = document.getElementById('whatsapp-accounts-list');
    const btnAddWhatsAppAccount = document.getElementById('btn-add-whatsapp-account');
    const modalOverlay = document.getElementById('custom-modal-overlay');

    // Recebe logs do processo principal e exibe no console do DevTools
    window.electronAPI.onDebugLog(({ level, message }) => {
        const log = console[level] || console.log;
        log(`[MAIN] ${message}`);
    });

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

    // --- Clientes por Construtora ---
    const clientCompanies = ['mrv', 'direcional', 'ola'];
    const clientsMap = { mrv: [], direcional: [], ola: [] };

    clientCompanies.forEach(company => {
        loadClients(company);
        const addBtn = document.getElementById(`${company}-btn-add-client`);
        if (addBtn) addBtn.addEventListener('click', () => openClientForm(company));

        ['nome','cpf','empreendimento','carta','sexo'].forEach(field => {
            const el = document.getElementById(`${company}-filter-${field}`);
            if (!el) return;
            const evt = el.tagName === 'SELECT' ? 'change' : 'input';
            el.addEventListener(evt, () => renderClients(company));
        });

        const listEl = document.getElementById(`${company}-clients-list`);
        if (listEl) {
            listEl.addEventListener('click', (e) => {
                const action = e.target.dataset.action;
                if (!action) return;
                const id = e.target.closest('.client-item')?.dataset.id;
                const client = clientsMap[company].find(c => c.id === id);
                if (action === 'edit') {
                    openClientForm(company, client);
                } else if (action === 'delete') {
                    showModal('Remover Cliente', `Deseja remover ${client.nome}?`, 'confirm', async () => {
                        await window.electronAPI.deleteClient(company, id);
                        await loadClients(company);
                    });
                } else if (action === 'detail') {
                    showClientDetail(client);
                }
            });
        }
    });

    async function loadClients(company) {
        clientsMap[company] = await window.electronAPI.getClients(company);
        renderClients(company);
    }

    function getFilters(company) {
        return {
            nome: document.getElementById(`${company}-filter-nome`).value.trim().toLowerCase(),
            cpf: document.getElementById(`${company}-filter-cpf`).value.trim(),
            empreendimento: document.getElementById(`${company}-filter-empreendimento`).value.trim().toLowerCase(),
            carta: document.getElementById(`${company}-filter-carta`).value,
            sexo: document.getElementById(`${company}-filter-sexo`).value
        };
    }

    function renderClients(company) {
        const listEl = document.getElementById(`${company}-clients-list`);
        const filters = getFilters(company);
        let clients = clientsMap[company];
        clients = clients.filter(c =>
            (!filters.nome || c.nome.toLowerCase().includes(filters.nome)) &&
            (!filters.cpf || c.cpf.includes(filters.cpf)) &&
            (!filters.empreendimento || c.empreendimento.toLowerCase().includes(filters.empreendimento)) &&
            (!filters.carta || c.carta === filters.carta) &&
            (!filters.sexo || c.sexo === filters.sexo)
        );
        listEl.innerHTML = '';
        if (clients.length === 0) {
            listEl.innerHTML = `<p class="empty-list-message">Nenhum cliente.</p>`;
            return;
        }
        clients.forEach(c => {
            const div = document.createElement('div');
            div.className = 'client-item';
            div.dataset.id = c.id;
            div.innerHTML = `
                <div class="client-main">
                    <strong>${c.nome}</strong> - ${c.cpf}
                </div>
                <div class="client-actions">
                    <button data-action="detail" class="btn-link">Detalhes</button>
                    <button data-action="edit" class="btn-link">Editar</button>
                    <button data-action="delete" class="btn-link text-danger">Excluir</button>
                </div>
            `;
            listEl.appendChild(div);
        });
    }

    function openClientForm(company, client = null) {
        modalOverlay.innerHTML = `
            <div class="modal-content">
                <h3 class="modal-title-text">${client ? 'Editar' : 'Adicionar'} Cliente</h3>
                <form id="client-form" class="client-form">
                    <input type="text" id="form-nome" placeholder="Nome" value="${client ? client.nome : ''}" required>
                    <input type="text" id="form-cpf" placeholder="CPF" value="${client ? client.cpf : ''}" required>
                    <select id="form-sexo" required>
                        <option value="">Sexo</option>
                        <option value="M" ${client && client.sexo === 'M' ? 'selected' : ''}>Masculino</option>
                        <option value="F" ${client && client.sexo === 'F' ? 'selected' : ''}>Feminino</option>
                    </select>
                    <input type="text" id="form-empreendimento" placeholder="Empreendimento" value="${client ? client.empreendimento : ''}" required>
                    <select id="form-carta" required>
                        <option value="">Carta</option>
                        <option value="SBPE" ${client && client.carta === 'SBPE' ? 'selected' : ''}>SBPE</option>
                        <option value="FGTS" ${client && client.carta === 'FGTS' ? 'selected' : ''}>FGTS</option>
                    </select>
                    <input type="file" id="form-ficha" ${client ? '' : 'required'}>
                    <div class="modal-actions">
                        <button type="submit" class="btn-modal btn-modal-confirm">Salvar</button>
                        <button type="button" id="form-cancel" class="btn-modal btn-modal-cancel">Cancelar</button>
                    </div>
                </form>
            </div>
        `;
        modalOverlay.classList.add('visible');
        const form = document.getElementById('client-form');
        document.getElementById('form-cancel').addEventListener('click', hideModal);
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const data = {
                nome: document.getElementById('form-nome').value.trim(),
                cpf: document.getElementById('form-cpf').value.trim(),
                sexo: document.getElementById('form-sexo').value,
                empreendimento: document.getElementById('form-empreendimento').value.trim(),
                carta: document.getElementById('form-carta').value,
                ficha: document.getElementById('form-ficha').files[0]?.path || (client ? client.ficha : '')
            };
            if (!validarCPF(data.cpf)) {
                showModal('Erro', 'CPF inválido.');
                return;
            }
            if (client) {
                await window.electronAPI.updateClient(company, client.id, data);
            } else {
                await window.electronAPI.addClient(company, data);
            }
            hideModal();
            await loadClients(company);
        });
    }

    function showClientDetail(client) {
        let mensagensHtml = '';
        if (client.mensagens && client.mensagens.length > 0) {
            mensagensHtml = '<ul>' + client.mensagens.map(m => `<li>${m}</li>`).join('') + '</ul>';
        } else {
            mensagensHtml = '<p>Nenhuma mensagem.</p>';
        }
        modalOverlay.innerHTML = `
            <div class="modal-content">
                <h3 class="modal-title-text">Detalhes do Cliente</h3>
                <p><strong>Nome:</strong> ${client.nome}</p>
                <p><strong>CPF:</strong> ${client.cpf}</p>
                <p><strong>Sexo:</strong> ${client.sexo}</p>
                <p><strong>Empreendimento:</strong> ${client.empreendimento}</p>
                <p><strong>Carta:</strong> ${client.carta}</p>
                <p><strong>Ficha:</strong> ${client.ficha || '-'}</p>
                <h4>Histórico de Mensagens</h4>
                ${mensagensHtml}
                <div class="modal-actions">
                    <button id="modal-btn-ok" class="btn-modal btn-modal-ok">OK</button>
                </div>
            </div>
        `;
        document.getElementById('modal-btn-ok').addEventListener('click', hideModal);
        modalOverlay.classList.add('visible');
    }

    function validarCPF(cpf) {
        cpf = cpf.replace(/\D/g, '');
        if (cpf.length !== 11 || /(\d)\1{10}/.test(cpf)) return false;
        let soma = 0, resto;
        for (let i = 1; i <= 9; i++) soma += parseInt(cpf.substring(i - 1, i)) * (11 - i);
        resto = (soma * 10) % 11;
        if (resto === 10 || resto === 11) resto = 0;
        if (resto !== parseInt(cpf.substring(9, 10))) return false;
        soma = 0;
        for (let i = 1; i <= 10; i++) soma += parseInt(cpf.substring(i - 1, i)) * (12 - i);
        resto = (soma * 10) % 11;
        if (resto === 10 || resto === 11) resto = 0;
        return resto === parseInt(cpf.substring(10, 11));
    }
});

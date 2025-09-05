# Assinador

Aplicativo desktop em Python/PySide6 para enviar formulários e validar assinaturas eletrônicas de clientes.

## Estrutura

```
assinar-desktop/
├─ .env.example
├─ requirements.txt
├─ make.ps1
├─ assets/
│  ├─ logos/
│  └─ themes/
├─ app/
│  ├─ main.py
│  ├─ ui/
│  │  ├─ window.py
│  │  └─ tray.py
│  ├─ core/
│  │  ├─ config.py
│  │  ├─ db.py
│  │  ├─ models.py
│  │  └─ theming.py
│  ├─ services/
│  │  ├─ whatsapp.py
│  │  ├─ govbr.py
│  │  ├─ icpbr.py
│  │  ├─ validator.py
│  │  └─ tunnel.py
│  ├─ server/
│  │  ├─ http.py
│  │  ├─ webhooks_wa.py
│  │  ├─ callbacks_govbr.py
│  │  └─ callbacks_icpbr.py
│  └─ flows/
│     ├─ first_contact.py
│     ├─ send_form.py
│     └─ validate_and_notify.py
├─ build/
│  ├─ assinar.spec
│  └─ icon.ico
└─ tests/
```

## Execução

```powershell
# Executar a aplicação
./make.ps1 run

# Gerar executável
./make.ps1 build
```

## Autor

Pexe – [Instagram: David.devloli](https://instagram.com/David.devloli)

# Passo 4 — Template e Corpo do E-mail

Este passo consolida o padrão de comunicação do Assinador com foco na validação de renda. O objetivo imediato é manter o uso de arquivos **`.oft`** (compatíveis com Outlook/Exchange) enriquecidos por placeholders para personalização dinâmica. Na sequência, abriremos caminho para suportar conteúdo **HTML/Handlebars**, transformando o motor em uma plataforma reutilizável para outros fluxos (contratos, notificações internas etc.).

## 1. Assunto padrão e rastreamento universal

* Assunto fixo: `Validação de Renda – {{NOME}} – CPF {{CPF}} – {{ID}}`.
* O campo `{{ID}}` funciona como âncora de rastreamento independente do provedor. Ele deve ser persistido e referenciado em todos os envelopes e logs.
* O prefixo do assunto não deve ser alterado por provedores ou filas intermediárias. Adapters que manipularem o assunto precisam preservar o formato.

## 2. Estrutura do template `.oft`

1. Criar o corpo no Outlook utilizando HTML base (vide seção 4) e salvar como **Modelo do Outlook (`.oft`)**.
2. Garantir que o template esteja versionado em `universal-mailer/templates/validacao_renda.oft`.
3. Utilizar placeholders em formato `{{CHAVE}}` para permitir substituição server-side.
4. Validar que o arquivo mantém a codificação UTF-8 e fontes padrão (`Segoe UI`).
5. Incluir assinatura institucional da Caixa, conforme orientações de branding.

> **Observação:** sempre que houver atualização no layout, exportar novamente o `.oft` com o mesmo nome de arquivo para preservar automações. Alterações relevantes devem ser descritas no changelog do repositório.

## 3. Placeholders disponíveis

| Placeholder | Descrição | Origem |
|-------------|-----------|--------|
| `{{NOME}}` | Nome completo do cliente. | Cadastro no CRM ou payload do processo. |
| `{{CPF}}` | CPF formatado (`000.000.000-00`). | Serviço de validação de identidade. |
| `{{ID}}` | Identificador universal do processo (UUID/protocolo). | Motor de rastreamento do Assinador. |
| `{{SITUACAO_ATUAL}}` | Status atual da análise (ex.: "Documentos recebidos"). | Workflow de renda. |
| `{{URL_PORTAL}}` | Link seguro para upload ou acompanhamento. | Serviço de portal do cliente. |

Adapters e serviços que renderizam o template devem expor validações para impedir envios com placeholders não resolvidos.

## 4. HTML de referência

Para facilitar a criação do `.oft`, mantemos um HTML base em `universal-mailer/templates/validacao_renda_body.html`. Ele já contempla estilo responsivo, linguagem inclusiva e espaços reservados para os placeholders:

```html
<!DOCTYPE html>
<html lang="pt-BR">
  <head>
    <!-- ... -->
  </head>
  <body>
    <div class="container">
      <p>Olá, <strong>{{NOME}}</strong>.</p>
      <p>
        Recebemos a documentação enviada para a <strong>Validação de Renda</strong>
        referente ao CPF <strong>{{CPF}}</strong> (protocolo <strong>{{ID}}</strong>).
      </p>
      <p class="highlight">
        Situação atual: <strong>{{SITUACAO_ATUAL}}</strong>
      </p>
      <p>
        Caso seja necessário complementar informações, utilize o botão para acessar o
        portal seguro e anexar os documentos solicitados.
      </p>
      <p style="text-align: center;">
        <a class="cta" href="{{URL_PORTAL}}" target="_blank" rel="noopener">
          Acessar portal seguro
        </a>
      </p>
    </div>
  </body>
</html>
```

### Boas práticas

* Centralizar os estilos no `<style>` para evitar incompatibilidades no Outlook.
* Garantir contraste adequado entre texto e plano de fundo.
* Usar links com `rel="noopener"` e `target="_blank"` para segurança e experiência.
* Evitar imagens como texto principal (acessibilidade e filtros antispam).

## 5. Próximos passos — HTML/Handlebars

1. Criar pipeline de renderização que aceite fontes `.oft` e `.html` (Handlebars) de forma intercambiável.
2. Introduzir testes automatizados para validar placeholders obrigatórios.
3. Permitir armazenamento de múltiplos templates por fluxo, incluindo versões A/B.
4. Expor API interna para consulta de templates ativos.

Essa etapa garante um padrão consistente para comunicações críticas, mantendo o alinhamento com as diretrizes da Caixa e preparando o terreno para evoluções aceleradas no motor de e-mails.

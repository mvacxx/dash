# Marketing Insights Dashboard

Aplicação completa (API + frontend) para consolidar métricas diárias de Facebook Ads e Google AdSense, permitindo calcular ROI por usuário.

## Visão geral

- **Backend** em FastAPI com suporte assíncrono, integração com banco SQLite (pode ser trocado por Postgres) e clientes prontos para chamar as APIs oficiais do Facebook Marketing API e Google AdSense.
- **Frontend** em React + Vite com interface responsiva, formulários de integração e visualização em tempo real das métricas de investimento, receita e ROI.
- Estrutura multiusuário: cada usuário pode conectar suas próprias contas e sincronizar métricas diárias para gerar relatórios.

## Instalação rápida

1. Clone o repositório e acesse a pasta principal:

   ```bash
   git clone <url-do-repositorio>
   cd dash
   ```

2. Configure o backend (ver seção abaixo) e mantenha o servidor FastAPI rodando.

3. Em outro terminal, configure o frontend (ver seção específica) e inicie o servidor de desenvolvimento.

4. Acesse `http://localhost:5173` (porta padrão do Vite) e utilize `http://localhost:8000` como URL da API ao preencher o formulário de login ou cadastro.

> Para implantar em produção, utilize um servidor WSGI/ASGI (como Uvicorn + Gunicorn) para o backend e gere os assets do frontend com `npm run build`, servindo-os com o web server de sua preferência.

## Pré-requisitos

- Python 3.11+
- Node.js 18+

## Configuração do backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Variáveis de ambiente importantes:

- `DATABASE_URL`: string de conexão SQLAlchemy (padrão usa SQLite local `app.db`).
- `FACEBOOK_API_VERSION`: versão da Graph API (padrão `v18.0`).
- `SECRET_KEY`: chave secreta usada para assinar tokens JWT.
- `ACCESS_TOKEN_EXPIRE_MINUTES`: duração (em minutos) dos tokens emitidos.
- `SCHEDULER_DAILY_HOUR_UTC` / `SCHEDULER_DAILY_MINUTE_UTC`: horário em UTC para disparar a sincronização automática diária.

### Autenticação e fluxo de sincronização

1. Crie um usuário `POST /users` com e-mail, nome e senha.
2. Obtenha um token de acesso autenticando-se em `POST /auth/login` (email + senha). O token JWT retornado deve ser enviado no header `Authorization: Bearer <token>`.
3. Cadastre as integrações autenticadas:
   - `POST /integrations/facebook` com `account_id`, `access_token` (e opcional `business_id`).
   - `POST /integrations/adsense` com `account_id`, `access_token`, `refresh_token`, `client_id`, `client_secret` e opcionalmente `expires_in` ou `token_expiry`.
4. Solicite a sincronização diária manual `POST /metrics/sync?date=YYYY-MM-DD`.
5. Consulte os relatórios `GET /metrics?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`.

Os clientes `FacebookAdsClient` e `GoogleAdSenseClient` utilizam as rotas oficiais REST; basta fornecer tokens válidos para receber dados reais.

### Sincronização automática

O backend utiliza APScheduler para executar uma tarefa diária (horário configurável via variáveis de ambiente) que dispara `sync_daily_metrics` para todos os usuários cadastrados.

Tokens do Google AdSense são persistidos com dados completos de OAuth (incluindo `refresh_token`). A cada sincronização, o serviço renova automaticamente o `access_token` quando expirado, garantindo chamadas válidas à API.

## Configuração do frontend

```bash
cd frontend
npm install
npm run dev
```

Defina a variável `VITE_API_URL` para apontar para a URL da API FastAPI (por exemplo `http://localhost:8000`).

A interface permite:

- Autenticar-se com email/senha (ou registrar um novo usuário).
- Conectar credenciais de Facebook Ads e Google AdSense com suporte a renovação automática do token do Google.
- Definir intervalo de datas e visualizar investimento, receita e ROI médio.
- Visualizar gráfico responsivo de ROI diário.

## Estrutura do banco

Tabelas principais:

- `users`: dados básicos e hash de senha.
- `integration_accounts`: credenciais por usuário e tipo (facebook_ads, google_adsense).
- `daily_metrics`: resultados agregados de gasto/receita/ROI por dia e por usuário.

## Próximos passos sugeridos

- Adicionar remoção/edição de integrações via interface.
- Implementar notificações quando sincronizações automáticas falharem.

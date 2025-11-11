# Marketing Insights Dashboard

Aplicação completa (API + frontend) para consolidar métricas diárias de Facebook Ads e Google AdSense, permitindo calcular ROI por usuário.

## Visão geral

- **Backend** em FastAPI com suporte assíncrono, integração com banco SQLite (pode ser trocado por Postgres) e clientes prontos para chamar as APIs oficiais do Facebook Marketing API e Google AdSense.
- **Frontend** em React + Vite com interface responsiva, formulários de integração e visualização em tempo real das métricas de investimento, receita e ROI.
- Estrutura multiusuário: cada usuário pode conectar suas próprias contas e sincronizar métricas diárias para gerar relatórios.

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

### Fluxo de sincronização

1. Crie um usuário `POST /users` com e-mail, nome e senha.
2. Cadastre as integrações:
   - `POST /integrations/facebook/{user_id}` com `account_id`, `access_token` (e opcional `business_id`).
   - `POST /integrations/adsense/{user_id}` com `account_id`, `access_token`, `refresh_token`, `client_id`, `client_secret`.
3. Solicite a sincronização diária `POST /metrics/sync/{user_id}?date=YYYY-MM-DD`.
4. Consulte os relatórios `GET /metrics/{user_id}?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`.

Os clientes `FacebookAdsClient` e `GoogleAdSenseClient` utilizam as rotas oficiais REST; basta fornecer tokens válidos para receber dados reais.

## Configuração do frontend

```bash
cd frontend
npm install
npm run dev
```

Defina a variável `VITE_API_URL` para apontar para a URL da API FastAPI (por exemplo `http://localhost:8000`).

A interface permite:

- Selecionar usuário (ID numérico).
- Conectar credenciais de Facebook Ads e Google AdSense.
- Definir intervalo de datas e visualizar investimento, receita e ROI médio.
- Visualizar gráfico responsivo de ROI diário.

## Estrutura do banco

Tabelas principais:

- `users`: dados básicos e hash de senha.
- `integration_accounts`: credenciais por usuário e tipo (facebook_ads, google_adsense).
- `daily_metrics`: resultados agregados de gasto/receita/ROI por dia e por usuário.

## Próximos passos sugeridos

- Implementar autenticação JWT para proteger as rotas.
- Criar tarefas agendadas (Celery/APS) para sincronização automática diária.
- Persistir tokens do Google usando OAuth completo (renovando access token com `refresh_token`).

# SAC Barcelos – Atendimento via WhatsApp, Telegram e Backoffice

API em FastAPI estruturada em camadas para receber chamados de moradores via WhatsApp/Telegram, atribuir setores pelo backoffice e acompanhar o status das solicitações.

## Arquitetura (melhores práticas adotadas)
- **Estrutura modular**: camadas separadas para configuração, banco, modelos, serviços, repositórios e rotas em `sac_barcelos/`.
- **Banco relacional**: SQLAlchemy com SQLite local por padrão (`data/sac.db`), pronto para apontar para Postgres/RDS via `DATABASE_URL`.
- **Idempotência em webhooks**: chave única por `source + channel_reference` evita duplicar chamados.
- **Attachments service**: salva anexos localmente e envia para S3 opcionalmente; valida erros de upload e mantém metadados.
- **CORS configurável**: origens liberadas via configuração.

## Principais endpoints
- `GET /health`: verificação de saúde.
- `POST /attachments`: envia um ou mais arquivos (multipart/form-data) e retorna os links.
- `POST /tickets`: cria um chamado pelo backoffice.
- `GET /tickets`: lista os chamados.
- `GET /tickets/{id}`: consulta um chamado.
- `PATCH /tickets/{id}/assignment`: atribui um setor ao chamado.
- `PATCH /tickets/{id}/status`: atualiza status (open, in_progress, resolved, closed) e registra metadados.
- `POST /webhooks/whatsapp`: recebe mensagens formatadas do WhatsApp e cria um chamado idempotente.
- `POST /webhooks/telegram`: recebe mensagens formatadas do Telegram e cria um chamado idempotente.

## Executando localmente
1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
2. Inicie a API:
   ```bash
   uvicorn sac_barcelos.main:app --host 0.0.0.0 --port 8000
   ```
3. Acesse a documentação interativa:
   - Swagger: http://localhost:8000/docs  
   - ReDoc: http://localhost:8000/redoc

## Variáveis de ambiente
- `DATABASE_URL`: URL do banco (padrão `sqlite:///./data/sac.db`).
- `ATTACHMENTS_DIR`: diretório local para salvar anexos (padrão `data/attachments`).
- `ATTACHMENTS_BUCKET`: bucket S3 opcional para armazenar anexos.
- `AWS_REGION`: região usada pelo cliente S3 (padrão `us-east-1`).
- `CORS_ALLOW_ORIGINS`: origens permitidas (lista separada por vírgula; padrão `*` via `Settings`).

## Exemplo de payload para webhooks
```json
{
  "chat_id": "5511999999999",
  "citizen_name": "Maria Silva",
  "contact": "+55 11 99999-9999",
  "text": "Iluminação queimada na Praça Central",
  "location": "Praça Central, ao lado da igreja",
  "attachments": [
    {
      "url": "https://example.com/foto.jpg",
      "filename": "foto.jpg"
    }
  ],
  "message_id": "abc-123"
}
```

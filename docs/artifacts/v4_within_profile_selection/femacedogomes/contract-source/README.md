# API de Eventos

Uma API simples para gerenciar eventos, construída com Node.js, Express e MongoDB.

## Instalação

Clone o repositório:

```bash
git clone <seu-repositorio>
cd <seu-repositorio>
```

Instale as dependências:

```bash
yarn install
```

Configure as variáveis de ambiente:

```bash
cp .env.example .env
# Edite o arquivo .env conforme necessário
```

## Executando o Servidor

### Ambiente de Desenvolvimento

```bash
yarn dev
```

### Ambiente de Produção

```bash
yarn start
```

## Estrutura do Projeto

```
src/
 |--config/         # Configurações e variáveis de ambiente
 |--controllers/    # Controladores das rotas
 |--models/         # Modelos do MongoDB (Mongoose)
 |--routes/         # Definição das rotas da API
 |--middlewares/    # Middlewares personalizados
 |--app.js          # Configuração do Express
 |--server.js       # Ponto de entrada da aplicação
```

## Rotas Principais

- **Eventos**:
  - `GET /event` - Lista todos os eventos
  - `POST /event` - Cria um novo evento
  - `GET /event/:id` - Obtém um evento por ID
  - `PUT /event/:id` - Atualiza um evento
  - `DELETE /event/:id` - Remove um evento
  - - `POST invite/:id/event` - Convida uma pessoa para o evento.

## Autenticação

A API usa autenticação via JWT. Para acessar rotas protegidas, é necessário incluir um token válido no cabeçalho `Authorization`.

## Testes

```bash
yarn test
```

## Tecnologias Utilizadas

- Node.js
- Express
- MongoDB + Mongoose
- JWT para autenticação
- Joi para validação de dados
- Winston para logging


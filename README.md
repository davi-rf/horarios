<div align="center">
  <h1>Horários API</h1>

  <img src="https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54">
  <img src="https://img.shields.io/badge/mysql-4479A1.svg?style=for-the-badge&logo=mysql&logoColor=white">
  <img src="https://img.shields.io/badge/sqlalchemy-373f48.svg?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgdmlld0JveD0iMCAwIDMwNCAzMDQiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHJlY3Qgd2lkdGg9IjMwNCIgaGVpZ2h0PSIzMDQiIGZpbGw9IiNGRkZGRkYiLz48L3N2Zz4=">
  <img src="https://img.shields.io/badge/version-2.0.0-blue?style=for-the-badge">
  <img src="https://img.shields.io/badge/license-MIT-green?style=for-the-badge">
</div>

<p align="center">
API em Python (FastAPI) para consulta de horários escolares e turnos de permanência, alimentada por um banco de dados MySQL.
</p>

## Funcionalidades

- **Consultar aulas por turma ou professor**: Permite buscar todas as matérias e ver quem lecionará em cada bloco e para qual turma.
- **Autenticação**: Implementação de cadastro simplificado e login através de tokens **JWT** e senhas com geração de hash pelo **Bcrypt**. Suporte a controle de rotas por perfis de acesso (ex.: administrador e professor).
- **Detecção de Conflitos**: Ao registrar novas aulas, ocorre uma verificação em tempo real para impedir alocação dupla de turma ou professor no mesmo horário.
- **Gerenciamento Completo (CRUD)**: Endpoints com métodos `GET`, `POST`, `PUT` e `DELETE` disponíveis para professores, matérias, cursos e aulas.
- **Alimentação automatizada**: Importação direta de planilhas CSV para as tabelas relacionais do banco através de script auxiliar.

## Estrutura do Projeto

```
horarios/
│
├── .gitignore
│
├── dados/
│   ├── aula_professor.csv
│   ├── aulas.csv
│   ├── cursos.csv
│   ├── materias.csv
│   ├── professor_materia.csv
│   ├── professores.csv
│   ├── restricoes_curso.csv
│   ├── restricoes_professor.csv
│   ├── salas.csv
│   ├── turmas.csv
│   └── usuarios.csv
│
├── data_entry.py
├── database.py
├── main.py
├── models.py
├── README.md
└── requirements.txt
```

### Tecnologias utilizadas:

- Python 3.x
- **FastAPI** (servidor HTTP e roteamento de alta performance)
- **Uvicorn** (servidor ASGI)
- **SQLAlchemy 2.0+** (ORM para acesso a dados - _novo em v2.0.0_)
- **PyMySQL** (driver MySQL compatível com SQLAlchemy - _novo em v2.0.0_)
- **MySQL** (armazenamento com modelagem relacional)
- **PyJWT** (Tokens JWT para autenticação)
- **Bcrypt** (hash de senhas)
- **Pydantic** (validação e serialização JSON)
- **Alembic** (gerenciamento de migrations - _novo em v2.0.0_)

### Arquivos

- **`dados/*.csv`**: Arquivos da base de dados estática inicial para popular rapidamente turmas, disciplinas, aulas e horários.
- **`data_entry.py`**: Script utilitário em Python encarregado de injetar os registros dos arquivos `dados/*.csv` diretamente dentro do servidor MySQL.
- **`database.py`**: Configuração centralizada de conexão com o banco usando SQLAlchemy, com pool de conexões e gerenciamento automático de sessões.
- **`models.py`**: Definição de modelos SQLAlchemy (ORM) para todas as entidades do banco (Usuários, Professores, Matérias, Cursos, Salas, Turmas, Aulas, Restrições).
- **`horarios.sql`**: Script DDL com restrições e relacionamentos. Tabelas: usuários, professores, matérias, cursos, salas, turmas, aulas, restrições de professores e cursos.
- **`main.py`**: Coração da aplicação. Disponibiliza endpoints FastAPI com autenticação (JWT + Bcrypt), CRUD completo e detecção de conflitos de horários (turma, professor, sala e subturmas).
- **`requirements.txt`**: Todas as bibliotecas necessárias (FastAPI, SQLAlchemy, PyMySQL, Pydantic, PyJWT, Bcrypt, Uvicorn, Alembic).
- **`select_all.sql`**: Queries básicas de verificação para auditoria nas tabelas.
- **`SQLALCHEMY_GUIDE.md`**: Guia completo e didático sobre SQLAlchemy com exemplos práticos.
- **`MIGRATION_SUMMARY.md`**: Documentação técnica da migração de mysql-connector para SQLAlchemy.

## Como Executar

1. **Banco de Dados**: Usando uma ferramenta ou pelo servidor local MySQL, aplique o código contido em `backend/horarios.sql` para garantir a criação limpa de todos os esquemas.
2. **Dependências**: Navegue até o diretório do backend e instale os pacotes:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```
3. **Carga Inicial**: Para evitar que o sistema inicie vazio, realize o preenchimento automático das planilhas:
   ```bash
   python data_entry.py
   ```
4. **Executando a API**: Inicialize a aplicação, ela disponibilizará os endpoints na porta padrão localhost:
   ```bash
   python main.py
   ```
5. **Autenticação e Testes da Interface (Swagger)**: Diferente de versões anteriores, atente-se à restrição dos painéis via `@app.post('/login')`. Utilize `http://localhost:8000/docs` para interagir com os testes do FastAPI, registrar seu usuário (`/users`) e inserir credenciais e o token pelo Authorization Header visualmente na tela de documentação via endpoint `Login`.

## Endpoints Principais

### Autenticação

- `POST /login` - Login com email e senha, retorna JWT token
- `POST /users` - Criar novo usuário (requer admin)

### Professores

- `GET /professores` - Listar todos os professores
- `POST /professores` - Criar professor
- `PUT /professores/{id}` - Atualizar professor
- `DELETE /professores/{id}` - Deletar professor

### Matérias

- `GET /materias` - Listar matérias
- `POST /materias` - Criar matéria
- `PUT /materias/{id}` - Atualizar matéria
- `DELETE /materias/{id}` - Deletar matéria

### Cursos

- `GET /cursos` - Listar cursos
- `POST /cursos` - Criar curso
- `PUT /cursos/{id}` - Atualizar curso
- `DELETE /cursos/{id}` - Deletar curso

### Turmas

- `GET /turmas` - Listar turmas
- `POST /turmas` - Criar turma
- `PUT /turmas/{id}` - Atualizar turma
- `DELETE /turmas/{id}` - Deletar turma

### Aulas

- `GET /aulas` - Listar aulas (com filtro opcional por dia)
- `POST /aulas` - Criar aula (com detecção automática de conflitos)
- `PUT /aulas/{id}` - Atualizar aula
- `DELETE /aulas/{id}` - Deletar aula

## Detecção de Conflitos

A API detecta automaticamente **4 tipos de conflitos** ao criar/atualizar aulas:

1. **Conflito de Turma**: Mesma turma não pode ter aulas simultâneas
2. **Conflito de Professor**: Professor não pode ministrar aulas simultâneas
3. **Conflito de Sala**: Sala não pode estar ocupada por outra aula
4. **Conflito de Subturmas**: Aula geral bloqueia subturmas (e vice-versa)

### Lógica de Subturmas

- **Aula Geral** (subturma = NULL) → Bloqueia aulas simultâneas de toda a turma
- **Aula de Subturma** (ex: "A") → Bloqueia apenas aulas gerais da mesma turma
- **Subturmas entre si** → Podem ter aulas simultâneas

## Autenticação e Autorização

```bash
# Login
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "senha123"}'

# Usar token em requisições autenticadas
curl -X GET http://localhost:8000/professores \
  -H "Authorization: Bearer <seu_token_jwt>"
```

## Versão

**v2.0.0** - 2026-04-05

### O que mudou em v2.0.0

✨ **Migração Completa para SQLAlchemy ORM**

- ✅ Substituição de `mysql-connector` por `SQLAlchemy + PyMySQL`
- ✅ Eliminação de SQL bruto (queries mais seguras e legíveis)
- ✅ Modelos ORM centralizados em `models.py`
- ✅ Relacionamentos automáticos entre entidades
- ✅ Pool de conexões gerenciado automaticamente
- ✅ Transações e sessões controladas automaticamente

🔒 **Melhorias de Segurança**

- ✅ Proteção automática contra SQL injection
- ✅ Type hints para melhor validação em IDE

🎯 **Detecção Avançada de Conflitos**

- ✅ Conflito de sala agora detectado
- ✅ Lógica de subturmas implementada
- ✅ Validações em tempo real antes de inserir aulas

📚 **Documentação**

- ✅ Guia completo de SQLAlchemy (`SQLALCHEMY_GUIDE.md`)
- ✅ Sumário técnico da migração (`MIGRATION_SUMMARY.md`)
- ✅ README atualizado com endpoints e funcionalidades

⚙️ **Infraestrutura**

- ✅ Suporte a Alembic para migrations (futuro)
- ✅ Melhor separação de concerns (database.py, models.py)
- ✅ Code mais mantível e testável

## Padrões de Desenvolvimento

### 1. Queries

```python
# ✅ Usar ORM
user = db.query(Usuario).filter(Usuario.email == email).first()

# ❌ Não usar SQL bruto
# cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
```

### 2. Transações

```python
# ✅ Use db.add() e db.commit()
novo_prof = Professor(nome="João")
db.add(novo_prof)
db.commit()

# ❌ Não manage manualmente
# cursor.execute("INSERT INTO...")
```

### 3. Relacionamentos

```python
# ✅ Acesse via relacionamentos
prof = db.query(Professor).filter_by(id=1).first()
aulas = prof.aulas  # Carrega automaticamente

# ❌ Não faça JOIN manualmente
# SELECT * FROM aulas JOIN aula_professor ...
```

## Roadmap Futuro

- [ ] Implementar Alembic para versionamento de schema
- [ ] Adicionar filtros avançados e busca
- [ ] WebSocket para atualizações em tempo real
- [ ] Relatórios em PDF
- [ ] Dashboard frontend (React/Vue)
- [ ] Cache com Redis
- [ ] Testes unitários com pytest
- [ ] CI/CD com GitHub Actions

## Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/sua-feature`)
3. Commit suas mudanças (`git commit -m 'Add: sua feature'`)
4. Push para a branch (`git push origin feature/sua-feature`)
5. Abra um Pull Request

## Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

## Suporte

Para reportar bugs, abra uma issue no repositório.
Para dúvidas técnicas, consulte a documentação em `SQLALCHEMY_GUIDE.md` e `MIGRATION_SUMMARY.md`.


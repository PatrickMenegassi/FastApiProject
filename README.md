# 🏋️ Workout API - FastAPI

Uma API RESTful para gerenciamento de academias e atletas, desenvolvida com FastAPI e PostgreSQL.

## 🚀 Tecnologias

- **FastAPI** - Framework web moderno
- **PostgreSQL** - Banco de dados relacional
- **SQLAlchemy** - ORM para Python
- **Alembic** - Migrations de banco de dados
- **Docker** - Containerização
- **Pydantic** - Validação de dados
- **Uvicorn** - Servidor ASGI

## 📋 Funcionalidades

- ✅ Gerenciamento de Atletas
- ✅ Categorias de treino
- ✅ Centros de treinamento
- ✅ API documentada automaticamente (Swagger/OpenAPI)
- ✅ Migrations automáticas com Alembic
- ✅ Container Docker com PostgreSQL

## 🛠️ Instalação

### Pré-requisitos
- Python 3.11+
- Docker e Docker Compose
- Git

### Configuração

1. **Clone o repositório:**
git clone https://github.com/PatrickMenegassi/FastApiProject.git
cd FastApiProject

2. **Criar e ativar ambiente virtual:**
python -m venv workoutapi
workoutapi\Scripts\activate  # Windows

3. **Instale as dependências**
pip install -r requirements.txt

4. **Suba o banco de dados com docker**
docker-compose up -d

5. **Execute as migrações**
alembic upgrade head

6. **Suba o servidor**
uvicorn workout_api.main:app --reload

7. **Acesse o servidor**
http://localhost:8000/docs

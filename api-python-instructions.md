# 🐍 Instructions Projet — API Python devZair

> Ce document est la **référence centrale de la Phase 2**.
> Il cadre l'architecture, les conventions, les bonnes pratiques et la pédagogie
> pour développer l'API Python FastAPI du portfolio devZair.

---

## 📋 Table des matières

1. [Contexte et objectifs](#1-contexte-et-objectifs)
2. [Plan de développement (Roadmap)](#2-plan-de-développement-roadmap)
3. [Architecture cible](#3-architecture-cible)
4. [Stack technique](#4-stack-technique)
5. [Concepts Python clés à maîtriser](#5-concepts-python-clés-à-maîtriser)
6. [Étape 0 — Environnement Docker](#étape-0--environnement-docker)
7. [Étape 1 — Initialisation du projet Python](#étape-1--initialisation-du-projet-python)
8. [Étape 2 — Configuration et Settings](#étape-2--configuration-et-settings)
9. [Étape 3 — Structure des modules (Architecture)](#étape-3--structure-des-modules-architecture)
10. [Étape 4 — Modèles de données (Pydantic)](#étape-4--modèles-de-données-pydantic)
11. [Étape 5 — Routeurs et Endpoints](#étape-5--routeurs-et-endpoints)
12. [Étape 6 — Sécurité (CORS, Auth, Rate Limiting)](#étape-6--sécurité-cors-auth-rate-limiting)
13. [Étape 7 — Base de données (SQLAlchemy + Alembic)](#étape-7--base-de-données-sqlalchemy--alembic)
14. [Étape 8 — Tests](#étape-8--tests)
15. [Étape 9 — Dockerisation production](#étape-9--dockerisation-production)
16. [Conventions de code Python](#conventions-de-code-python)
17. [Sécurité — Checklist complète](#sécurité--checklist-complète)
18. [Checklist avant chaque session](#checklist-avant-chaque-session)

---

## 1. Contexte et objectifs

### Pourquoi une API Python ?

Le frontend React est un site **statique** : il affiche des données codées en dur dans `src/data/`.
L'API Python va permettre de :

- **Dynamiser le contenu** : gérer les projets, compétences, messages de contact depuis une base de données
- **Créer un espace admin** : ajouter/modifier/supprimer du contenu sans toucher au code
- **Sécuriser les données sensibles** : les clés et tokens ne sont jamais dans le frontend
- **Préparer l'avenir** : envoyer des emails, gérer des fichiers, ajouter de l'IA...

### Pourquoi FastAPI ?

FastAPI est le framework Python le plus moderne pour créer des APIs. Ses avantages :

| Avantage | Détail |
|----------|--------|
| **Rapidité** | Comparable à NodeJS/Go grâce à l'asynchrone natif |
| **Validation automatique** | Les données entrantes sont validées sans écrire de code |
| **Documentation auto** | Swagger UI généré automatiquement à `/docs` |
| **Type hints Python** | Cohérent avec TypeScript — même philosophie |
| **Écosystème moderne** | Pydantic, SQLAlchemy 2, Alembic... |

---

## 2. Plan de développement (Roadmap)

```
✅ Phase 1  — Frontend React (terminé)

🔵 Phase 2  — API Python FastAPI

  ✅ Étape 0  — Environnement Docker (dev + prod)
  ⬜ Étape 1  — Initialisation projet Python (uv, structure)
  ⬜ Étape 2  — Configuration centralisée (Settings, .env)
  ⬜ Étape 3  — Architecture des modules (Router, Service, Repository)
  ⬜ Étape 4  — Modèles de données (Pydantic schemas)
  ⬜ Étape 5  — Premiers endpoints (projets, compétences)
  ⬜ Étape 6  — Sécurité (CORS, rate limiting, JWT)
  ⬜ Étape 7  — Base de données (PostgreSQL, SQLAlchemy, Alembic)
  ⬜ Étape 8  — Endpoint Contact (envoi d'email)
  ⬜ Étape 9  — Tests (pytest)
  ⬜ Étape 10 — Dockerisation production

🔮 Phase 3  — Interface admin (à définir)
```

> ⚠️ **Règle d'or** : on ne passe pas à l'étape suivante tant que la précédente
> n'est pas **comprise** et **validée** (tests qui passent, code committé).

---

## 3. Architecture cible

### Vue globale du dépôt

```
devzair-portfolio/
├── frontend/           ← React (Phase 1 — terminé)
└── api/                ← Python FastAPI (Phase 2 — on commence ici)
    ├── src/
    │   └── app/
    │       ├── __init__.py
    │       ├── main.py             ← Point d'entrée FastAPI
    │       ├── core/               ← Configuration, sécurité, dépendances
    │       │   ├── config.py       ← Settings (variables d'env)
    │       │   ├── security.py     ← JWT, hashing
    │       │   └── dependencies.py ← Injection de dépendances
    │       ├── models/             ← Modèles SQLAlchemy (tables DB)
    │       │   └── project.py
    │       ├── schemas/            ← Modèles Pydantic (validation API)
    │       │   └── project.py
    │       ├── repositories/       ← Accès base de données (requêtes SQL)
    │       │   └── project_repository.py
    │       ├── services/           ← Logique métier
    │       │   └── project_service.py
    │       ├── routers/            ← Routes HTTP (endpoints)
    │       │   ├── projects.py
    │       │   ├── skills.py
    │       │   └── contact.py
    │       └── database/
    │           ├── session.py      ← Connexion DB
    │           └── migrations/     ← Alembic (historique des migrations)
    ├── tests/
    │   ├── conftest.py
    │   ├── test_projects.py
    │   └── test_contact.py
    ├── .env                        ← Variables locales (jamais dans Git !)
    ├── .env.example                ← Template (toujours dans Git)
    ├── .gitignore
    ├── pyproject.toml              ← Config projet + dépendances
    ├── Dockerfile
    ├── docker-compose.yml          ← Dev
    └── docker-compose.prod.yml     ← Production
```

### Le pattern architectural : Router → Service → Repository

C'est le cœur de l'architecture. Chaque couche a **une seule responsabilité** :

```
Requête HTTP
     ↓
  [Router]          ← Reçoit la requête, valide via Pydantic, renvoie la réponse
     ↓
  [Service]         ← Contient la logique métier (règles, transformations)
     ↓
  [Repository]      ← Parle à la base de données (requêtes SQL)
     ↓
  Base de données
```

**Pourquoi cette séparation ?**

- Le Router ne sait pas comment on stocke les données → interchangeable
- Le Service ne sait pas si c'est PostgreSQL ou SQLite → testable facilement
- Le Repository ne connaît pas les règles métier → réutilisable

> 💡 **Analogie** : c'est comme un restaurant.
> Le serveur (Router) prend la commande.
> Le chef (Service) décide comment préparer le plat.
> L'économe (Repository) gère les ingrédients en réserve.

---

## 4. Stack technique

| Rôle | Outil | Pourquoi |
|------|-------|----------|
| Framework web | **FastAPI** | Moderne, rapide, auto-documentation |
| Validation données | **Pydantic v2** | Intégré à FastAPI, très performant |
| ORM (base de données) | **SQLAlchemy 2** | Standard Python, puissant, async |
| Migrations DB | **Alembic** | Versionning du schéma de la DB |
| Base de données | **PostgreSQL** | Robuste, standard production |
| Serveur ASGI | **Uvicorn** | Serveur async pour FastAPI |
| Gestionnaire packages | **uv** | Ultra-rapide, remplace pip/poetry |
| Tests | **pytest + httpx** | Standard Python |
| Auth | **python-jose + passlib** | JWT + hashing sécurisé |
| Email | **fastapi-mail** | Envoi d'emails simple |
| Linter/Formatter | **Ruff** | Remplace flake8 + black + isort |
| Type checker | **mypy** | Vérification statique des types |

---

## 5. Concepts Python clés à maîtriser

Avant de coder, voici les concepts Python que tu vas rencontrer.
Pas besoin de tout maîtriser maintenant — ils seront expliqués à chaque étape.

### Les type hints

Python est dynamiquement typé, mais depuis Python 3.5+, on peut (et doit) annoter les types :

```python
# Sans type hints (déconseillé)
def get_project(project_id):
    return project_id

# Avec type hints (recommandé)
def get_project(project_id: int) -> dict:
    return {"id": project_id}
```

> 💡 C'est l'équivalent de TypeScript pour Python. FastAPI **utilise** ces annotations
> pour valider automatiquement les données. C'est magique.

### L'asynchrone (async/await)

FastAPI est asynchrone. Même syntaxe qu'en JavaScript :

```python
# Synchrone (bloque tout pendant la requête)
def get_projects():
    return db.query(Project).all()

# Asynchrone (libère le thread pendant l'attente)
async def get_projects():
    return await db.execute(select(Project))
```

### Les décorateurs

Les `@` sont des décorateurs — ils "emballent" une fonction pour lui ajouter des comportements :

```python
@app.get("/projects")       # ← Ce décorateur dit à FastAPI :
async def list_projects():  #   "quand GET /projects → appelle cette fonction"
    ...
```

> 💡 Tu as déjà vu ça en React avec les HOC — même idée.

### Les dataclasses et Pydantic

Pydantic permet de définir des structures de données avec validation :

```python
from pydantic import BaseModel

class ProjectSchema(BaseModel):
    title: str
    description: str
    is_active: bool = True  # valeur par défaut

# Si on envoie un JSON avec title = 123 (int), Pydantic le convertit en "123" (str)
# Si on oublie description, Pydantic lève une erreur claire automatiquement
```

---

## Étape 0 — Environnement Docker

### 🎓 Concept : pourquoi Docker pour le dev ?

Même raison que pour le frontend :
- Python installé en local → problèmes de versions entre machines
- Docker → même environnement pour toi, ton collègue, la production
- PostgreSQL dans Docker → pas besoin d'installer Postgres sur ta machine

### Ce qu'on va créer

```
api/
├── Dockerfile                  ← Image Docker de l'API
├── docker-compose.yml          ← Orchestre API + PostgreSQL + pgAdmin
└── docker-compose.prod.yml     ← Production (à venir à l'étape 9)
```

### `api/Dockerfile`

```dockerfile
# On part d'une image Python officielle légère (slim = sans les outils inutiles)
FROM python:3.12-slim

# Empêche Python de créer des fichiers .pyc (bytecode inutile en dev)
ENV PYTHONDONTWRITEBYTECODE=1

# Force Python à afficher les logs immédiatement (pas de buffer)
# → On voit les erreurs en temps réel dans Docker
ENV PYTHONUNBUFFERED=1

# On définit le dossier de travail dans le conteneur
WORKDIR /app

# On installe uv (gestionnaire de paquets ultra-rapide)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# On copie d'abord les fichiers de config (pour profiter du cache Docker)
# Si on ne change que le code source, Docker ne réinstalle pas les dépendances
COPY pyproject.toml uv.lock* ./

# On installe les dépendances dans un virtualenv géré par uv
RUN uv sync --frozen --no-install-project

# On copie le reste du code source
COPY src/ ./src/

# On expose le port sur lequel Uvicorn va écouter
EXPOSE 8000

# Commande de démarrage :
# --reload = hot reload (redémarre automatiquement si le code change)
# --host 0.0.0.0 = accessible depuis l'extérieur du conteneur
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

> 💡 **Pourquoi `app.main:app` ?**
> C'est la notation Python : `module.fichier:variable`
> Ici : le module `app`, fichier `main.py`, variable `app` (l'instance FastAPI)

### `api/docker-compose.yml`

```yaml
services:

  # 🐍 L'API Python
  api:
    build: .
    container_name: devzair-api
    ports:
      - "8000:8000"           # Port local:Port conteneur
    volumes:
      - ./src:/app/src         # Hot reload : les changements de code sont immédiats
    env_file:
      - .env                   # Variables d'environnement depuis le fichier .env
    depends_on:
      db:
        condition: service_healthy  # Attend que la DB soit prête avant de démarrer
    networks:
      - devzair-network

  # 🐘 La base de données PostgreSQL
  db:
    image: postgres:16-alpine   # Version légère de Postgres
    container_name: devzair-db
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: ${DB_NAME}
    ports:
      - "5432:5432"             # Accessible en local pour les outils DB (DBeaver, etc.)
    volumes:
      - postgres_data:/var/lib/postgresql/data  # Les données persistent entre les redémarrages
    healthcheck:
      # Vérifie que Postgres est prêt à accepter des connexions
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER} -d ${DB_NAME}"]
      interval: 5s
      timeout: 5s
      retries: 5
    networks:
      - devzair-network

  # 🖥️ Interface graphique pour la base de données (optionnel mais pratique)
  pgadmin:
    image: dpage/pgadmin4:latest
    container_name: devzair-pgadmin
    environment:
      PGADMIN_DEFAULT_EMAIL: ${PGADMIN_EMAIL}
      PGADMIN_DEFAULT_PASSWORD: ${PGADMIN_PASSWORD}
    ports:
      - "5050:80"               # Interface web accessible sur http://localhost:5050
    depends_on:
      - db
    networks:
      - devzair-network

# Volumes nommés : Docker gère le stockage (données persistent entre `docker compose down`)
volumes:
  postgres_data:

# Réseau interne : les conteneurs se parlent par leur nom de service (ex: "db")
networks:
  devzair-network:
    driver: bridge
```

### `api/.env`

```bash
# Base de données
DB_USER=devzair
DB_PASSWORD=change_me_in_prod
DB_NAME=devzair_db
DB_HOST=db          # ← "db" = nom du service Docker, pas "localhost" !
DB_PORT=5432

# URL complète de connexion (utilisée par SQLAlchemy)
DATABASE_URL=postgresql+asyncpg://devzair:change_me_in_prod@db:5432/devzair_db

# Application
APP_ENV=development
SECRET_KEY=une_cle_secrete_tres_longue_a_changer_absolument
ALLOWED_ORIGINS=http://localhost:5173  # URL du frontend React en dev

# pgAdmin
PGADMIN_EMAIL=admin@devzair.fr
PGADMIN_PASSWORD=admin
```

### `api/.env.example`

```bash
# Copier ce fichier en .env et remplir les valeurs
# NE JAMAIS committer le fichier .env

DB_USER=
DB_PASSWORD=
DB_NAME=
DB_HOST=db
DB_PORT=5432
DATABASE_URL=postgresql+asyncpg://USER:PASSWORD@db:5432/DB_NAME

APP_ENV=development
SECRET_KEY=
ALLOWED_ORIGINS=http://localhost:5173

PGADMIN_EMAIL=
PGADMIN_PASSWORD=
```

### `api/.gitignore`

```gitignore
# Variables d'environnement (JAMAIS dans Git)
.env
.env.local
.env.*.local

# Python
__pycache__/
*.py[cod]
*.egg-info/
.eggs/
dist/
build/
.venv/
venv/

# uv
.uv/
uv.lock       # À débattre : certains équipes le committent pour reproduire l'env exact

# Tests
.pytest_cache/
.coverage
htmlcov/

# Mypy
.mypy_cache/

# IDE
.vscode/
.idea/
```

### ✅ Vérification Étape 0

```bash
cd api
docker compose up -d

# Vérifier que les 3 services sont démarrés
docker compose ps

# Voir les logs de l'API (elle va crasher car main.py n'existe pas encore — c'est normal)
docker compose logs api

# pgAdmin accessible sur http://localhost:5050
# Se connecter avec les credentials du .env
```

### 📚 Ce qu'on a appris

- Docker Compose orchestre plusieurs conteneurs qui se parlent via un réseau interne
- `depends_on` + `healthcheck` garantit que l'API ne démarre qu'une fois la DB prête
- Les variables d'environnement dans `.env` ne doivent **jamais** être committées
- `DB_HOST=db` : dans Docker, on accède à un service par son **nom**, pas `localhost`

---

## Étape 1 — Initialisation du projet Python

### 🎓 Concept : `uv` et `pyproject.toml`

**`uv`** est le nouveau standard pour gérer les projets Python (comme `pnpm` pour Node).
Il remplace `pip`, `virtualenv`, `poetry` et `pip-tools` — tout en un, et 10x plus rapide.

**`pyproject.toml`** est le fichier de configuration central du projet Python (comme `package.json`).
Il déclare les dépendances, la version Python, les outils de qualité de code...

### Commandes d'initialisation

```bash
cd api

# Initialise un nouveau projet uv
# Crée pyproject.toml, .python-version, src/app/__init__.py
uv init --package --app

# Ajoute les dépendances principales
uv add fastapi[standard] sqlalchemy[asyncio] asyncpg pydantic-settings alembic

# Dépendances de sécurité
uv add python-jose[cryptography] passlib[bcrypt] python-multipart

# Dépendances email
uv add fastapi-mail

# Dépendances de développement (--dev = pas installées en production)
uv add --dev pytest pytest-asyncio httpx ruff mypy
```

### `api/pyproject.toml` résultant

```toml
[project]
name = "devzair-api"
version = "0.1.0"
description = "API portfolio devZair"
requires-python = ">=3.12"

dependencies = [
    "fastapi[standard]>=0.115.0",
    "sqlalchemy[asyncio]>=2.0.0",
    "asyncpg>=0.30.0",
    "pydantic-settings>=2.0.0",
    "alembic>=1.13.0",
    "python-jose[cryptography]>=3.3.0",
    "passlib[bcrypt]>=1.7.4",
    "python-multipart>=0.0.9",
    "fastapi-mail>=1.4.0",
]

[dependency-groups]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "httpx>=0.27.0",
    "ruff>=0.6.0",
    "mypy>=1.11.0",
]

[tool.ruff]
# Ruff remplace flake8 + black + isort en un seul outil ultra-rapide
line-length = 88
target-version = "py312"

[tool.ruff.lint]
# E = pycodestyle errors, F = Pyflakes, I = isort (tri des imports), N = naming conventions
select = ["E", "F", "I", "N", "UP"]
ignore = ["E501"]  # On gère la longueur de ligne via le formateur

[tool.ruff.format]
# Style Black (le standard Python)
quote-style = "double"

[tool.mypy]
python_version = "3.12"
strict = true
ignore_missing_imports = true

[tool.pytest.ini_options]
asyncio_mode = "auto"           # Tous les tests async sans décorateur spécifique
testpaths = ["tests"]
```

### `api/src/app/main.py` — Premier fichier

```python
"""
Point d'entrée de l'application FastAPI devZair.

Ce fichier crée l'instance principale de l'application et configure :
- Les métadonnées (titre, version, description)
- Les middlewares (CORS, etc.)
- Les routeurs (les différents groupes d'endpoints)
"""

from fastapi import FastAPI

# On importe nos settings (configurés à l'étape 2)
# from app.core.config import settings

# Création de l'application FastAPI
# Ces paramètres alimentent la documentation automatique disponible sur /docs
app = FastAPI(
    title="devZair API",
    description="API du portfolio de devZair",
    version="0.1.0",
    # En production, on désactivera la doc publique :
    # docs_url=None, redoc_url=None
)


# Route de santé : permet de vérifier que l'API est vivante
# Utilisée par Docker, les load balancers, les outils de monitoring
@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    """Vérifie que l'API est opérationnelle."""
    return {"status": "ok", "service": "devzair-api"}
```

### ✅ Vérification Étape 1

```bash
# Reconstruire l'image Docker avec les nouvelles dépendances
docker compose build api

# Démarrer
docker compose up -d

# L'API doit démarrer sans erreur
docker compose logs api

# Tester la route de santé
curl http://localhost:8000/health
# Réponse attendue : {"status":"ok","service":"devzair-api"}

# Documentation Swagger automatique
# Ouvrir http://localhost:8000/docs dans le navigateur
```

### 📚 Ce qu'on a appris

- `uv` gère les dépendances Python comme `pnpm` gère les packages Node
- `pyproject.toml` centralise toute la configuration du projet
- FastAPI crée une documentation Swagger automatiquement — c'est **gratuit**
- La route `/health` est une convention universelle pour surveiller les APIs

---

## Étape 2 — Configuration et Settings

### 🎓 Concept : la configuration centralisée

En React, les variables d'environnement viennent de `import.meta.env.VITE_*`.
En Python/FastAPI, on utilise **Pydantic Settings** : une classe qui lit les variables
d'environnement et les valide avec des types.

**Avantages** :
- Toute la config est dans **un seul fichier** — on sait où chercher
- Les types sont vérifiés au démarrage — l'app plante tôt si une var est manquante
- L'IDE comprend les types → autocomplétion

### `api/src/app/core/config.py`

```python
"""
Configuration centralisée de l'application.

Pydantic Settings lit automatiquement les variables depuis :
1. Le fichier .env
2. Les variables d'environnement système

L'ordre de priorité : variables système > .env
"""

from functools import lru_cache  # Pour mettre en cache l'instance (ne lire .env qu'une fois)

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Toutes les variables de configuration de l'application.

    Pydantic valide les types au démarrage.
    Si DATABASE_URL est absent du .env → erreur claire, pas un bug mystérieux.
    """

    # --- Application ---
    app_env: str = "development"          # "development" | "production" | "test"
    app_name: str = "devZair API"
    app_version: str = "0.1.0"
    debug: bool = False                   # True en dev, False en prod

    # --- Base de données ---
    database_url: str                     # Requis : pas de valeur par défaut

    # --- Sécurité ---
    secret_key: str                       # Requis : clé pour signer les JWT
    algorithm: str = "HS256"             # Algorithme de signature JWT
    access_token_expire_minutes: int = 30

    # --- CORS (Cross-Origin Resource Sharing) ---
    # Quelles origines peuvent appeler l'API ?
    # En dev : http://localhost:5173 (le frontend Vite)
    # En prod : https://devzair.fr
    allowed_origins: list[str] = ["http://localhost:5173"]

    # --- Email ---
    mail_username: str = ""
    mail_password: str = ""
    mail_from: str = ""
    mail_port: int = 587
    mail_server: str = ""
    mail_starttls: bool = True
    mail_ssl_tls: bool = False

    # Indique à Pydantic Settings où trouver le fichier .env
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,  # DATABASE_URL == database_url
    )

    @property
    def is_production(self) -> bool:
        """Raccourci pour vérifier si on est en production."""
        return self.app_env == "production"


# lru_cache = on ne crée qu'une seule instance de Settings (Singleton)
# Lire les fichiers disque à chaque requête serait inutilement lent
@lru_cache
def get_settings() -> Settings:
    """Retourne l'instance unique des settings."""
    return Settings()


# Instance globale pour un accès direct dans le code
settings = get_settings()
```

### Utilisation dans `main.py` (mise à jour)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    # En production : désactiver la doc publique
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
)

# Middleware CORS : autorise le frontend à appeler l'API
# Sans ça, le navigateur bloque les requêtes cross-origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,  # Origines autorisées (depuis .env)
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}
```

### ✅ Vérification Étape 2

```bash
# Vérifier que l'app démarre sans erreur avec les nouvelles settings
docker compose restart api
docker compose logs api

# Si une variable requise manque dans .env, FastAPI affiche une erreur claire :
# ValidationError: 1 validation error for Settings
#   database_url → Field required
```

### 📚 Ce qu'on a appris

- `BaseSettings` de Pydantic lit et **valide** les variables d'environnement
- `lru_cache` évite de relire le `.env` à chaque requête
- Le middleware CORS est **obligatoire** pour que le frontend puisse appeler l'API
- La doc Swagger est désactivée en production pour des raisons de sécurité

---

## Étape 3 — Structure des modules (Architecture)

### 🎓 Concept : séparation des responsabilités

Voici le flux complet d'une requête GET `/api/v1/projects` :

```
1. Client (React) → GET /api/v1/projects

2. [Router] projects.py
   - Reçoit la requête HTTP
   - Valide les paramètres (query params, path params)
   - Appelle le service
   - Retourne la réponse sérialisée en JSON

3. [Service] project_service.py
   - Contient la logique métier
   - Ex: "Ne retourner que les projets actifs, triés par date"
   - Appelle le repository pour les données

4. [Repository] project_repository.py
   - Fait la requête SQL à la base de données
   - Retourne les objets SQLAlchemy bruts

5. Base de données → Résultat → remonte la chaîne → JSON → Client
```

### Pourquoi ne pas tout mettre dans le Router ?

```python
# ❌ Mauvais : tout dans le router
@router.get("/projects")
async def get_projects(db: AsyncSession = Depends(get_db)):
    # Logique métier mélangée avec l'accès DB et la réponse HTTP
    result = await db.execute(
        select(Project).where(Project.is_active == True).order_by(Project.created_at.desc())
    )
    projects = result.scalars().all()
    return projects

# Si demain on veut réutiliser cette logique ailleurs → copier-coller → bug
# Si on veut tester sans base de données → impossible facilement
# Si la logique devient complexe → le fichier devient ingérable
```

```python
# ✅ Bon : séparation claire
# router → service → repository
# Chaque fichier fait une seule chose → testable, réutilisable, lisible
```

### Exemple complet : module Projects

#### `api/src/app/schemas/project.py` (Pydantic — validation)

```python
"""
Schémas Pydantic pour les projets.

On distingue plusieurs schémas selon le contexte :
- ProjectBase : champs communs
- ProjectCreate : données attendues pour créer un projet (POST)
- ProjectUpdate : données pour modifier un projet (PATCH — tous les champs optionnels)
- ProjectResponse : données renvoyées par l'API (GET)

Cette distinction permet de contrôler précisément ce qu'on accepte et ce qu'on renvoie.
"""

from datetime import datetime

from pydantic import BaseModel, HttpUrl


class ProjectBase(BaseModel):
    """Champs communs à tous les schémas Project."""
    title: str
    description: str
    stack: list[str]                        # ["React", "TypeScript", "FastAPI"]
    github_url: HttpUrl | None = None       # Pydantic valide que c'est bien une URL
    live_url: HttpUrl | None = None
    is_active: bool = True


class ProjectCreate(ProjectBase):
    """Données attendues lors de la création d'un projet (POST /projects)."""
    # Hérite de ProjectBase — tous les champs sont requis sauf ceux avec des defaults
    pass


class ProjectUpdate(BaseModel):
    """
    Données pour la mise à jour partielle (PATCH /projects/{id}).

    Tous les champs sont optionnels : on ne met à jour que ce qu'on envoie.
    """
    title: str | None = None
    description: str | None = None
    stack: list[str] | None = None
    github_url: HttpUrl | None = None
    live_url: HttpUrl | None = None
    is_active: bool | None = None


class ProjectResponse(ProjectBase):
    """
    Données renvoyées par l'API (ce que le client voit).

    On ajoute les champs générés par la base de données.
    """
    id: int
    created_at: datetime
    updated_at: datetime

    # Permet à Pydantic de lire les attributs d'un objet SQLAlchemy
    # (par défaut, Pydantic n'accepte que les dicts)
    model_config = {"from_attributes": True}
```

#### `api/src/app/repositories/project_repository.py`

```python
"""
Repository Projects — accès base de données.

Ce module est le seul à connaître SQLAlchemy.
Il ne contient aucune logique métier — seulement des opérations CRUD.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectRepository:
    """Encapsule toutes les opérations DB sur la table projects."""

    def __init__(self, session: AsyncSession) -> None:
        # On injecte la session — le Repository ne la crée pas lui-même
        # Cela permet de tester avec une session de test
        self.session = session

    async def get_all(self, *, active_only: bool = False) -> list[Project]:
        """Récupère tous les projets, avec filtre optionnel sur le statut."""
        query = select(Project)

        if active_only:
            query = query.where(Project.is_active == True)  # noqa: E712

        query = query.order_by(Project.created_at.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, project_id: int) -> Project | None:
        """Récupère un projet par son ID. Retourne None si inexistant."""
        result = await self.session.execute(
            select(Project).where(Project.id == project_id)
        )
        return result.scalar_one_or_none()

    async def create(self, data: ProjectCreate) -> Project:
        """Crée un nouveau projet en base de données."""
        # model_dump() convertit le schéma Pydantic en dictionnaire Python
        project = Project(**data.model_dump())
        self.session.add(project)
        await self.session.commit()
        await self.session.refresh(project)  # Recharge depuis la DB (pour récupérer l'id, etc.)
        return project

    async def update(self, project: Project, data: ProjectUpdate) -> Project:
        """Met à jour un projet existant (mise à jour partielle)."""
        # exclude_unset=True : ne met à jour que les champs explicitement envoyés
        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(project, field, value)

        await self.session.commit()
        await self.session.refresh(project)
        return project

    async def delete(self, project: Project) -> None:
        """Supprime un projet."""
        await self.session.delete(project)
        await self.session.commit()
```

#### `api/src/app/services/project_service.py`

```python
"""
Service Projects — logique métier.

Ce module contient les règles métier.
Il ne sait pas si la DB est PostgreSQL ou SQLite — il appelle le repository.
Il ne sait pas que c'est une API HTTP — le router s'en charge.
"""

from fastapi import HTTPException, status

from app.repositories.project_repository import ProjectRepository
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate


class ProjectService:
    """Orchestre la logique métier liée aux projets."""

    def __init__(self, repository: ProjectRepository) -> None:
        self.repository = repository

    async def get_all_projects(self, *, active_only: bool = True) -> list[ProjectResponse]:
        """
        Retourne la liste des projets.
        Par défaut, ne retourne que les projets actifs (logique métier).
        """
        projects = await self.repository.get_all(active_only=active_only)
        return [ProjectResponse.model_validate(p) for p in projects]

    async def get_project(self, project_id: int) -> ProjectResponse:
        """
        Retourne un projet par son ID.
        Lève une erreur 404 si le projet n'existe pas.
        """
        project = await self.repository.get_by_id(project_id)

        if not project:
            # HTTPException est la façon standard de retourner des erreurs HTTP en FastAPI
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Projet {project_id} introuvable",
            )

        return ProjectResponse.model_validate(project)

    async def create_project(self, data: ProjectCreate) -> ProjectResponse:
        """Crée un nouveau projet."""
        project = await self.repository.create(data)
        return ProjectResponse.model_validate(project)

    async def update_project(self, project_id: int, data: ProjectUpdate) -> ProjectResponse:
        """Met à jour un projet existant."""
        project = await self.repository.get_by_id(project_id)

        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Projet {project_id} introuvable",
            )

        updated = await self.repository.update(project, data)
        return ProjectResponse.model_validate(updated)

    async def delete_project(self, project_id: int) -> None:
        """Supprime un projet."""
        project = await self.repository.get_by_id(project_id)

        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Projet {project_id} introuvable",
            )

        await self.repository.delete(project)
```

#### `api/src/app/routers/projects.py`

```python
"""
Router Projects — endpoints HTTP.

Ce module définit les routes de l'API pour les projets.
Il valide les entrées (via Pydantic), appelle le service, retourne les réponses.
Il ne contient aucune logique métier ni accès DB direct.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.repositories.project_repository import ProjectRepository
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.services.project_service import ProjectService

# APIRouter = un groupe de routes avec un préfixe commun
# On peut lui associer des tags pour la documentation Swagger
router = APIRouter(prefix="/projects", tags=["projects"])


def get_project_service(db: AsyncSession = Depends(get_db)) -> ProjectService:
    """
    Factory pour créer le service avec ses dépendances.

    Depends() = injection de dépendances de FastAPI.
    FastAPI va appeler get_db() automatiquement et passer le résultat au service.
    C'est l'équivalent de l'injection de dépendances dans les frameworks comme Spring.
    """
    repository = ProjectRepository(session=db)
    return ProjectService(repository=repository)


@router.get(
    "/",
    response_model=list[ProjectResponse],  # Pydantic serialise automatiquement la réponse
    summary="Liste des projets",
)
async def list_projects(
    active_only: bool = True,                              # Query param: /projects?active_only=false
    service: ProjectService = Depends(get_project_service),
) -> list[ProjectResponse]:
    """Retourne la liste des projets du portfolio."""
    return await service.get_all_projects(active_only=active_only)


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Détail d'un projet",
)
async def get_project(
    project_id: int,                                       # Path param: /projects/42
    service: ProjectService = Depends(get_project_service),
) -> ProjectResponse:
    """Retourne les détails d'un projet spécifique."""
    return await service.get_project(project_id)


@router.post(
    "/",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,    # 201 Created (pas 200 OK pour une création)
    summary="Créer un projet",
)
async def create_project(
    data: ProjectCreate,                                   # Corps de la requête (JSON)
    service: ProjectService = Depends(get_project_service),
) -> ProjectResponse:
    """Crée un nouveau projet. Nécessite une authentification admin."""
    return await service.create_project(data)


@router.patch(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Mettre à jour un projet",
)
async def update_project(
    project_id: int,
    data: ProjectUpdate,
    service: ProjectService = Depends(get_project_service),
) -> ProjectResponse:
    """Met à jour partiellement un projet."""
    return await service.update_project(project_id, data)


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,  # 204 No Content : succès sans corps de réponse
    summary="Supprimer un projet",
)
async def delete_project(
    project_id: int,
    service: ProjectService = Depends(get_project_service),
) -> None:
    """Supprime un projet."""
    await service.delete_project(project_id)
```

---

## Étape 4 — Modèles de données (Pydantic)

> ✅ Déjà couvert en détail dans les schémas de l'Étape 3.
> Cette étape s'attardera sur les **modèles SQLAlchemy** (tables en base de données).

### 🎓 Concept : deux types de modèles

| | Pydantic Schema | SQLAlchemy Model |
|---|---|---|
| **Rôle** | Validation des données API | Représentation d'une table DB |
| **Utilisé par** | Router (entrée/sortie JSON) | Repository (lecture/écriture DB) |
| **Fichier** | `schemas/` | `models/` |

### `api/src/app/models/base.py`

```python
"""
Classe de base pour tous les modèles SQLAlchemy.

En regroupant les colonnes communes ici, on respecte le principe DRY :
id, created_at, updated_at sont présents sur toutes les tables.
"""

from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base déclarative SQLAlchemy 2.0."""
    pass


class TimestampMixin:
    """
    Mixin : un mixin est une classe qu'on "mélange" à d'autres pour partager du comportement.

    Ici, on ajoute automatiquement created_at et updated_at à tout modèle qui hérite de ce mixin.
    """
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),  # La DB génère la valeur (pas Python)
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),         # Mis à jour automatiquement à chaque modification
        nullable=False,
    )
```

### `api/src/app/models/project.py`

```python
"""
Modèle SQLAlchemy pour la table 'projects'.

Mapped et mapped_column sont la syntaxe moderne de SQLAlchemy 2.0.
Ils utilisent les type hints Python pour définir le schéma de la table.
"""

from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Project(Base, TimestampMixin):
    """
    Représente la table 'projects' en base de données.

    __tablename__ définit le nom de la table SQL.
    Chaque attribut Mapped correspond à une colonne.
    """

    __tablename__ = "projects"

    # Mapped[int] + primary_key=True → colonne id INTEGER PRIMARY KEY AUTOINCREMENT
    id: Mapped[int] = mapped_column(primary_key=True)

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # ARRAY(String) est spécifique à PostgreSQL — tableau de chaînes de caractères
    stack: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False, default=list)

    github_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    live_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # is_active permet de "cacher" un projet sans le supprimer (soft visibility)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)

    def __repr__(self) -> str:
        """Représentation lisible de l'objet en debug."""
        return f"<Project id={self.id} title={self.title!r}>"
```

---

## Étape 5 — Routeurs et Endpoints

> ✅ Les routeurs ont été introduits à l'Étape 3 avec l'exemple Projects.

### Enregistrer les routeurs dans `main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import contact, projects, skills  # On importe tous les routeurs

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)

# Préfixe /api/v1 : convention pour versionner l'API
# Si on casse la compatibilité un jour → /api/v2 sans toucher /api/v1
API_PREFIX = "/api/v1"

app.include_router(projects.router, prefix=API_PREFIX)
app.include_router(skills.router, prefix=API_PREFIX)
app.include_router(contact.router, prefix=API_PREFIX)


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}
```

### Convention des endpoints REST

| Méthode | URL | Action | Code succès |
|---------|-----|--------|-------------|
| GET | `/api/v1/projects` | Liste tous les projets | 200 |
| GET | `/api/v1/projects/{id}` | Détail d'un projet | 200 |
| POST | `/api/v1/projects` | Crée un projet | 201 |
| PATCH | `/api/v1/projects/{id}` | Met à jour partiellement | 200 |
| DELETE | `/api/v1/projects/{id}` | Supprime un projet | 204 |

---

## Étape 6 — Sécurité (CORS, Auth, Rate Limiting)

### 🎓 Concept : JWT (JSON Web Tokens)

Le JWT est le mécanisme d'authentification standard pour les APIs REST.

```
1. Admin POST /api/v1/auth/login avec {username, password}
2. L'API vérifie le mot de passe (haché en DB)
3. Si OK → génère un token JWT signé avec la SECRET_KEY
4. Le frontend stocke ce token (localStorage ou cookie httpOnly)
5. Pour chaque requête protégée → envoie le token dans le header :
   Authorization: Bearer eyJhbGc...
6. L'API vérifie la signature → si valide → accès accordé
```

### `api/src/app/core/security.py`

```python
"""
Utilitaires de sécurité : hashing des mots de passe + génération/vérification des JWT.
"""

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# Contexte de hashing : bcrypt est l'algorithme recommandé pour les mots de passe
# Il est intentionnellement lent pour résister aux attaques par force brute
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash un mot de passe en clair.
    Le hash est différent à chaque appel (salt aléatoire intégré).
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Vérifie qu'un mot de passe en clair correspond à son hash.
    On ne peut pas "décrypter" le hash — on rehash et on compare.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Génère un JWT signé avec la SECRET_KEY.

    Le token contient un "payload" (données non-chiffrées mais signées) :
    - sub : l'identifiant du sujet (ex: username)
    - exp : date d'expiration

    Quiconque intercepte ce token peut lire le payload,
    mais ne peut pas le modifier sans invalider la signature.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode["exp"] = expire

    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> dict:
    """
    Décode et vérifie un JWT.
    Lève JWTError si le token est invalide ou expiré.
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError as e:
        raise ValueError("Token invalide ou expiré") from e
```

### `api/src/app/core/dependencies.py`

```python
"""
Dépendances FastAPI réutilisables (injectées avec Depends()).

Ce fichier centralise les dépendances communes :
- Session de base de données
- Utilisateur courant (authentification)
"""

from collections.abc import AsyncGenerator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.database.session import async_session_factory

# Schéma d'authentification : lit le token depuis le header Authorization: Bearer <token>
bearer_scheme = HTTPBearer()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dépendance qui fournit une session de base de données.

    Utilise un générateur async (yield) :
    - FastAPI appelle get_db() → exécute jusqu'au yield → injecte la session
    - Quand la requête est terminée → reprend après le yield → ferme la session
    C'est une garantie que la session est toujours fermée, même en cas d'erreur.
    """
    async with async_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()  # Annule les changements en cas d'erreur
            raise
        finally:
            await session.close()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    """
    Dépendance d'authentification.

    Injecter cette dépendance dans un endpoint le rend protégé :
    @router.post("/", dependencies=[Depends(get_current_user)])

    Si le token est absent ou invalide → 401 Unauthorized automatiquement.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentification requise",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(credentials.credentials)
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
    except ValueError:
        raise credentials_exception

    return {"username": username}
```

### Protection d'un endpoint

```python
# Sans protection (public)
@router.get("/projects")
async def list_projects(...):
    ...

# Avec protection (admin requis)
@router.post("/projects", dependencies=[Depends(get_current_user)])
async def create_project(...):
    ...
```

### Rate Limiting (limitation des requêtes)

Pour protéger l'API contre les abus (spam, brute force) :

```bash
# Ajouter slowapi
uv add slowapi
```

```python
# Dans main.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Dans un routeur (ex: endpoint de contact — cible des spammers)
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/contact")
@limiter.limit("5/minute")   # Max 5 requêtes par minute par IP
async def send_contact(request: Request, ...):
    ...
```

---

## Étape 7 — Base de données (SQLAlchemy + Alembic)

### 🎓 Concept : migrations de base de données

Une migration = un fichier qui décrit une **modification du schéma** de la DB.

Exemple :
- Version 1 : table `projects` avec 5 colonnes
- Version 2 : ajout d'une colonne `thumbnail_url`
- Version 3 : renommage de `description` en `summary`

Alembic garde l'**historique** de ces changements.
Sur un nouveau serveur, il suffit de jouer toutes les migrations dans l'ordre
pour retrouver le schéma exact.

> 💡 C'est l'équivalent de Git pour le schéma de ta base de données.

### `api/src/app/database/session.py`

```python
"""
Configuration de la connexion à la base de données.
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

# Le moteur est la connexion à la DB
# echo=True en dev → affiche toutes les requêtes SQL dans les logs (pratique pour déboguer)
engine = create_async_engine(
    settings.database_url,
    echo=settings.app_env == "development",
    pool_size=5,           # Nombre de connexions maintenues en permanence
    max_overflow=10,       # Connexions supplémentaires si nécessaire
)

# Factory de sessions : chaque requête HTTP obtient sa propre session
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Les objets restent accessibles après commit
)
```

### Initialiser Alembic

```bash
# Dans le conteneur Docker
docker compose exec api uv run alembic init src/app/database/migrations

# Configurer alembic.ini pour utiliser nos settings
# (modifier la ligne sqlalchemy.url)
```

### `alembic.ini` (modifier)

```ini
# Laisser vide : on configure l'URL dynamiquement depuis les settings Python
sqlalchemy.url =
```

### `src/app/database/migrations/env.py` (modifier)

```python
"""Configuration Alembic — lit la config Python pour l'URL de connexion."""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# On importe nos modèles pour qu'Alembic détecte les changements
from app.core.config import settings
from app.models.base import Base
from app.models.project import Project  # noqa: F401 — import nécessaire pour la détection

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# L'URL vient de nos settings (pas de alembic.ini)
config.set_main_option("sqlalchemy.url", settings.database_url.replace("+asyncpg", ""))

target_metadata = Base.metadata  # Permet à Alembic de détecter les changements de modèles
```

### Workflow Alembic

```bash
# Créer une migration automatiquement (Alembic compare les modèles avec la DB)
docker compose exec api uv run alembic revision --autogenerate -m "create projects table"

# Appliquer les migrations en attente
docker compose exec api uv run alembic upgrade head

# Voir l'historique des migrations
docker compose exec api uv run alembic history

# Revenir en arrière d'une migration
docker compose exec api uv run alembic downgrade -1
```

---

## Étape 8 — Tests

### 🎓 Concept : pourquoi tester une API ?

Les tests permettent de :
- S'assurer qu'un endpoint renvoie bien un 404 quand un projet n'existe pas
- Détecter les régressions : un changement qui casse quelque chose d'existant
- Documenter le comportement attendu (les tests sont une forme de documentation)

### `api/tests/conftest.py`

```python
"""
Configuration globale des tests pytest.

conftest.py est automatiquement chargé par pytest.
Les fixtures définies ici sont disponibles dans tous les tests.
"""

import asyncio
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database.session import async_session_factory
from app.main import app
from app.models.base import Base

# Base de données en mémoire pour les tests (plus rapide, isolée)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="session")
async def test_db_engine():
    """Crée le moteur de base de données de test."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Fournit une session de test avec rollback automatique après chaque test."""
    session_factory = async_sessionmaker(test_db_engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session
        await session.rollback()  # Annule les changements → tests isolés


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Client HTTP de test."""
    # Remplace la vraie DB par la DB de test
    app.dependency_overrides[async_session_factory] = lambda: db_session

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
```

### `api/tests/test_projects.py`

```python
"""Tests des endpoints /api/v1/projects."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_projects_empty(client: AsyncClient) -> None:
    """Liste vide au départ."""
    response = await client.get("/api/v1/projects/")

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_create_and_get_project(client: AsyncClient) -> None:
    """Créer un projet puis le récupérer."""
    project_data = {
        "title": "Nidemiel",
        "description": "Site e-commerce de vente de miel",
        "stack": ["React", "FastAPI"],
        "is_active": True,
    }

    # Création
    create_response = await client.post("/api/v1/projects/", json=project_data)
    assert create_response.status_code == 201

    created = create_response.json()
    assert created["title"] == "Nidemiel"
    assert "id" in created

    # Récupération
    get_response = await client.get(f"/api/v1/projects/{created['id']}")
    assert get_response.status_code == 200
    assert get_response.json()["title"] == "Nidemiel"


@pytest.mark.asyncio
async def test_get_nonexistent_project(client: AsyncClient) -> None:
    """Un projet inexistant retourne 404."""
    response = await client.get("/api/v1/projects/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_project_partial(client: AsyncClient) -> None:
    """Mise à jour partielle d'un projet."""
    # Créer d'abord
    create = await client.post(
        "/api/v1/projects/",
        json={"title": "Test", "description": "Description", "stack": ["Python"]},
    )
    project_id = create.json()["id"]

    # Mettre à jour seulement le titre
    update = await client.patch(
        f"/api/v1/projects/{project_id}",
        json={"title": "Nouveau titre"},
    )
    assert update.status_code == 200
    assert update.json()["title"] == "Nouveau titre"
    assert update.json()["description"] == "Description"  # Inchangé
```

### Lancer les tests

```bash
# Dans le conteneur
docker compose exec api uv run pytest

# Avec couverture de code
docker compose exec api uv run pytest --cov=app --cov-report=term-missing

# Un test spécifique
docker compose exec api uv run pytest tests/test_projects.py::test_create_and_get_project -v
```

---

## Étape 9 — Dockerisation production

### `api/Dockerfile` (production)

```dockerfile
# Étape 1 : Build (contient tous les outils de compilation)
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock* ./

# --no-dev : pas les dépendances de développement en production
RUN uv sync --frozen --no-dev --no-install-project

COPY src/ ./src/

# Étape 2 : Image finale (légère, sans les outils de compilation)
FROM python:3.12-slim AS production

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# On copie seulement le virtualenv et le code depuis le builder
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src

# On utilise le Python du virtualenv directement
ENV PATH="/app/.venv/bin:$PATH"

# Utilisateur non-root (bonne pratique sécurité : l'app ne tourne pas en root)
RUN adduser --disabled-password --gecos "" appuser
USER appuser

EXPOSE 8000

# Pas de --reload en production (performance + sécurité)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
```

### `api/docker-compose.prod.yml`

```yaml
services:
  api:
    build:
      context: .
      target: production          # Utilise l'étape "production" du Dockerfile multi-stage
    container_name: devzair-api-prod
    restart: unless-stopped      # Redémarre automatiquement si l'API plante
    env_file:
      - .env.prod                 # Variables de production (jamais dans Git)
    networks:
      - devzair-network
    # Pas de ports exposés directement : Caddy fait le proxy

  db:
    image: postgres:16-alpine
    container_name: devzair-db-prod
    restart: unless-stopped
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: ${DB_NAME}
    volumes:
      - postgres_data_prod:/var/lib/postgresql/data
    networks:
      - devzair-network

volumes:
  postgres_data_prod:

networks:
  devzair-network:
    external: true  # Partagé avec le réseau Caddy du frontend
```

---

## Conventions de code Python

### Nommage

| Élément | Convention | Exemple |
|---------|------------|---------|
| Module/fichier | snake_case | `project_service.py` |
| Classe | PascalCase | `ProjectService` |
| Fonction/méthode | snake_case | `get_all_projects()` |
| Variable | snake_case | `is_active`, `project_id` |
| Constante | UPPER_SNAKE_CASE | `MAX_PROJECTS` |
| Type alias | PascalCase | `ProjectList = list[ProjectResponse]` |

### Structure d'un module

```python
"""Docstring du module — une phrase qui décrit son rôle."""

# 1. Imports de la bibliothèque standard
from datetime import datetime
from typing import Any

# 2. Imports tiers (pip/uv)
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

# 3. Imports locaux (app.)
from app.core.config import settings
from app.schemas.project import ProjectResponse

# 4. Constantes du module
MAX_RESULTS = 100

# 5. Classes

# 6. Fonctions

# 7. Code de niveau module (rare dans FastAPI)
```

### Règles Ruff à connaître

```bash
# Vérifier le code
docker compose exec api uv run ruff check src/

# Corriger automatiquement
docker compose exec api uv run ruff check src/ --fix

# Formater (style Black)
docker compose exec api uv run ruff format src/

# Vérifier les types
docker compose exec api uv run mypy src/
```

### Gestion des erreurs

```python
# ❌ Exception générique
raise Exception("Une erreur s'est produite")

# ✅ Exception HTTP avec code et message clairs
raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Projet introuvable",
)

# ✅ Pour les erreurs de validation métier
raise HTTPException(
    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    detail="Le titre du projet ne peut pas être vide",
)
```

### Async partout

```python
# ❌ Synchrone dans FastAPI (bloque le serveur pendant la requête)
def get_projects(db: Session):
    return db.query(Project).all()

# ✅ Asynchrone (libère le serveur pendant l'attente)
async def get_projects(db: AsyncSession):
    result = await db.execute(select(Project))
    return result.scalars().all()
```

---

## Sécurité — Checklist complète

### Variables d'environnement

- [ ] `.env` est dans `.gitignore`
- [ ] `.env.example` est dans Git (sans valeurs réelles)
- [ ] `SECRET_KEY` est une chaîne longue et aléatoire (min 32 caractères)
- [ ] Les mots de passe DB sont forts et uniques par environnement

```bash
# Générer une SECRET_KEY sécurisée
python -c "import secrets; print(secrets.token_hex(32))"
```

### CORS

- [ ] `ALLOWED_ORIGINS` ne contient que les origines légitimes
- [ ] Jamais `allow_origins=["*"]` en production

### Authentification

- [ ] Les mots de passe sont hashés avec bcrypt (jamais stockés en clair)
- [ ] Les JWT ont une durée d'expiration courte (30 min par défaut)
- [ ] Les endpoints admin sont protégés par `Depends(get_current_user)`

### Base de données

- [ ] Utiliser des requêtes paramétrées (SQLAlchemy le fait automatiquement)
- [ ] Jamais de `f"SELECT ... WHERE id = {user_input}"` (injection SQL)

### Headers de sécurité (configurés dans Caddy)

```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

### Données sensibles dans les logs

- [ ] Ne jamais loguer de mots de passe ou tokens
- [ ] Filtrer les données personnelles dans les logs d'erreur

---

## Checklist avant chaque session

- [ ] Relire ce document pour se remettre en contexte
- [ ] Vérifier à quelle étape de la roadmap on en est
- [ ] Lancer l'environnement Docker dev : `docker compose up -d`
- [ ] Vérifier que l'API répond : `curl http://localhost:8000/health`
- [ ] Committer le travail précédent si ce n'est pas fait
- [ ] Lancer les tests pour vérifier que rien n'est cassé

```bash
# Commandes de dev courantes
docker compose up -d                              # Démarrer
docker compose logs -f api                        # Suivre les logs en temps réel
docker compose exec api uv run pytest             # Tests
docker compose exec api uv run ruff check src/    # Linter
docker compose exec api uv run mypy src/          # Types
docker compose exec api uv run alembic upgrade head  # Migrations
docker compose down                               # Arrêter
docker compose down -v                            # Arrêter + supprimer les volumes (reset DB)
```

---

*Document maintenu tout au long du projet — Phase 2 API Python FastAPI*
*Mis à jour à chaque évolution significative de l'architecture*

# Héros du Foyer

## Description du projet

Le **compagnon de la famille** est une application web destinée à faciliter la gestion des tâches familiales. L'objectif est de proposer une application ludique permettant de répartir les tâches, avec un système de points, de récompenses et un classement des membres de la famille, alliant motivation et bienveillance.

## Fonctionnalités principales

- Répartition simple et flexible des tâches familiales entre les membres.
- Système de gamification comprenant :
    - Attribution de points selon les tâches accomplies.
    - Récompenses motivantes.
    - Classement des membres pour encourager la participation.
- Interface encourageante : valoriser les utilisateurs sans blâmer ceux n’ayant pas terminé leurs tâches, en les incitant positivement à les accomplir.

## Architecture technique

- Application **100% codée en Python**.
- Interface utilisateur construite avec **Materialize CSS**.
- Structure en **architecture logicielle en couches** :
    - Composants front-end et back-end séparés.
- Base de données : **SQLite**.
- Déploiement dans un environnement **Docker**.
- Application entièrement en **français**.

## Pour commencer

### Prérequis

- Python 3.13
- Docker

### Installation

```bash
uv sync
```

### Lancer l'application

```bash
make run
```

### Lancer avec Docker

```bash
docker build -t familly-companion .
docker run -p 80:80 familly-companion
```

### Base de données

Les migrations de la base de données sont gérées avec Alembic. Pour appliquer les migrations, utilisez la commande suivante :

```bash
make db-migrate
```

## Structure du projet

```
.
├── alembic
│   ├── versions
│   └── ...
├── alembic.ini
├── Dockerfile
├── GEMINI.md
├── heros_du_foyer.db
├── Makefile
├── pyproject.toml
├── README.md
├── src
│   ├── __init__.py
│   ├── api
│   │   ├── __init__.py
│   │   ├── user_routes.py
│   │   └── web_routes.py
│   ├── core
│   │   ├── __init__.py
│   │   ├── models.py
│   │   └── services.py
│   ├── data
│   │   ├── __init__.py
│   │   └── database.py
│   ├── main.py
│   └── web
│       ├── __init__.py
│       ├── static
│       │   └── css
│       │       └── style.css
│       └── templates
│           ├── index.html
│           └── register.html
├── tests
└── uv.lock
```

## Utilisation du Makefile

Un `Makefile` est disponible pour simplifier les tâches de développement courantes.

- `make install`: Installe les dépendances du projet.
- `make run`: Lance l'application.
- `make db-migrate`: Applique les migrations de la base de données.
- `make docker-build`: Construit l'image Docker de l'application.
- `make docker-run`: Lance le conteneur Docker.
- `make clean`: Nettoie les fichiers de build et les caches.
- `make help`: Affiche l'aide.

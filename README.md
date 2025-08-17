# Héros du Foyer

## Description du projet

Le **compagnon de la famille** est une application web destinée à faciliter la gestion des tâches familiales. L'objectif est de proposer une application ludique permettant de répartir les tâches, avec un système de points, de récompenses et un classement des membres de la famille, alliant motivation et bienveillance. Le tableau de bord est désormais dynamique, affichant les données en temps réel via des appels API.

## Fonctionnalités principales

- Répartition simple et flexible des tâches familiales entre les membres.
- Système de gamification comprenant :
    - Attribution de points selon les tâches accomplies.
    - Récompenses motivantes.
    - Classement des membres pour encourager la participation.
- Interface encourageante : valoriser les utilisateurs sans blâmer ceux n’ayant pas terminé leurs tâches, en les incitant positivement à les accomplir.
- **Tableau de bord dynamique** : Affichage en temps réel des membres, des tâches et des récompenses, avec des interactions client-côté pour la gestion des tâches et des récompenses.
- **Gestion des Héros (Membres de la Famille)** : Une page dédiée permet de créer, modifier et supprimer les membres de la famille, ainsi que de visualiser leurs points.
- **Gestion des Quêtes et Récompenses** : Une page dédiée permet de créer, modifier et supprimer les quêtes (tâches) et les récompenses.

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

- Python 3.13 (ou version compatible avec `pyproject.toml`)
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

## API Endpoints

Les endpoints API suivants sont disponibles pour interagir avec l'application (requièrent un token d'authentification):

- `GET /api/members`: Récupère la liste de tous les membres de la famille.
- `GET /api/members/{member_id}`: Récupère les détails d'un membre spécifique.
- `POST /api/members`: Crée un nouveau membre de la famille.
- `PUT /api/members/{member_id}`: Met à jour les informations d'un membre existant.
- `DELETE /api/members/{member_id}`: Supprime un membre de la famille.
- `GET /api/tasks`: Récupère la liste de toutes les tâches.
- `GET /api/tasks/{task_id}`: Récupère les détails d'une tâche spécifique.
- `POST /api/tasks`: Crée une nouvelle tâche.
- `PUT /api/tasks/{task_id}`: Met à jour les informations d'une tâche existante.
- `DELETE /api/tasks/{task_id}`: Supprime une tâche.
- `POST /api/tasks/{task_id}/complete`: Marque une tâche comme terminée.
- `GET /api/rewards`: Récupère la liste de toutes les récompenses disponibles.
- `GET /api/rewards/{reward_id}`: Récupère les détails d'une récompense spécifique.
- `POST /api/rewards`: Crée une nouvelle récompense.
- `PUT /api/rewards/{reward_id}`: Met à jour les informations d'une récompense existante.
- `DELETE /api/rewards/{reward_id}`: Supprime une récompense.
- `POST /api/members/{member_id}/claim_reward/{reward_id}`: Permet à un membre de réclamer une récompense.
- `GET /api/leaderboard`: Récupère le classement des membres par points.

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
│   │   ├── schemas.py
│   │   └── services.py
│   ├── data
│   │   ├── __init__.py
│   │   └── database.py
│   ├── main.py
│   └── web
│       ├── __init__.py
│       ├── static
│       │   ├── css
│       │   │   └── style.css
│       │   └── js
│       │       ├── dashboard.js
│       │       ├── members.js
│       │       └── quests_rewards.js
│       └── templates
│           ├── base.html
│           ├── dashboard.html
│           ├── members.html
│           └── quests_rewards.html
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
# Familly companion app

## Description du projet

Je démarre un projet d'application web, un **compagnon de la famille**, destiné à faciliter la gestion des tâches familiales. L'objectif est de proposer une application ludique permettant de répartir les tâches, avec un système de points, de récompenses et un classement des membres de la famille, alliant motivation et bienveillance.

## Fonctionnalités principales

- Répartition simple et flexible des tâches familiales entre les membres.
- Système de gamification comprenant :
    - Attribution de points selon les tâches accomplies.
    - Récompenses motivantes.
    - Classement des membres pour encourager la participation.
- Interface encourageante : valoriser les utilisateurs sans blâmer ceux n’ayant pas terminé leurs tâches, en les incitant positivement à les accomplir.


## Architecture technique

- Application **100% codée en Python**.
- Structure en **architecture logicielle en couches** :
    - Composants front-end et back-end séparés.
- Base de données : **SQLite**.
- Migrations de base de données : **Alembic**.
- Déploiement dans un environnement **Docker**.
- Application entièrement en **français**.


## Interface utilisateur

- Plusieurs pages dont une **page d’administration** accessible uniquement aux utilisateurs autorisés.
- Système d’authentification simple via un fournisseur **d’authentification externe** (Google, Facebook, Apple).
- Le style de l'interface est géré par la bibliothèque **Materialize CSS** pour une apparence moderne et cohérente.
- Un template de base (`base.html`) est utilisé pour assurer la cohérence visuelle sur toutes les pages.


## Gestion des tâches

- Ajout et suppression de tâches rapide et facile pour chaque membre de la famille.


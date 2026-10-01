# IPSSI Express Food

Application de livraison de repas réalisée avec un backend Django REST Framework et un frontend React.

## Répartition actuelle

| Partie | Julien — Backend | Rayen — Frontend |
| --- | --- | --- |
| Architecture globale | Responsable backend | Intégration frontend |
| Django / API REST | Responsable | Consommation API / tests d'intégration UI |
| Clients | API | UI / gestion |
| Plats & desserts | API | UI / gestion |
| Commandes | Logique métier | UI / création / suivi |
| Livreurs | API | UI / affichage / gestion |
| Statut livreur | API | Affichage et gestion |
| Position livreur | API | Affichage et mise à jour |
| Calcul total | Serveur | Affichage |
| Livraison offerte dès 19,99 € | Serveur | Affichage |
| Attribution livreur | Serveur | Affichage |
| Temps estimé | Serveur | Affichage |
| React | — | Responsable |
| Responsive | — | Responsable |
| Déploiement frontend | — | Responsable |

## Structure

```text
express-food/
├── backend/   # Django REST Framework
└── frontend/  # React + Vite — Rayen
```

## Backend

Voir [backend/README.md](backend/README.md).

## Frontend — Rayen

Voir [frontend/README.md](frontend/README.md).

Démarrage rapide :

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Le frontend utilise par défaut l'API :

```text
http://127.0.0.1:8000/api
```

## Parcours utilisateur frontend

- accueil ;
- menu du jour ;
- panier ;
- finalisation de commande ;
- suivi de livraison ;
- affichage des livreurs ;
- interface de gestion pour clients, repas, commandes et livreurs.

## Contribution Rayen

La contribution actuelle de Rayen est centrée sur le **frontend React et l'intégration UI avec l'API Django**.

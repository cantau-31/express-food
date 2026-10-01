# Intégration front ↔ back — IPSSI Express Food

Ce document relie les trois parties du projet et décrit la **couture d'intégration** entre le
backend Django (Julien) et le frontend React (Rayen). Il relève de la partie
**Data & intégration** (Rima).

## Vue d'ensemble

```text
Navigateur
   │
   ▼
Frontend React/Vite (Rayen)            Backend Django REST (Julien)
  src/api.js  ──── HTTP/JSON ────►  /api/...  ──►  services  ──►  MongoDB Atlas
  VITE_API_BASE_URL                 CORS_ALLOWED_ORIGINS            4 collections
```

- **Backend** : API JSON sans état, documents MongoDB (voir [modele-donnees.md](modele-donnees.md)).
- **Frontend** : consomme l'API via `frontend/src/api.js`.
- **Data & intégration** : modèle de données, outils de sauvegarde/restauration/intégrité,
  déploiement backend et câblage ci-dessous (voir [deploiement.md](deploiement.md)).

## Contrat d'API partagé

Les deux côtés doivent respecter le même contrat (référence complète dans
[api.md](api.md)) :

- Toutes les routes se terminent par un **slash final** (`/api/meals/today/`, `/api/orders/{id}/status/`).
- Les champs sont en **snake_case** (`first_name`, `client_id`, `meal_id`, `delivery_driver_id`).
- L'identifiant est exposé en `id` (chaîne).
- Les montants sont des **chaînes à deux décimales** (`"19.99"`) ; le serveur fait autorité sur
  les prix et totaux (les montants envoyés par le client sont ignorés).
- `Content-Type: application/json`.

`frontend/src/api.js` suit déjà ce contrat (routes à slash final, mêmes noms de champs).

## La couture : deux variables à faire correspondre

| Côté | Variable | Valeur | Pointe vers |
| --- | --- | --- | --- |
| Frontend | `VITE_API_BASE_URL` | `https://<backend>/api` | l'URL publique du backend (Render) |
| Backend | `CORS_ALLOWED_ORIGINS` | `https://<frontend>` | l'URL publique du frontend (Vercel) |

Si l'une des deux est fausse, le navigateur affiche une erreur réseau ou une erreur CORS. En
local, les valeurs par défaut suffisent : frontend sur `http://localhost:5173`, backend sur
`http://127.0.0.1:8000`, et `CORS_ALLOWED_ORIGINS=http://localhost:5173` est déjà la valeur par
défaut du backend.

## Démarrage local complet

Deux terminaux, backend d'abord :

```bash
# Terminal 1 — backend (Python)
cd backend
python -m venv .venv && .venv\Scripts\activate   # Windows
pip install -r requirements.txt
cp .env.example .env            # renseigner MONGODB_URI (Atlas) et DJANGO_SECRET_KEY
python manage.py init_db
python manage.py seed_data
python manage.py runserver      # http://127.0.0.1:8000
```

```bash
# Terminal 2 — frontend (Node.js)
cd frontend
npm install
cp .env.example .env            # VITE_API_BASE_URL=http://127.0.0.1:8000/api
npm run dev                     # http://localhost:5173
```

> Les transactions MongoDB (création de commande, affectation du livreur) nécessitent un
> replica set : utiliser **Atlas**, pas un MongoDB local standalone.

## Smoke test de bout en bout

Backend démarré avec `seed_data`, puis frontend ouvert :

1. La page menu affiche les 2 plats + 2 desserts du jour (`GET /api/meals/today/`).
2. Ajouter des repas au panier ; les frais de livraison passent à `0,00 €` dès `19,99 €` de sous-total.
3. Sélectionner/créer un client, puis créer la commande (`POST /api/orders/`).
4. Redirection vers le suivi : statut, livreur affecté, ETA (`GET /api/orders/{id}/status/`).
5. Côté admin, faire passer la commande à `delivered` : le livreur redevient disponible.
6. Aucune erreur CORS dans la console du navigateur.

Pour vérifier la cohérence des données après manipulation :

```bash
cd backend && python manage.py verify_data
```

## Qui fait quoi

| Partie | Responsable | Documents |
| --- | --- | --- |
| Backend / API | Julien | [api.md](api.md), [README](../README.md) |
| Frontend / UI | Rayen | [frontend/DEPLOYMENT.md](../frontend/DEPLOYMENT.md), [README](../README.md) |
| Data & intégration | Rima | [modele-donnees.md](modele-donnees.md), [deploiement.md](deploiement.md), ce document |

# IPSSI Express Food

Application de livraison de repas express : deux plats et deux desserts préparés
chaque jour, commande en ligne, affectation automatique d'un livreur et suivi de
la livraison en temps quasi réel. La livraison est offerte dès **19,99 €**.

Projet annuel **MIA4 — IPSSI**. L'application est composée d'une API REST
(Django + MongoDB) et d'une interface web (React), déployables séparément.

## Sommaire

- [Fonctionnalités](#fonctionnalités)
- [Architecture](#architecture)
- [Structure du dépôt](#structure-du-dépôt)
- [Prérequis](#prérequis)
- [Démarrage rapide (local)](#démarrage-rapide-local)
- [API](#api)
- [Modèle de données](#modèle-de-données)
- [Tests](#tests)
- [Intégration continue](#intégration-continue)
- [Déploiement](#déploiement)
- [Opérations sur les données](#opérations-sur-les-données)
- [Sécurité & RGPD](#sécurité--rgpd)
- [Équipe](#équipe)
- [Documentation](#documentation)

## Fonctionnalités

- Menu du jour : 2 plats + 2 desserts, chargés depuis l'API.
- Panier persistant dans le navigateur, calcul du sous-total et de la livraison.
- Livraison **offerte dès 19,99 €** de sous-total (seuil appliqué par le serveur).
- Commande avec client existant ou création d'un nouveau client.
- Affectation **automatique et transactionnelle** d'un livreur disponible.
- Suivi de commande : statut, livreur affecté, position, temps estimé, récapitulatif.
- Flotte de livreurs (statut `available` / `delivering` / `offline`).
- Interface de gestion (clients, repas, commandes, livreurs).
- Interface responsive desktop / mobile.

## Architecture

```text
Navigateur
   │
   ▼
Frontend React + Vite            Backend Django REST Framework
  src/api.js  ──── HTTP/JSON ──►  /api/...  ──►  services  ──►  MongoDB Atlas
  VITE_API_BASE_URL               CORS_ALLOWED_ORIGINS           4 collections
```

Flux d'une requête : **React → URL Django → vue → serializer → service métier →
MongoDB → réponse JSON**.

| Couche | Technologies |
| --- | --- |
| Frontend | React 19, React Router 7, Vite 7, Vitest |
| Backend | Python 3.10+, Django 5.2, Django REST Framework |
| Accès données | PyMongo (pilote officiel, **sans ODM** : documents = dictionnaires) |
| Base de données | MongoDB Atlas (4 collections : `clients`, `meals`, `delivery_drivers`, `orders`) |
| Tests backend | `mongomock` (aucun compte Atlas requis) |
| Déploiement | Backend → Render · Frontend → Vercel |

Le backend n'active ni l'ORM SQL, ni les sessions, ni l'admin Django
(`DATABASES = {}`). Les montants sont manipulés en `Decimal` et renvoyés en
chaînes à deux décimales ; le serveur fait seul autorité sur les prix et totaux.

## Structure du dépôt

```text
express-food/
├── README.md                   # ce document
├── render.yaml                 # blueprint de déploiement du backend (Render)
├── .gitattributes
├── .github/workflows/
│   ├── backend-ci.yml          # CI backend : check + tests Django/mongomock
│   └── frontend-build.yml      # CI frontend : tests + build Vite
├── docs/
│   ├── api.md                  # référence API complète (endpoints, règles, curl)
│   ├── modele-donnees.md       # modèle de données MongoDB
│   ├── integration.md          # couture front ↔ back (API ↔ CORS)
│   └── deploiement.md          # déploiement & opérations data
├── backend/                    # API Django REST Framework (PyMongo)
│   ├── manage.py
│   ├── requirements.txt        # dépendances compatibles
│   ├── requirements-lock.txt   # versions figées (CI)
│   ├── requirements-prod.txt   # + gunicorn (production)
│   ├── Procfile · Dockerfile · .dockerignore
│   ├── .env.example
│   ├── config/                 # settings, routes globales, wsgi, test_settings
│   ├── common/                 # db.py (PyMongo), serializers, data_ops, commandes
│   ├── clients/ · meals/ · delivery/ · orders/
│   └── backups/                # exports JSON (ignorés par Git — RGPD)
└── frontend/                   # React + Vite
    ├── package.json
    ├── vite.config.js
    ├── vercel.json             # fallback SPA pour React Router
    ├── .env.example
    └── src/                    # api.js, cart.js, App.jsx, AdminDashboard.jsx, tests
```

## Prérequis

- **Python 3.10+** (le backend est testé jusqu'à 3.13).
- **Node.js 20+** et npm (frontend).
- Un **cluster MongoDB Atlas** (le niveau gratuit M0 suffit). Les transactions
  — création de commande, affectation du livreur — exigent un **replica set** :
  un MongoDB local standalone ne convient pas, Atlas oui.

> Les **tests** backend n'ont besoin d'aucun compte Atlas : ils utilisent
> `mongomock`. Seul le serveur en fonctionnement a besoin d'Atlas.

## Démarrage rapide (local)

Deux services, deux terminaux. Démarrer le backend en premier.

### 1. Backend — API Django (`http://127.0.0.1:8000`)

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows ; macOS/Linux : source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # renseigner MONGODB_URI (Atlas) et DJANGO_SECRET_KEY
python manage.py check
python manage.py init_db        # crée les collections et les index (unicité des emails)
python manage.py seed_data      # données de démonstration (2 plats + 2 desserts + livreurs)
python manage.py runserver
```

Générer une clé secrète Django :

```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

`init_db` est requis avant les premières écritures. Aucune migration SQL
(`migrate`) n'est nécessaire. Le vrai `.env` n'est jamais commité.

### 2. Frontend — React (`http://localhost:5173`)

```bash
cd frontend
npm install
cp .env.example .env            # VITE_API_BASE_URL=http://127.0.0.1:8000/api
npm run dev
```

La variable `VITE_API_BASE_URL` pointe vers l'API ; en local, la valeur par
défaut (`http://127.0.0.1:8000/api`) suffit. Le lien exact entre les deux
services (URL d'API ↔ CORS) est décrit dans [docs/integration.md](docs/integration.md).

## API

API JSON sans état exposant quatre ressources. Conventions : routes à **slash
final**, champs **snake_case**, identifiants `id` (chaîne), montants en
**chaînes à deux décimales**, `Content-Type: application/json`.

| Méthodes | Route | Usage |
| --- | --- | --- |
| GET, POST | `/api/clients/` | Lister, créer |
| GET, PUT, PATCH, DELETE | `/api/clients/{id}/` | Lire, modifier, supprimer |
| GET, POST | `/api/meals/` | Lister, créer |
| GET | `/api/meals/today/` | Repas disponibles du jour |
| GET, PATCH, DELETE | `/api/meals/{id}/` | Lire, modifier, supprimer |
| GET, POST | `/api/delivery-drivers/` | Lister, créer |
| GET | `/api/delivery-drivers/available/` | Livreurs disponibles |
| GET, PATCH | `/api/delivery-drivers/{id}/` | Lire, modifier |
| PATCH | `/api/delivery-drivers/{id}/status/` | Changer le statut |
| PATCH | `/api/delivery-drivers/{id}/location/` | Mettre à jour la position |
| GET, POST | `/api/orders/` | Lister, créer |
| GET | `/api/orders/{id}/` | Lire la commande complète |
| GET, PATCH | `/api/orders/{id}/status/` | Suivre, changer le statut |

Référence complète (règles de validation par ressource, codes de réponse,
machine à états des commandes, exemples curl) : **[docs/api.md](docs/api.md)**.

## Modèle de données

Quatre collections MongoDB (`clients`, `meals`, `delivery_drivers`, `orders`),
leurs champs, index, relations et invariants sont décrits dans
**[docs/modele-donnees.md](docs/modele-donnees.md)**. Les commandes conservent
une copie du nom et du prix des repas (historique immuable) ; la suppression
d'un client ne supprime pas ses commandes.

## Tests

**Backend** (depuis `backend/`, `mongomock`, sans Atlas) :

```bash
python manage.py test --settings=config.test_settings
```

Couvre le CRUD clients, l'unicité des emails, la validation, les repas du jour,
les montants et le seuil de livraison, l'affectation du livreur, le suivi, les
transitions de statut, les erreurs réseau, CORS, le seed, et les outils data
(sauvegarde / restauration / contrôle d'intégrité). Des tests d'intégration
MongoDB facultatifs sont activables via `RUN_MONGODB_INTEGRATION=1` (voir
[docs/api.md](docs/api.md) et les commentaires de `orders/test_integration.py`).

**Frontend** (depuis `frontend/`, Vitest) :

```bash
npm test
```

Couvre le calcul du panier (sous-total, frais, seuil 19,99 €, panier vide), le
client API HTTP et un parcours de commande de bout en bout.

## Intégration continue

Deux workflows GitHub Actions, filtrés par chemin pour ne se déclencher que sur
leur sous-projet :

- [`.github/workflows/backend-ci.yml`](.github/workflows/backend-ci.yml) — sur
  `backend/**` : `manage.py check` puis toute la suite de tests avec les versions
  figées (`requirements-lock.txt`). Aucun secret requis (tests `mongomock`).
- [`.github/workflows/frontend-build.yml`](.github/workflows/frontend-build.yml)
  — sur `frontend/**` : installation, tests Vitest puis build Vite.

## Déploiement

Les deux services se déploient séparément :

- **Backend → Render** via le blueprint [`render.yaml`](render.yaml)
  (`gunicorn`, health check sur `/api/meals/today/`). Un `Dockerfile` est aussi
  fourni en alternative.
- **Frontend → Vercel** (preset Vite, root directory `frontend`, build
  `npm run build`, sortie `dist`, fallback SPA via `vercel.json`).

Le point clé de l'intégration : `VITE_API_BASE_URL` (frontend) doit pointer vers
l'URL publique du backend, et `CORS_ALLOWED_ORIGINS` (backend) doit contenir
l'URL publique exacte du frontend. Procédure complète, variables d'environnement
et check-list de mise en production : **[docs/deploiement.md](docs/deploiement.md)**
et **[docs/integration.md](docs/integration.md)**.

## Opérations sur les données

Trois commandes de gestion Django (depuis `backend/`, `.env` configuré) :

```bash
python manage.py backup_data      # export JSON des 4 collections (backups/)
python manage.py restore_data --input chemin/vers/sauvegarde.json
python manage.py verify_data      # contrôle d'intégrité (lecture seule)
```

L'export utilise le JSON étendu MongoDB (préserve `ObjectId` et `datetime`).
`verify_data` vérifie les références, les montants et la cohérence
livreur/commande. Détails dans [docs/deploiement.md](docs/deploiement.md).

## Sécurité & RGPD

- Cette API de **démonstration** n'a ni authentification ni rôles : à réserver à
  un environnement de développement avec données fictives.
- Les secrets (`DJANGO_SECRET_KEY`, `MONGODB_URI`) vivent uniquement dans `.env`
  (ou le dashboard de la plateforme) — **jamais commités**.
- Les sauvegardes contiennent des données personnelles : le dossier
  `backend/backups/` est **ignoré par Git** ; ne jamais les committer ni les
  partager, et limiter leur durée de conservation.
- En production : `DEBUG=False`, `ALLOWED_HOSTS` et `CORS_ALLOWED_ORIGINS`
  explicites, HTTPS (fourni par Render et Vercel), serveur WSGI (`gunicorn`).

## Équipe

Projet réalisé en trinôme (MIA4 — IPSSI).

| Partie | Responsable | Périmètre |
| --- | --- | --- |
| Backend / API | Julien | Django REST, logique métier, accès MongoDB (PyMongo), règles d'affectation et de statut |
| Frontend / UI | Rayen | Interface React, parcours commande & suivi, responsive, intégration de l'API |
| Data & intégration | Rima | Modèle de données, sauvegarde / restauration / intégrité, CI, déploiement et couture front ↔ back |

## Documentation

| Document | Contenu |
| --- | --- |
| [docs/api.md](docs/api.md) | Référence API : endpoints, validation, codes, machine à états, curl |
| [docs/modele-donnees.md](docs/modele-donnees.md) | Collections MongoDB, champs, index, relations, invariants |
| [docs/integration.md](docs/integration.md) | Couture front ↔ back, variables, smoke test de bout en bout |
| [docs/deploiement.md](docs/deploiement.md) | Déploiement backend/frontend, CI, opérations data, check-list |

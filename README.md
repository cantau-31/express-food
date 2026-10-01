# IPSSI Express Food

Application web de livraison de repas réalisée dans le cadre du projet annuel IPSSI.

## Architecture

```text
React (frontend)
    ↓ HTTP / JSON
API Django REST Framework
    ↓ PyMongo
MongoDB Atlas
```

Le dépôt contient actuellement le backend Django dans `backend/`. Le frontend React pourra être ajouté dans un dossier `frontend/`.

## Répartition de l'équipe

| Partie | Julien — Backend | Rima — Frontend | Rayen — Data / intégration |
| --- | --- | --- | --- |
| Architecture globale | Responsable | Contribution | Contribution |
| API REST | Responsable | — | Tests / validation |
| Gestion clients | Backend / API | Interface | MongoDB / données |
| Gestion plats / desserts | Backend / API | Interface | MongoDB / données |
| Gestion commandes | Logique métier | Interface | MongoDB / données |
| Gestion livreurs | Backend / API | Interface | MongoDB / données |
| Statut et position livreur | API / logique | Affichage | Persistance MongoDB |
| MongoDB Atlas | Connexion backend | — | Responsable |
| Collections / index MongoDB | Modèles / accès | — | Responsable |
| Connexion React ↔ API | API / CORS | Consommation API | Tests d'intégration |
| Tests API | Backend | — | Intégration / données |
| Déploiement | Backend | Frontend | Support DB / configuration |
| README / installation | Backend | Frontend | DB / intégration |

### Contribution Rayen — Data / intégration

La partie Data / intégration couvre notamment :

- configuration MongoDB Atlas et variables d'environnement ;
- collections `clients`, `meals`, `delivery_drivers`, `orders` ;
- index MongoDB et unicité des emails clients ;
- stockage des statuts et positions des livreurs ;
- données de démonstration ;
- tests API liés à la persistance ;
- tests d'intégration réels sur MongoDB Atlas ;
- validation des transactions et de l'affectation concurrente d'un livreur ;
- documentation de la configuration Atlas et du déploiement.

## Installation du backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Sous Windows :

```bash
.venv\Scripts\activate
```

Renseigner ensuite `backend/.env`, en particulier :

```env
DJANGO_SECRET_KEY=une-cle-secrete-longue
MONGODB_URI=mongodb+srv://USER:PASSWORD@CLUSTER.mongodb.net/?retryWrites=true&w=majority
MONGODB_DATABASE=express_food
```

Initialiser MongoDB et charger les données de démonstration :

```bash
python manage.py check
python manage.py check_mongodb
python manage.py init_db
python manage.py seed_data
python manage.py verify_data
python manage.py db_status
python manage.py runserver
```

API locale : `http://127.0.0.1:8000/api/`.

Endpoint de santé / readiness : `GET /api/health/`. Il renvoie `200` lorsque l’API et MongoDB répondent, et `503` si MongoDB est indisponible.

## Tests

Tests unitaires sans compte Atlas :

```bash
cd backend
python manage.py test --settings=config.test_settings
```

Tests d'intégration sur un vrai cluster Atlas :

```bash
RUN_MONGODB_INTEGRATION=1 python manage.py test orders.test_integration --settings=config.test_settings
```

Ces tests utilisent une base temporaire `express_food_test_<uuid>` puis la suppriment automatiquement.

## MongoDB Atlas

La procédure détaillée est disponible dans [docs/MONGODB_ATLAS.md](docs/MONGODB_ATLAS.md). Le schéma logique des collections est documenté dans [docs/DATA_MODEL.md](docs/DATA_MODEL.md). Une fiche de démonstration et de soutenance pour la partie Data / intégration est disponible dans [docs/RAYEN_SOUTENANCE.md](docs/RAYEN_SOUTENANCE.md).

Les identifiants Atlas ne doivent jamais être commités. Le fichier `.env` est ignoré par Git ; seul `.env.example` est versionné.

## Déploiement backend

Un Blueprint Render est fourni dans `render.yaml`. Les secrets, notamment `DJANGO_SECRET_KEY` et `MONGODB_URI`, doivent être définis directement dans l'environnement de déploiement.

## Règles métier principales

- deux plats et deux desserts peuvent être proposés chaque jour ;
- les commandes utilisent les prix calculés côté serveur ;
- livraison gratuite à partir de **19,99 €** ;
- un livreur disponible peut être affecté atomiquement à une commande ;
- le suivi expose le statut, le prénom du livreur, sa position éventuelle et l'estimation ;
- une livraison ou une annulation libère le livreur.

## Méthodologie projet

Le projet est organisé avec Git/GitHub et une répartition par responsabilités.

**Trello : à renseigner avec le lien du tableau de l'équipe avant la remise finale.**


## Vérification d'intégrité des données

La commande suivante contrôle les principales références et incohérences sans modifier les données :

```bash
cd backend
python manage.py verify_data
```

Elle vérifie notamment les statuts de commandes/livreurs, les coordonnées partielles, les références client/livreur des commandes et la cohérence entre `active_order_id` d'un livreur et la commande affectée.


## Données personnelles / RGPD

Le projet limite les données client aux informations nécessaires à la livraison. Pour une démonstration de gestion du droit à l'effacement sans supprimer l'historique transactionnel, une commande d'administration permet d'anonymiser les informations personnelles d'un client :

```bash
cd backend
python manage.py anonymize_client CLIENT_ID
```

La commande remplace le prénom, le nom, l'email, le téléphone et l'adresse par des valeurs anonymisées, tout en conservant les commandes historiques liées à l'identifiant technique du client.

Cette fonctionnalité aide à démontrer une démarche de minimisation et d'anonymisation, mais **ne constitue pas à elle seule une conformité RGPD complète** : une politique de conservation, les bases légales, l'information des personnes et les contrôles d'accès restent à définir par le projet.

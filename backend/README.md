# IPSSI Express Food — Backend

Backend étudiant Python / Django REST Framework / MongoDB Atlas, indépendant du frontend React. Aucun frontend, paiement ou service cartographique n'est inclus.

## Installation

Prérequis : Python 3.10 ou supérieur, accès réseau à MongoDB Atlas, un environnement virtuel. Développé et testé ici avec Python 3.14 et Django 5.2.

Depuis la racine du dépôt :

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Sous Windows, activer avec `.venv\Scripts\activate`. Modifier `.env` avant de lancer le serveur. Générer une clé Django avec :

```bash
python -c 'import secrets; print(secrets.token_urlsafe(50))'
```

Reporter cette valeur dans `DJANGO_SECRET_KEY`. Le vrai `.env` est ignoré par Git. Les dépendances compatibles sont dans `requirements.txt` ; `requirements-lock.txt` fige les versions utilisées lors des vérifications (`pip install -r requirements-lock.txt`).

## Configurer MongoDB Atlas

1. Créer un projet et un cluster Atlas.
2. Dans **Database Access**, créer un utilisateur de base de données, avec les droits `readWrite` sur `express_food`.
3. Dans **Network Access**, autoriser l'adresse IP du poste ou du serveur.
4. Dans **Connect → Drivers → Python**, copier l'URI `mongodb+srv://…` dans `MONGODB_URI` du fichier `.env`. Remplacer utilisateur et mot de passe ; encoder les caractères réservés du mot de passe pour une URI.
5. Définir `MONGODB_DATABASE=express_food`.
6. Créer les index, charger les données et lancer Django :

```bash
python manage.py check
python manage.py init_db
python manage.py seed_data
python manage.py runserver
```

`init_db` est requis avant les premières écritures pour garantir notamment l'unicité des emails. `seed_data` le lance aussi. Il crée les collections et leurs index. Les transactions nécessitent un replica set ou cluster shardé, comme Atlas ; un MongoDB local standalone ne convient pas. Aucune migration SQL ni commande `migrate` n'est nécessaire.

Le serveur écoute sur `http://127.0.0.1:8000`. `check` valide Django sans contacter Atlas ; `init_db` vérifie réellement l'accès à MongoDB. L'absence d'identifiants Atlas empêche donc seulement les opérations sur les données, pas les tests unitaires.

## Configuration

| Variable | Rôle / défaut |
| --- | --- |
| `DJANGO_SECRET_KEY` | Obligatoire, secret Django |
| `DEBUG` | `False` par défaut ; `True` dans l'exemple de développement |
| `ALLOWED_HOSTS` | Hôtes autorisés, séparés par des virgules |
| `CORS_ALLOWED_ORIGINS` | Origines exactes, par défaut `http://localhost:5173` |
| `MONGODB_URI` | URI Atlas, conservée uniquement dans `.env` |
| `MONGODB_DATABASE` | `express_food` |
| `FREE_DELIVERY_THRESHOLD` | `19.99` euros |
| `DEFAULT_DELIVERY_FEE` | `2.99` euros |
| `DEFAULT_DELIVERY_ESTIMATE` | `20` minutes |

La journée métier est celle du fuseau `Europe/Paris`. Les horodatages sont conservés en UTC. L'estimation est **simulée et fixe**, pas un compte à rebours ni une garantie de livraison en moins de 20 minutes. Elle vaut `null` sans livreur, `0` après livraison et `null` après annulation. Elle pourra être remplacée par un service cartographique.

## Architecture et choix technique

```text
backend/
├── manage.py
├── requirements.txt / requirements-lock.txt
├── .env.example / .gitignore
├── config/
├── common/
├── clients/
├── meals/
├── delivery/
└── orders/
```

Flux : **React → URL Django → vue → serializer → service métier → MongoDB → réponse JSON**.

PyMongo est le pilote officiel MongoDB. Il donne directement accès aux quatre collections `clients`, `meals`, `delivery_drivers`, `orders`. Aucun ODM n'est utilisé : les documents sont des dictionnaires, leur contrat d'entrée/sortie est explicite dans les serializers DRF. L'ORM SQL, les sessions et l'administration Django ne sont pas activés.

Les vues clients et repas réutilisent un petit CRUD. Les services commandes et livraison portent les règles métier. Les identifiants MongoDB `_id` sont exposés sous forme de chaînes `id`. Les montants sont calculés avec `Decimal`, stockés et renvoyés en chaînes à deux décimales.

## API JSON

Toutes les routes utilisent un slash final. Envoyer `Content-Type: application/json`.

| Méthodes | Route | Usage |
| --- | --- | --- |
| GET, POST | `/api/clients/` | Lister, créer |
| GET, PUT, PATCH, DELETE | `/api/clients/{id}/` | Lire, remplacer, modifier, supprimer |
| GET, POST | `/api/meals/` | Lister, créer |
| GET | `/api/meals/today/` | Repas disponibles du jour |
| GET, PATCH, DELETE | `/api/meals/{id}/` | Lire, modifier, supprimer |
| GET, POST | `/api/delivery-drivers/` | Lister, créer |
| GET | `/api/delivery-drivers/available/` | Livreurs disponibles |
| GET, PATCH | `/api/delivery-drivers/{id}/` | Lire, modifier |
| PATCH | `/api/delivery-drivers/{id}/status/` | Statut |
| PATCH | `/api/delivery-drivers/{id}/location/` | Position |
| GET, POST | `/api/orders/` | Lister, créer |
| GET | `/api/orders/{id}/` | Lire la commande |
| GET, PATCH | `/api/orders/{id}/status/` | Suivre / changer statut |

Les clients requièrent `first_name`, `last_name`, `email`, `phone`, `address`.
Les repas requièrent `name`, `price`, `type`, `date`.
Les livreurs requièrent `first_name`, `last_name`, `phone`.
Une commande requiert un client existant et des lignes d'articles valides.

## Tests

```bash
python manage.py test --settings=config.test_settings
```

Les tests unitaires remplacent MongoDB par `mongomock`.

Tests d'intégration facultatifs :

```bash
RUN_MONGODB_INTEGRATION=1 python manage.py test orders.test_integration --settings=config.test_settings
```

## Périmètre de sécurité et données personnelles

Cette API de démonstration n'inclut pas d'authentification ni de rôles. La conserver sur un environnement de développement avec données fictives. Avant une exposition publique, ajouter authentification, autorisations, HTTPS et règles de conservation/suppression des données.

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
python manage.py check_mongodb
python manage.py init_db
python manage.py seed_data
python manage.py runserver
```

`init_db` est requis avant les premières écritures pour garantir notamment l'unicité des emails. `seed_data` le lance aussi. Il crée les collections et leurs index. Les transactions nécessitent un replica set ou cluster shardé, comme Atlas ; un MongoDB local standalone ne convient pas. Aucune migration SQL ni commande `migrate` n'est nécessaire.

Le serveur écoute sur `http://127.0.0.1:8000`. `check` valide Django sans contacter Atlas ; `check_mongodb` effectue un ping explicite du cluster ; `init_db` vérifie réellement l'accès à MongoDB. L'absence d'identifiants Atlas empêche donc seulement les opérations sur les données, pas les tests unitaires.

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
├── config/                  # Paramètres, routes globales, WSGI, settings de test
├── common/
│   ├── db.py                # Connexion PyMongo, transactions, index
│   ├── serializers.py       # Identifiants MongoDB et champs communs
│   ├── views.py             # CRUD partagé
│   ├── exceptions.py        # Erreurs MongoDB → réponses JSON
│   ├── testing.py / tests.py
│   └── management/commands/ # init_db, seed_data
├── clients/                 # serializers.py, views.py, urls.py, tests.py
├── meals/                   # serializers.py, views.py, urls.py, tests.py
├── delivery/                # idem + services.py
└── orders/                  # idem + services.py, test_integration.py
```

Flux : **React → URL Django → vue → serializer → service métier → MongoDB → réponse JSON**.

PyMongo est le pilote officiel MongoDB. Il donne directement accès aux quatre collections `clients`, `meals`, `delivery_drivers`, `orders`. Aucun ODM n'est utilisé : les documents sont des dictionnaires, leur contrat d'entrée/sortie est explicite dans les serializers DRF. L'ORM SQL, les sessions et l'administration Django ne sont pas activés.

Les vues clients et repas réutilisent un petit CRUD. Les services commandes et livraison portent les règles métier. Les identifiants MongoDB `_id` sont exposés sous forme de chaînes `id`. Les montants sont calculés avec `Decimal`, stockés et renvoyés en chaînes à deux décimales, par exemple `"19.99"`. Le frontend doit les traiter comme des montants, pas comme une source de prix faisant autorité.

Les commandes contiennent une copie du nom et du prix de chaque repas : modifier ou supprimer un repas ne modifie pas l'historique de la commande. La suppression d'un client ne supprime pas les commandes ; leur `client_id` reste une référence historique.

## API JSON

Toutes les routes utilisent un slash final. Envoyer `Content-Type: application/json`. Les listes retournent des tableaux JSON (sans pagination, adaptés au volume de cette démonstration).

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
| PATCH | `/api/delivery-drivers/{id}/status/` | `{"status":"offline"}` |
| PATCH | `/api/delivery-drivers/{id}/location/` | `{"latitude":43.6045,"longitude":1.4440}` |
| GET, POST | `/api/orders/` | Lister, créer |
| GET | `/api/orders/{id}/` | Lire la commande complète |
| GET, PATCH | `/api/orders/{id}/status/` | Suivre, changer le statut |

Les clients requièrent `first_name`, `last_name`, `email`, `phone`, `address`. Les emails sont normalisés en minuscules et ont un index unique.

Les repas requièrent `name`, `price`, `type` (`dish` ou `dessert`), `date` (`YYYY-MM-DD`). `description` et `image_url` sont facultatifs ; `available` vaut `true` par défaut. Le seed crée deux plats et deux desserts pour aujourd'hui. Aucun plafond artificiel d'entrées n'est imposé.

Les livreurs requièrent `first_name`, `last_name`, `phone`. Le statut initial est `available` ou `offline`. Les coordonnées sont facultatives mais doivent être fournies ensemble ; latitude entre -90 et 90, longitude entre -180 et 180. `delivering` est réservé à l'affectation par une commande.

Une commande requiert un client existant et de 1 à 100 lignes distinctes, chaque quantité entière entre 1 et 100. Tous les repas doivent être disponibles **et datés d'aujourd'hui**. Les champs financiers éventuellement envoyés sont ignorés : prix et totaux viennent exclusivement du serveur.

Réponses : `200` lecture/modification, `201` création, `204` suppression, `400` validation/transition/email dupliqué, `404` identifiant ou référence introuvable, `405` méthode non autorisée, `503` MongoDB indisponible. Les erreurs de validation indiquent les champs concernés ; les erreurs générales utilisent `detail` et ne révèlent pas l'URI MongoDB.

Cette version privilégie ce contrat documenté et les exemples ci-dessous ; Swagger n'est pas installé.

## Règles d'affectation et statuts

L'affectation réserve atomiquement le premier livreur disponible (ordre des identifiants), puis insère la commande dans **la même transaction**. Un échec annule les deux opérations. `with_transaction` gère les conflits temporaires MongoDB. Le champ interne `active_order_id` empêche une commande ancienne de libérer un livreur réaffecté.

- Avec livreur : commande `accepted`, livreur `delivering`.
- Sans livreur : commande `pending`, `delivery_driver_id` et estimation à `null`.
- `pending → accepted` retente l'affectation ; reste `pending` avec erreur `400` si aucun livreur n'est disponible. Il n'y a pas de tâche automatique en arrière-plan.
- `pending → cancelled` est autorisé.
- `accepted → preparing / out_for_delivery / delivered / cancelled`.
- `preparing → out_for_delivery / delivered / cancelled`.
- `out_for_delivery → delivered / cancelled`.
- `delivered` et `cancelled` sont terminaux. Répéter le statut courant est sans effet.

Le passage direct `accepted → delivered` facilite la démonstration demandée. La livraison **ou l'annulation** libère le livreur dans la transaction. Un changement manuel ne peut pas rendre disponible ou mettre hors ligne un livreur occupé.

## Démonstration avec curl

Après le seed, récupérer les identifiants :

```bash
curl http://127.0.0.1:8000/api/clients/
curl http://127.0.0.1:8000/api/meals/today/
curl http://127.0.0.1:8000/api/delivery-drivers/available/
```

Remplacer `CLIENT_ID` et `MEAL_ID` dans cette requête :

```bash
curl -X POST http://127.0.0.1:8000/api/orders/ \
  -H 'Content-Type: application/json' \
  -d '{"client_id":"CLIENT_ID","items":[{"meal_id":"MEAL_ID","quantity":2}]}'
```

Deux poulets à 12,99 € donnent un sous-total de `25.98`, des frais de `0.00` et un total de `25.98`. Un poulet donne `12.99 + 2.99 = 15.98`.

Avec l'identifiant de la commande retournée :

```bash
curl http://127.0.0.1:8000/api/orders/ORDER_ID/status/
curl http://127.0.0.1:8000/api/delivery-drivers/
curl -X PATCH http://127.0.0.1:8000/api/orders/ORDER_ID/status/ \
  -H 'Content-Type: application/json' -d '{"status":"delivered"}'
curl http://127.0.0.1:8000/api/delivery-drivers/available/
```

Exemple de suivi sans livreur :

```json
{"order_id":"…","status":"pending","driver":null,"estimated_delivery_minutes":null}
```

Exemple avec livreur (coordonnées nulles tant qu'elles n'ont pas été renseignées) :

```json
{"order_id":"…","status":"accepted","driver":{"id":"…","first_name":"Lucas","latitude":null,"longitude":null},"estimated_delivery_minutes":20}
```

## Tests

Exécuter **depuis le dossier `backend`** :

```bash
python manage.py test --settings=config.test_settings
```

Les tests unitaires remplacent MongoDB par `mongomock` et n'utilisent aucun compte Atlas. Ils couvrent CRUD clients, unicité, validation, repas du jour, montants, seuil, indisponibilité des repas, affectation, suivi, transitions, protection du livreur, erreurs réseau, CORS et seed répétable. Ils ne simulent pas les garanties transactionnelles d'un vrai serveur.

Tests d'intégration facultatifs, avec `.env` configuré pour un cluster **de test** :

```bash
RUN_MONGODB_INTEGRATION=1 python manage.py test orders.test_integration --settings=config.test_settings
```

Ils créent une base temporaire `express_food_test_<uuid>`, testent deux commandes concurrentes et le rollback après échec, puis suppriment cette base. L'utilisateur MongoDB doit avoir les droits de création/écriture/suppression sur cette base de test. Ils ne modifient pas les collections `express_food`. Sans la variable d'activation, ces deux tests sont ignorés.

## Périmètre de sécurité et données personnelles

Cette API de démonstration n'inclut pas d'authentification ni de rôles : toute personne ayant accès au serveur peut lire et modifier les ressources. La conserver sur un environnement de développement avec données fictives. Avant une exposition publique, ajouter authentification, autorisations client/personnel, HTTPS et règles de conservation/suppression des données. CORS limite les appels des navigateurs mais ne constitue pas une authentification.

Les champs se limitent aux besoins de livraison. Le suivi ne retourne que le prénom et la position du livreur. Le projet ne prétend pas assurer seul une conformité RGPD complète : les commandes sont conservées lors de la suppression d'un client et une politique de rétention reste à définir. En déploiement, utiliser `DEBUG=False`, des hôtes et origines explicites, et un serveur WSGI adapté ; `runserver` est réservé au développement.

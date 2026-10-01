# MongoDB Atlas — configuration Data / intégration

Cette procédure correspond à la partie Data / intégration du projet Express Food.

## 1. Créer le cluster

1. Créer un projet MongoDB Atlas.
2. Créer un cluster compatible avec les transactions.
3. Conserver le nom logique de base : `express_food`.

## 2. Sécuriser les accès réseau

Dans **Network Access**, autoriser uniquement :

- l'adresse IP de développement des membres concernés ;
- l'adresse IP ou le réseau du serveur de production lorsque celui-ci est connu.

Éviter `0.0.0.0/0` en production sauf nécessité temporaire et documentée.

## 3. Créer les utilisateurs et privilèges

Le cahier des charges demande de gérer plusieurs niveaux de privilèges.

Configuration conseillée :

### Utilisateur application

Nom indicatif : `express_food_app`

Droit :
- `readWrite` sur la base `express_food`.

Cet utilisateur est utilisé dans `MONGODB_URI` par Django.

### Utilisateur lecture seule

Nom indicatif : `express_food_readonly`

Droit :
- `read` sur la base `express_food`.

Il permet une consultation sans modification.

### Responsable Data / owner

Le compte Atlas du responsable Data conserve les droits nécessaires à l'administration du projet Atlas, sans réutiliser ces privilèges dans l'application Django.

## 4. Variables d'environnement

Créer `backend/.env` à partir de `.env.example` :

```env
DJANGO_SECRET_KEY=replace-with-a-long-random-secret
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173
MONGODB_URI=mongodb+srv://USER:PASSWORD@CLUSTER.mongodb.net/?retryWrites=true&w=majority
MONGODB_DATABASE=express_food
FREE_DELIVERY_THRESHOLD=19.99
DEFAULT_DELIVERY_FEE=2.99
DEFAULT_DELIVERY_ESTIMATE=20
```

Ne jamais versionner le vrai fichier `.env`.

## 5. Initialiser les collections et index

Depuis `backend/` :

```bash
python manage.py check
python manage.py init_db
python manage.py seed_data
```

`init_db` crée les index utiles :

- `clients.email` unique ;
- `meals(date, available)` ;
- `delivery_drivers.status` ;
- `orders.client_id`.

`seed_data` insère des données fictives reproductibles :

- 2 clients ;
- 2 plats ;
- 2 desserts ;
- 3 livreurs.

## 6. Vérifier la persistance

Démarrer l'API :

```bash
python manage.py runserver
```

Puis vérifier les routes :

```bash
curl http://127.0.0.1:8000/api/clients/
curl http://127.0.0.1:8000/api/meals/today/
curl http://127.0.0.1:8000/api/delivery-drivers/
curl http://127.0.0.1:8000/api/orders/
```

Les documents doivent également être visibles dans Atlas via **Browse Collections**.

## 7. Tests d'intégration Atlas

Exécuter :

```bash
RUN_MONGODB_INTEGRATION=1 python manage.py test orders.test_integration --settings=config.test_settings
```

Les tests créent une base temporaire nommée `express_food_test_<uuid>`, vérifient notamment :

- qu'un seul livreur est réservé lors de deux créations concurrentes ;
- qu'une transaction est annulée si l'insertion de la commande échoue ;
- que le livreur redevient disponible après livraison.

La base temporaire est supprimée à la fin.

## 8. Vérifications avant soutenance

- cluster Atlas accessible ;
- `init_db` réussi ;
- `seed_data` réussi ;
- tests unitaires réussis ;
- tests d'intégration Atlas réussis ;
- aucun secret présent sur GitHub ;
- utilisateur application limité à `readWrite` sur `express_food` ;
- utilisateur lecture seule créé ;
- capture ou démonstration Atlas prête pour la soutenance.

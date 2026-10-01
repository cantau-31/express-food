# Rayen — fiche de soutenance Data / intégration

Cette fiche sert de support rapide pour présenter la partie **Data / intégration** du projet Express Food.

## 1. Mon rôle

Je suis responsable de la partie **MongoDB Atlas et intégration des données**.

Mon travail couvre :

- la connexion entre Django et MongoDB Atlas ;
- la structure des collections ;
- les index et contraintes de données ;
- le stockage du statut et de la position des livreurs ;
- les données de démonstration ;
- les tests API liés à la persistance ;
- les tests d'intégration réels sur Atlas ;
- la configuration nécessaire au déploiement.

## 2. Architecture à expliquer

```text
React
  ↓ JSON / HTTP
Django REST Framework
  ↓
Services métier
  ↓
PyMongo
  ↓
MongoDB Atlas
```

Le backend n'utilise pas une base SQL Django. Les documents MongoDB sont manipulés avec PyMongo.

## 3. Collections

### clients
Stocke les informations utiles à la livraison.

Point important :
- index unique sur `email`.

### meals
Stocke les plats et desserts.

Points importants :
- date du menu ;
- disponibilité ;
- prix ;
- type `dish` ou `dessert`.

### delivery_drivers
Stocke les livreurs.

Points importants :
- statut `available`, `delivering` ou `offline` ;
- latitude et longitude ;
- commande active éventuelle.

### orders
Stocke les commandes.

Points importants :
- référence client ;
- lignes de commande ;
- sous-total ;
- frais de livraison ;
- total ;
- livreur affecté ;
- statut ;
- estimation de livraison.

## 4. Règle métier à montrer

La livraison devient gratuite à partir de **19,99 €** :

```python
fee = Decimal("0") if subtotal >= settings.FREE_DELIVERY_THRESHOLD else settings.DEFAULT_DELIVERY_FEE
```

Le calcul est fait côté serveur afin que le frontend ne puisse pas imposer un faux total.

## 5. Affectation d'un livreur

L'affectation est atomique :

1. chercher un livreur `available` ;
2. le passer en `delivering` ;
3. lui affecter la commande ;
4. enregistrer la commande dans la même transaction.

Le but est d'éviter que deux commandes simultanées reçoivent le même livreur.

## 6. Commandes de démonstration

Depuis `backend/` :

```bash
python manage.py check
python manage.py check_mongodb
python manage.py init_db
python manage.py seed_data
python manage.py db_status
python manage.py preflight
```

Puis :

```bash
python manage.py runserver
```

Le diagnostic `db_status` doit afficher les quatre collections, leur nombre de documents et leurs index sans révéler l'URI MongoDB.

## 7. Tests

### Tests unitaires / API

```bash
python manage.py test --settings=config.test_settings
```

Ils utilisent `mongomock`, donc ils ne modifient pas Atlas.

### Tests d'intégration Atlas

```bash
RUN_MONGODB_INTEGRATION=1 python manage.py test orders.test_integration --settings=config.test_settings
```

Ils utilisent une base temporaire `express_food_test_<uuid>`.

Deux comportements importants sont vérifiés :

- deux commandes concurrentes ne peuvent pas réserver le même livreur ;
- si l'insertion d'une commande échoue, la transaction rend le livreur disponible.

## 8. Sécurité

À préciser pendant la soutenance :

- le vrai `.env` n'est jamais versionné ;
- l'URI MongoDB est une variable d'environnement ;
- l'application utilise un compte Atlas limité à `readWrite` sur `express_food` ;
- un compte séparé peut être créé en lecture seule ;
- les droits d'administration Atlas ne sont pas utilisés par l'application.

## 9. Déploiement

Le dépôt contient `render.yaml`.

En production, les valeurs suivantes doivent être configurées comme secrets ou variables d'environnement :

- `DJANGO_SECRET_KEY`
- `MONGODB_URI`
- `ALLOWED_HOSTS`
- `CORS_ALLOWED_ORIGINS`

`DEBUG` doit rester à `False`.

## 10. Mini discours

> Ma partie concerne les données et l'intégration MongoDB Atlas. J'ai organisé la persistance autour de quatre collections : clients, repas, livreurs et commandes. J'ai ajouté les index nécessaires, notamment l'unicité des emails, et je gère aussi le statut ainsi que la position des livreurs. La connexion Atlas est sécurisée par variables d'environnement. Pour l'intégration, nous avons des tests unitaires avec une base simulée et des tests réels Atlas qui vérifient notamment les transactions et l'affectation concurrente d'un livreur. Le calcul des montants et de la livraison gratuite à partir de 19,99 € reste côté serveur pour éviter qu'un client puisse modifier les prix depuis le frontend.

## 11. Questions probables

**Pourquoi MongoDB ?**  
Parce que le cahier des charges impose MongoDB Atlas et que le format document convient bien aux commandes contenant une liste d'articles.

**Pourquoi copier le nom et le prix du repas dans la commande ?**  
Pour garder l'historique exact de la commande même si le menu ou le prix change ensuite.

**Pourquoi un index unique sur l'email ?**  
Pour empêcher deux clients d'avoir le même email au niveau de la base.

**Pourquoi utiliser une transaction ?**  
Pour que l'affectation du livreur et la création de la commande soient validées ou annulées ensemble.

**Pourquoi utiliser un fichier .env ?**  
Pour éviter de mettre les identifiants et secrets dans le code ou sur GitHub.


## 12. Préflight avant démonstration

Une fois Atlas configuré, lancer :

```bash
cd backend
python manage.py preflight
```

Cette commande enchaîne la vérification de connexion MongoDB et le contrôle d'intégrité logique des données. Si elle termine par `Préflight Data / intégration : OK`, la partie Data est prête pour la démonstration.

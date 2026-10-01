# Référence API — IPSSI Express Food

API JSON du backend Django REST Framework. Elle expose quatre ressources
(`clients`, `meals`, `delivery-drivers`, `orders`) stockées dans MongoDB.
Pour le modèle de données, voir [modele-donnees.md](modele-donnees.md).

## Conventions

- Toutes les routes se terminent par un **slash final** (`/api/meals/today/`).
- En-tête `Content-Type: application/json` pour les corps de requête.
- Les champs sont en **snake_case** (`first_name`, `client_id`, `meal_id`,
  `delivery_driver_id`).
- L'identifiant MongoDB `_id` est exposé sous forme de chaîne dans le champ `id`.
- Les montants sont calculés avec `Decimal` et renvoyés en **chaînes à deux
  décimales** (`"19.99"`). Le **serveur fait autorité** sur les prix et les
  totaux : tout montant envoyé par le client est ignoré.
- Les horodatages sont conservés en UTC ; la journée métier suit le fuseau
  `Europe/Paris`.
- Les listes renvoient des tableaux JSON (pas de pagination, volume adapté à la
  démonstration).
- Pas d'authentification : voir la note de sécurité en fin de document.

## Endpoints

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

## Règles par ressource

**Clients** — requièrent `first_name`, `last_name`, `email`, `phone`,
`address`. Les emails sont normalisés en minuscules et portent un index unique.

**Repas** — requièrent `name`, `price`, `type` (`dish` ou `dessert`), `date`
(`YYYY-MM-DD`). `description` et `image_url` sont facultatifs ; `available` vaut
`true` par défaut. Le seed crée deux plats et deux desserts pour aujourd'hui.

**Livreurs** — requièrent `first_name`, `last_name`, `phone`. Le statut initial
est `available` ou `offline`. Les coordonnées sont facultatives mais doivent
être fournies ensemble (latitude entre -90 et 90, longitude entre -180 et 180).
Le statut `delivering` est réservé à l'affectation par une commande.

**Commandes** — requièrent un client existant et de 1 à 100 lignes distinctes,
chaque quantité entière entre 1 et 100. Tous les repas doivent être disponibles
**et datés d'aujourd'hui**. Les champs financiers éventuellement envoyés sont
ignorés : prix et totaux viennent exclusivement du serveur. La commande conserve
une copie du nom et du prix de chaque repas : modifier ou supprimer un repas
ensuite ne change pas l'historique de la commande.

## Codes de réponse

| Code | Signification |
| --- | --- |
| `200` | Lecture ou modification réussie |
| `201` | Création réussie |
| `204` | Suppression réussie |
| `400` | Validation, transition de statut invalide ou email dupliqué |
| `404` | Identifiant ou référence introuvable |
| `405` | Méthode non autorisée |
| `503` | MongoDB indisponible |

Les erreurs de validation indiquent les champs concernés ; les erreurs
générales utilisent la clé `detail` et ne révèlent jamais l'URI MongoDB.

## Affectation du livreur et machine à états

L'affectation réserve **atomiquement** le premier livreur disponible (dans
l'ordre des identifiants), puis insère la commande dans **la même transaction** :
un échec annule les deux opérations. Le champ interne `active_order_id` empêche
une commande ancienne de libérer un livreur déjà réaffecté.

- Avec livreur : commande `accepted`, livreur `delivering`.
- Sans livreur : commande `pending`, `delivery_driver_id` et estimation à `null`.
- `pending → accepted` retente l'affectation ; reste `pending` avec une erreur
  `400` si aucun livreur n'est disponible (pas de tâche automatique en arrière-plan).
- `pending → cancelled` est autorisé.
- `accepted → preparing / out_for_delivery / delivered / cancelled`.
- `preparing → out_for_delivery / delivered / cancelled`.
- `out_for_delivery → delivered / cancelled`.
- `delivered` et `cancelled` sont terminaux. Répéter le statut courant est sans effet.

La livraison **ou l'annulation** libère le livreur dans la transaction. Un
changement manuel ne peut pas rendre disponible ou mettre hors ligne un livreur
occupé. Le temps estimé est **simulé et fixe** (pas un compte à rebours) : `null`
sans livreur, `20` à l'affectation, `0` après livraison, `null` après annulation.

## Démonstration avec curl

Après le seed, récupérer les identifiants :

```bash
curl http://127.0.0.1:8000/api/clients/
curl http://127.0.0.1:8000/api/meals/today/
curl http://127.0.0.1:8000/api/delivery-drivers/available/
```

Remplacer `CLIENT_ID` et `MEAL_ID`, puis créer une commande :

```bash
curl -X POST http://127.0.0.1:8000/api/orders/ \
  -H 'Content-Type: application/json' \
  -d '{"client_id":"CLIENT_ID","items":[{"meal_id":"MEAL_ID","quantity":2}]}'
```

Deux plats à 12,99 € donnent un sous-total de `25.98`, des frais de `0.00`
(seuil de 19,99 € atteint) et un total de `25.98`. Un seul plat donne
`12.99 + 2.99 = 15.98`.

Avec l'identifiant de la commande retournée, suivre puis livrer :

```bash
curl http://127.0.0.1:8000/api/orders/ORDER_ID/status/
curl -X PATCH http://127.0.0.1:8000/api/orders/ORDER_ID/status/ \
  -H 'Content-Type: application/json' -d '{"status":"delivered"}'
curl http://127.0.0.1:8000/api/delivery-drivers/available/
```

Exemple de suivi sans livreur :

```json
{"order_id":"…","status":"pending","driver":null,"estimated_delivery_minutes":null}
```

Exemple avec livreur (coordonnées nulles tant qu'elles ne sont pas renseignées) :

```json
{"order_id":"…","status":"accepted","driver":{"id":"…","first_name":"Lucas","latitude":null,"longitude":null},"estimated_delivery_minutes":20}
```

## Sécurité

Cette API de démonstration **n'a ni authentification ni rôles** : toute personne
ayant accès au serveur peut lire et modifier les ressources. CORS limite les
appels des navigateurs mais ne constitue pas une authentification. Le suivi ne
retourne que le prénom et la position du livreur. Avant toute exposition
publique réelle : authentification, autorisations, HTTPS, et une politique de
conservation/suppression des données (voir [deploiement.md](deploiement.md)).

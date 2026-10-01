# Modèle de données — IPSSI Express Food

Documentation de la base MongoDB `express_food` (partie **Data & intégration**). Elle reflète
le code qui fait autorité : les index dans [`backend/common/db.py`](../backend/common/db.py),
les contrats d'entrée/sortie dans les `serializers.py` de chaque application et les règles
métier dans les `services.py`. En cas de doute, le code prime sur ce document.

Aucun ODM n'est utilisé : les documents sont des dictionnaires PyMongo. Il n'y a ni base SQL,
ni commande `migrate`. Les quatre collections sont créées et indexées par
`python manage.py init_db`.

## Conventions transverses

- **Identifiants** : l'`_id` MongoDB (`ObjectId`) est exposé dans l'API sous forme de chaîne `id`.
- **Montants** : calculés avec `Decimal`, **stockés et renvoyés en chaînes à deux décimales**
  (ex. `"19.99"`). Le serveur est la seule source de prix ; les montants envoyés par le client
  sont ignorés.
- **Dates** : la journée métier (`date` des repas) est une chaîne `YYYY-MM-DD` dans le fuseau
  `Europe/Paris`. Les horodatages (`created_at`, `updated_at`) sont des `datetime` en **UTC**.
- **Références** : les liens entre collections ne sont pas contraints par la base ; leur
  cohérence est vérifiée par `python manage.py verify_data` (voir plus bas).

## Collections

### `clients`

| Champ | Type | Règle |
| --- | --- | --- |
| `_id` | ObjectId | exposé en `id` |
| `first_name` | string | ≤ 100 |
| `last_name` | string | ≤ 100 |
| `email` | string | minuscule, **unique** |
| `phone` | string | `^\+?[0-9 .()-]{6,25}$` |
| `address` | string | ≤ 500 |
| `created_at` | datetime | UTC |

Index : `email` (unique). Supprimer un client **ne supprime pas** ses commandes : leur
`client_id` reste une référence historique.

### `meals`

| Champ | Type | Règle |
| --- | --- | --- |
| `_id` | ObjectId | exposé en `id` |
| `name` | string | ≤ 150 |
| `description` | string | ≤ 2000, facultatif (défaut `""`) |
| `price` | string décimal | > 0, deux décimales |
| `type` | string | `dish` ou `dessert` |
| `date` | string | `YYYY-MM-DD` (jour métier) |
| `image_url` | string URL | facultatif (défaut `""`) |
| `available` | bool | défaut `true` |
| `created_at` | datetime | UTC |

Index : `(date, available)` composé — sert la route « repas du jour ».

### `delivery_drivers`

| Champ | Type | Règle |
| --- | --- | --- |
| `_id` | ObjectId | exposé en `id` |
| `first_name` | string | ≤ 100 |
| `last_name` | string | ≤ 100 |
| `phone` | string | même regex que les clients |
| `status` | string | `available`, `delivering`, `offline` |
| `latitude` | float \| null | -90..90, fournie avec `longitude` |
| `longitude` | float \| null | -180..180, fournie avec `latitude` |
| `active_order_id` | string \| null | commande en cours (interne) |
| `created_at` / `updated_at` | datetime | UTC |

Index : `status`. Le statut `delivering` est réservé à l'affectation par une commande ; il
n'est jamais posé manuellement.

### `orders`

| Champ | Type | Règle |
| --- | --- | --- |
| `_id` | ObjectId | exposé en `id` |
| `client_id` | string | référence `clients._id` |
| `items` | array | 1 à 100 lignes distinctes |
| `items[].meal_id` | string | référence `meals._id` |
| `items[].name` | string | **copie** du nom au moment de la commande |
| `items[].quantity` | int | 1..100 |
| `items[].unit_price` | string décimal | copie du prix |
| `items[].subtotal` | string décimal | `unit_price × quantity` |
| `subtotal` | string décimal | somme des lignes |
| `delivery_fee` | string décimal | `0.00` si `subtotal` ≥ 19,99 €, sinon `2.99` |
| `total` | string décimal | `subtotal + delivery_fee` |
| `status` | string | voir machine à états |
| `delivery_driver_id` | string \| null | référence `delivery_drivers._id` |
| `estimated_delivery_minutes` | int \| null | `20` affectée, `0` livrée, `null` sinon |
| `created_at` / `updated_at` | datetime | UTC |

Index : `client_id`. La commande **copie** le nom et le prix de chaque repas : modifier ou
supprimer un repas ensuite ne change pas l'historique.

## Relations

```text
clients._id  <────  orders.client_id            (référence historique, non supprimée en cascade)
meals._id    <────  orders.items[].meal_id       (prix et nom copiés dans la commande)
delivery_drivers._id  <──>  orders.delivery_driver_id
delivery_drivers.active_order_id  ────>  orders._id   (réservation : évite de libérer un livreur réaffecté)
```

## Machine à états d'une commande

```text
pending ──> accepted | cancelled
accepted ──> preparing | out_for_delivery | delivered | cancelled
preparing ──> out_for_delivery | delivered | cancelled
out_for_delivery ──> delivered | cancelled
delivered  (terminal)
cancelled  (terminal)
```

L'affectation réserve atomiquement le premier livreur disponible puis insère la commande
dans **la même transaction** (nécessite un replica set / Atlas). La livraison ou l'annulation
libère le livreur dans la transaction.

## Invariants vérifiés par `verify_data`

`python manage.py verify_data` est en lecture seule et signale, le cas échéant :

1. `orders.client_id` qui ne pointe sur aucun client.
2. `orders.delivery_driver_id` qui ne pointe sur aucun livreur.
3. `total ≠ subtotal + delivery_fee`, ou une ligne dont `subtotal ≠ unit_price × quantity`,
   ou un `subtotal` de commande différent de la somme des lignes.
4. Un livreur `delivering` sans `active_order_id` (ou l'inverse), ou dont la commande active
   ne le référence pas en retour.
5. Un `email` client en double, un `type` de repas ou un `price` invalide.

Zéro anomalie signifie une base cohérente.

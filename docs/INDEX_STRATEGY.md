# Stratégie d'index MongoDB

Les index sont créés par :

```bash
cd backend
python manage.py init_db
```

La commande est idempotente : elle peut être relancée sans recréer les collections.

## Index par collection

| Collection | Index | But |
| --- | --- | --- |
| `clients` | `email` unique | empêcher les doublons d'email et accélérer la recherche |
| `meals` | `date + available` | charger efficacement le menu disponible du jour |
| `delivery_drivers` | `status` | trouver rapidement les livreurs disponibles |
| `delivery_drivers` | `active_order_id` | retrouver le livreur lié à une commande active |
| `orders` | `client_id` | afficher l'historique des commandes d'un client |
| `orders` | `status` | filtrer les commandes selon leur état |
| `orders` | `delivery_driver_id` | retrouver les commandes liées à un livreur |
| `orders` | `created_at` | faciliter les tris et recherches chronologiques |

## Pourquoi ne pas indexer tous les champs ?

Chaque index accélère certaines lectures mais ajoute un coût aux écritures et consomme de l'espace. Les index retenus correspondent donc aux accès réellement utiles au projet.

## Vérification

```bash
python manage.py init_db
python manage.py db_status
```

`db_status` affiche les index présents collection par collection sans révéler de données personnelles.

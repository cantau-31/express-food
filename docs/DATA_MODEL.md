# Modèle de données MongoDB

Le backend utilise quatre collections métier dans la base `express_food`.

## `clients`

Exemple :

```json
{
  "_id": "ObjectId",
  "first_name": "Rayen",
  "last_name": "Demo",
  "email": "rayen@example.com",
  "phone": "0600000000",
  "address": "10 rue de la Démo, Toulouse",
  "created_at": "DateTime"
}
```

Index :
- `email` unique.

## `meals`

Exemple :

```json
{
  "_id": "ObjectId",
  "name": "Poulet et riz",
  "description": "Menu de démonstration",
  "price": "12.99",
  "type": "dish",
  "date": "YYYY-MM-DD",
  "image_url": "",
  "available": true,
  "created_at": "DateTime"
}
```

Contraintes applicatives :
- `type` : `dish` ou `dessert` ;
- prix positif à deux décimales ;
- seules les entrées disponibles et datées du jour sont commandables.

Index :
- `(date, available)`.

## `delivery_drivers`

Exemple :

```json
{
  "_id": "ObjectId",
  "first_name": "Lucas",
  "last_name": "Demo",
  "phone": "0600000001",
  "status": "available",
  "latitude": 43.6045,
  "longitude": 1.444,
  "active_order_id": null,
  "created_at": "DateTime",
  "updated_at": "DateTime"
}
```

Statuts :
- `available`
- `delivering`
- `offline`

Règles :
- latitude et longitude sont fournies ensemble ;
- un livreur ne peut passer à `delivering` que par attribution d'une commande ;
- un livreur occupé ne peut être libéré manuellement avant livraison/annulation.

Index :
- `status` ;
- `active_order_id` pour retrouver rapidement le livreur lié à une commande active.

## `orders`

Exemple :

```json
{
  "_id": "ObjectId",
  "client_id": "ObjectId sous forme de chaîne",
  "items": [
    {
      "meal_id": "ObjectId sous forme de chaîne",
      "name": "Poulet et riz",
      "quantity": 2,
      "unit_price": "12.99",
      "subtotal": "25.98"
    }
  ],
  "subtotal": "25.98",
  "delivery_fee": "0.00",
  "total": "25.98",
  "status": "accepted",
  "delivery_driver_id": "ObjectId sous forme de chaîne",
  "estimated_delivery_minutes": 20,
  "created_at": "DateTime",
  "updated_at": "DateTime"
}
```

Règles principales :
- les prix sont recalculés côté serveur ;
- livraison gratuite pour un sous-total `>= 19.99` ;
- l'affectation du livreur et l'insertion de la commande sont effectuées dans une même transaction ;
- le nom et le prix du repas sont copiés dans la commande pour préserver l'historique.

Index :
- `client_id` ;
- `status` ;
- `delivery_driver_id` ;
- `created_at`.

Ces index couvrent les principales recherches de suivi, d’historique et de diagnostic.

## Relations logiques

```text
clients
   │ 1
   │
   └──< orders >──┐
                  │
                  ├── meals (références + snapshot nom/prix)
                  │
                  └── delivery_drivers (0 ou 1 livreur affecté)
```

MongoDB reste volontairement dénormalisé sur les lignes de commande : la commande conserve un snapshot du nom et du prix du repas au moment de l'achat.

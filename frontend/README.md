# Express Food — Frontend React

Frontend réalisé par **Rayen** pour IPSSI Express Food.

## Fonctionnalités

- menu du jour depuis l'API Django ;
- panier persistant dans le navigateur ;
- calcul visuel du sous-total et de la livraison offerte dès 19,99 € ;
- sélection d'un client existant ou création d'un nouveau client ;
- création de commande via l'API ;
- redirection immédiate vers le suivi de livraison ;
- suivi du statut, du livreur et du temps estimé ;
- affichage de la flotte et du statut des livreurs ;
- interface responsive desktop / mobile ;
- URLs explicites via React Router.

## Installation

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Le frontend démarre par défaut sur :

```text
http://localhost:5173
```

Le backend Django doit être disponible sur :

```text
http://127.0.0.1:8000
```

La variable `VITE_API_BASE_URL` permet de changer l'URL de l'API.

## Routes

- `/` — accueil
- `/menu` — menu du jour
- `/cart` — panier
- `/checkout` — finalisation de commande
- `/tracking` — recherche d'une commande
- `/tracking/:id` — suivi détaillé
- `/drivers` — affichage des livreurs

## Rôle de Rayen

Rayen est responsable du frontend React : UI, responsive, intégration avec l'API Django, affichage des données de commande/livraison et préparation du déploiement frontend.


## Tests frontend

Les règles de calcul du panier sont couvertes par des tests automatisés :

```bash
cd frontend
npm test
```

Les tests vérifient notamment :
- le calcul du sous-total ;
- les frais de livraison sous le seuil ;
- la livraison gratuite exactement à **19,99 €** ;
- le comportement d'un panier vide.

Le workflow GitHub Actions exécute désormais les tests avant le build Vite.

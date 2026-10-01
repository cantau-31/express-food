# Déploiement du frontend — Rayen

Le frontend React/Vite est prêt à être déployé sur Vercel.

## Configuration du projet Vercel

Paramètres recommandés :

- **Framework Preset** : Vite
- **Root Directory** : `frontend`
- **Build Command** : `npm run build`
- **Output Directory** : `dist`
- **Install Command** : `npm install`

Le fichier `vercel.json` présent dans `frontend/` gère le fallback SPA pour React Router.

## Variable d'environnement obligatoire

Configurer sur Vercel :

```text
VITE_API_BASE_URL=https://URL-PUBLIQUE-DU-BACKEND/api
```

Ne pas utiliser `http://127.0.0.1:8000/api` en production : cette adresse ne fonctionne que sur le poste local.

## CORS côté backend

Le backend Django doit autoriser l'URL publique du frontend dans `CORS_ALLOWED_ORIGINS`.

Exemple :

```text
CORS_ALLOWED_ORIGINS=https://express-food.vercel.app
```

Cette configuration relève du backend.

## Vérifications après déploiement

Tester dans cet ordre :

1. ouvrir la page d'accueil ;
2. ouvrir `/menu` directement dans le navigateur ;
3. recharger `/menu` pour vérifier le fallback SPA ;
4. vérifier le chargement du menu du jour depuis Django ;
5. ajouter un repas au panier ;
6. vérifier le calcul des frais de livraison ;
7. sélectionner ou créer un client ;
8. créer une commande ;
9. vérifier la redirection vers `/tracking/:id` ;
10. vérifier le statut, le livreur, l'ETA et le récapitulatif ;
11. ouvrir `/drivers` ;
12. ouvrir `/admin` et tester les écrans de gestion.

## Validation finale

Le frontend est considéré comme terminé lorsque :

- l'URL publique est accessible ;
- les routes React fonctionnent après rafraîchissement ;
- l'API publique Django est joignable ;
- aucune erreur CORS n'apparaît dans le navigateur ;
- le parcours menu → panier → commande → suivi fonctionne ;
- l'URL publique du frontend est ajoutée au README du projet.

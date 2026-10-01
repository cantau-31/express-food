# Déploiement & opérations data — IPSSI Express Food

Guide de la partie **Data & intégration** : mise en production du backend, intégration continue
et opérations sur les données (sauvegarde, restauration, contrôle d'intégrité).

L'application a deux services déployés séparément :

- **Backend** Django REST Framework → **Render** (sections 1 à 3).
- **Frontend** React/Vite → **Vercel** (section 4).

Le lien entre les deux (URL d'API et CORS) est décrit dans [integration.md](integration.md).

Le backend lit toute sa configuration depuis l'environnement (voir
[`backend/.env.example`](../backend/.env.example)). Aucun secret n'est écrit dans le dépôt :
le vrai `.env` et les sauvegardes sont ignorés par Git.

## Variables d'environnement (backend)

| Variable | Rôle | En production |
| --- | --- | --- |
| `DJANGO_SECRET_KEY` | secret Django (obligatoire) | valeur longue aléatoire, générée par la plateforme |
| `DEBUG` | mode debug | **`False`** |
| `ALLOWED_HOSTS` | hôtes autorisés | l'hôte public (ex. `ipssi-express-food-api.onrender.com`) |
| `CORS_ALLOWED_ORIGINS` | origines navigateur autorisées | l'URL **exacte** du frontend Vercel |
| `MONGODB_URI` | URI Atlas (secret) | saisie dans le dashboard, jamais commitée |
| `MONGODB_DATABASE` | base | `express_food` |
| `FREE_DELIVERY_THRESHOLD` / `DEFAULT_DELIVERY_FEE` / `DEFAULT_DELIVERY_ESTIMATE` | règles métier | `19.99` / `2.99` / `20` |

## 1. MongoDB Atlas (base de production)

1. Créer un projet et un cluster (le niveau gratuit M0 suffit pour la démonstration).
2. **Database Access** : créer un utilisateur avec le rôle `readWrite` sur `express_food`.
3. **Network Access** : autoriser les IP de la plateforme d'hébergement. Sur Render (plan
   gratuit, IP sortantes variables), autoriser `0.0.0.0/0` **uniquement** avec des données
   fictives ; pour un vrai déploiement, restreindre aux IP sortantes de la plateforme.
4. **Connect → Drivers → Python** : copier l'URI `mongodb+srv://…` dans `MONGODB_URI`
   (encoder les caractères spéciaux du mot de passe).

## 2. Déploiement backend sur Render

Le fichier [`render.yaml`](../render.yaml) décrit le service (Infrastructure as Code).

1. Pousser le dépôt sur GitHub.
2. Render → **New → Blueprint** → sélectionner le dépôt. Render lit `render.yaml`.
3. Renseigner dans le dashboard les variables marquées `sync: false` :
   `MONGODB_URI`, `ALLOWED_HOSTS` (l'hôte `.onrender.com` attribué) et
   `CORS_ALLOWED_ORIGINS` (l'URL Vercel du frontend). `DJANGO_SECRET_KEY` est généré
   automatiquement.
4. Au premier déploiement, créer les index via **Shell** du service :

   ```bash
   python manage.py init_db
   # facultatif, données de démonstration :
   python manage.py seed_data
   ```

Build : `pip install -r requirements-prod.txt` ; démarrage : `gunicorn config.wsgi:application`.
Le `healthCheckPath` interroge `/api/meals/today/`.

> La racine du dépôt Git doit être le dossier qui contient `backend/` et `frontend/` (là où se
> trouvent `render.yaml` et `.github/`). Le `rootDir: backend` du blueprint pointe vers l'API.

## 3. Déploiement backend par conteneur (alternative)

Un [`Dockerfile`](../backend/Dockerfile) est fourni (contexte de build : `backend/`).

```bash
cd backend
docker build -t ipssi-express-food-api .
docker run --rm -p 8000:8000 --env-file .env ipssi-express-food-api
```

L'image lance `gunicorn` sur le port 8000. Fournir `DJANGO_SECRET_KEY` et `MONGODB_URI`
par l'environnement (`--env-file` ou variables).

## 4. Déploiement frontend sur Vercel

Le frontend React/Vite se déploie sur **Vercel**. La procédure détaillée
(réglages du projet, variable `VITE_API_BASE_URL`, fallback SPA via `vercel.json`
et vérifications post-déploiement) est documentée dans
[`frontend/DEPLOYMENT.md`](../frontend/DEPLOYMENT.md).

Point d'intégration à ne pas manquer : `VITE_API_BASE_URL` (frontend) doit
pointer vers l'URL publique du backend, et `CORS_ALLOWED_ORIGINS` (backend) doit
contenir l'URL Vercel **exacte** du frontend (voir [integration.md](integration.md)).

## 5. Intégration continue (GitHub Actions)

Deux workflows coexistent, filtrés par chemin pour ne pas se déclencher inutilement :

- [`.github/workflows/backend-ci.yml`](../.github/workflows/backend-ci.yml) (Rima) — sur
  changement dans `backend/**` : versions figées (`requirements-lock.txt`), `manage.py check`,
  puis toute la suite de tests avec `--settings=config.test_settings`. Tests `mongomock`,
  **aucun compte Atlas requis**, donc aucun secret dans la CI.
- [`.github/workflows/frontend-build.yml`](../.github/workflows/frontend-build.yml) (Rayen) —
  sur changement dans `frontend/**` : installation, tests puis build React.

## 6. Opérations sur les données

Trois commandes de gestion (dossier `backend/`, `.env` configuré pour la base visée) :

```bash
# Sauvegarde : exporte les 4 collections en JSON (défaut : backups/express_food_<horodatage>.json)
python manage.py backup_data
python manage.py backup_data --output chemin/vers/sauvegarde.json

# Restauration : remplace les collections par le contenu du fichier (--keep pour ajouter sans vider)
python manage.py restore_data --input chemin/vers/sauvegarde.json

# Contrôle d'intégrité (lecture seule) : références, montants, cohérence livreur/commande
python manage.py verify_data
```

Le format d'export est le JSON étendu MongoDB (`bson.json_util`) : il préserve les `ObjectId`
et les `datetime` lors d'un aller-retour. `restore_data` recrée ensuite les index.

> **RGPD** : les sauvegardes contiennent des données personnelles clients. Le dossier
> `backend/backups/` est ignoré par Git — ne jamais committer ni partager ces fichiers,
> et les conserver dans un emplacement sécurisé avec une durée de rétention limitée.

## 7. Check-list avant mise en production

- [ ] `DEBUG=False`.
- [ ] `ALLOWED_HOSTS` et `CORS_ALLOWED_ORIGINS` explicites (pas de valeur de développement).
- [ ] `CORS_ALLOWED_ORIGINS` = l'URL Vercel réelle, et `VITE_API_BASE_URL` (frontend) = l'URL Render réelle.
- [ ] `DJANGO_SECRET_KEY` long et secret, hors du dépôt.
- [ ] Atlas : utilisateur `readWrite` dédié, accès réseau restreint.
- [ ] `init_db` exécuté une fois (index, dont l'unicité des emails).
- [ ] HTTPS assuré par les plateformes (Render et Vercel le fournissent).
- [ ] `verify_data` sans anomalie, sauvegarde récente disponible.

> **Rappel sécurité** : cette API de démonstration n'a ni authentification ni rôles. Avant
> une exposition publique réelle, ajouter authentification, autorisations, et une politique
> de conservation/suppression des données.

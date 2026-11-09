# Site vitrine : produits digitaux + appli Sève

Site statique (HTML/CSS, sans framework) qui présente les produits digitaux et redirige vers Etsy pour l'achat, avec une section dédiée à l'appli **Sève**.

- `products.json` : **le seul fichier à modifier** (nom du site, liens Etsy, produits, appli).
- `build.py` : génère les pages dans `public/` (Python 3, aucune dépendance).
- `public/` : le site prêt à mettre en ligne (`style.css`, `main.js`, polices, images).

## Voir le site en local

```bash
python3 build.py
```

```bash
python3 -m http.server 8000 --directory public
```

Puis ouvrir http://localhost:8000.

## À remplir avant la mise en ligne

Dans `products.json` :

| Champ | Quoi mettre |
| --- | --- |
| `site.name` | Nom de la boutique (« A Studio & Cie », boutique Etsy AStudioCie) |
| `site.etsy_shop_url` | Lien de la boutique Etsy (ex. `https://www.etsy.com/shop/MaBoutique`) |
| `site.url` | Adresse du site une fois en ligne (pour le référencement) |
| `site.contact_email` | E-mail de contact affiché en pied de page (facultatif) |
| `products[].versions` | Une ligne par version vendue (ex. numérique, imprimée) : `name`, `detail`, `price` (vide = « Voir le prix »), `etsy_url` |
| `apps[].store_url` | Lien Google Play de Sève quand elle sera publiée |

Tant qu'un lien est vide, le bouton affiche « Bientôt sur Etsy » / « Bientôt sur Google Play ».

## Ajouter le produit de la semaine

1. Créer `public/img/<slug>/` et y mettre les visuels Etsy (format 4:3 conseillé, ~1600 px de large, JPG).
2. Copier le bloc d'un produit dans `products.json`, changer `slug`, `week` (numéro de semaine), `title`, `price`, `versions` (avec les liens Etsy), `images`, textes.
3. Lancer `python3 build.py`.

Le dernier produit (plus grand numéro de semaine) devient automatiquement la « Nouveauté » de l'accueil, la frise « Un produit par semaine » et le compte à rebours se mettent à jour.

## Mise en ligne

**GitHub Pages (automatique)** : le workflow `.github/workflows/pages.yml` reconstruit et publie le site à chaque modification sur `main`. À activer une fois : dépôt GitHub → *Settings* → *Pages* → *Source* : **GitHub Actions**.

**Alternative** : glisser le dossier `public` sur https://app.netlify.com/drop.

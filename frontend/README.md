# Frontend Citoyen - Climate AI Collective

Interface web simple permettant aux citoyens de consulter les propositions climatiques et de voter.

## Fonctionnalités

- **Liste des propositions** : Affichage de toutes les propositions avec filtres par domaine et statut
- **Détails des propositions** : Visualisation complète des propositions (actions, impact, budget, validation, simulation)
- **Système de vote** : Vote sur 3 axes (impact, faisabilité, désirabilité) avec échelle de 1 à 10
- **Statistiques en temps réel** : Résumé des votes agrégés pour chaque proposition

## Prérequis

- L'API doit être lancée sur http://localhost:8002
- Un navigateur web moderne (Chrome, Firefox, Safari, Edge)

## Installation

Aucune installation n'est nécessaire. Il s'agit d'une application web statique (HTML/CSS/JavaScript vanilla).

## Lancement

### Option 1 : Serveur HTTP simple avec Python

```bash
cd frontend

# Python 3
python -m http.server 8080

# Ou Python 2
python -m SimpleHTTPServer 8080
```

Accédez à http://localhost:8080

### Option 2 : Serveur HTTP avec Node.js

```bash
cd frontend

# Installer http-server globalement
npm install -g http-server

# Lancer le serveur
http-server -p 8080
```

Accédez à http://localhost:8080

### Option 3 : Ouvrir directement dans le navigateur

Vous pouvez ouvrir `index.html` directement dans votre navigateur, mais certaines fonctionnalités (comme CORS) peuvent ne pas fonctionner correctement.

## Structure des fichiers

```
frontend/
├── index.html         # Page principale (liste des propositions)
├── proposal.html      # Page de détail d'une proposition
├── styles.css         # Styles CSS
├── app.js            # JavaScript pour la page principale
├── proposal.js       # JavaScript pour la page de détail
└── README.md         # Ce fichier
```

## Utilisation

### Consulter les propositions

1. Ouvrez http://localhost:8080
2. Vous verrez la liste de toutes les propositions
3. Utilisez les filtres pour affiner votre recherche :
   - Filtrer par domaine (Transport, Énergie, etc.)
   - Filtrer par statut (Générée, Validée, etc.)
4. Cliquez sur une proposition pour voir les détails

### Voter sur une proposition

1. Cliquez sur une proposition dans la liste
2. Lisez attentivement les détails de la proposition
3. Descendez jusqu'à la section "Votez sur cette proposition"
4. Évaluez la proposition sur 3 axes (1-10) :
   - **Impact climatique** : Potentiel de réduction des émissions
   - **Faisabilité** : Facilité de mise en œuvre
   - **Désirabilité sociale** : Acceptabilité et bénéfices
5. Ajoutez un commentaire optionnel
6. Cliquez sur "Envoyer mon vote"
7. Votre vote est enregistré et les statistiques sont mises à jour

### Voir les résultats des votes

Les résultats des votes sont affichés :
- Dans la liste des propositions (note globale moyenne)
- Sur la page de détail (résumé complet avec moyennes par axe)

## Configuration de l'API

L'URL de l'API est configurée au début des fichiers JavaScript :

```javascript
const API_BASE_URL = 'http://localhost:8002';
```

Si votre API est hébergée ailleurs, modifiez cette valeur dans :
- `app.js` (ligne 2)
- `proposal.js` (ligne 2)

## Fonctionnalités avancées (à venir)

- Authentification des citoyens
- Système de commentaires
- Partage sur les réseaux sociaux
- Export des propositions en PDF
- Graphiques interactifs pour les simulations
- Notifications en temps réel
- Mode sombre

## Compatibilité navigateurs

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Opera 76+

## Contribution

Ce frontend est conçu pour être simple et facilement extensible. Les contributions sont les bienvenues pour :
- Améliorer l'UX/UI
- Ajouter des visualisations de données
- Optimiser les performances
- Améliorer l'accessibilité

## Licence

Open-source - Voir le fichier LICENSE du projet principal

# 🏦 Chatbot Bancaire avec Hugging Face

Un chatbot bancaire intelligent spécialisé dans la simulation et la demande de crédit, utilisant les technologies Hugging Face pour la compréhension du langage naturel.

## 🚀 Fonctionnalités

- **🤖 Classification d'intents** avec DistilBERT
- **🔍 Extraction d'entités** avec BERT-NER
- **💰 Calculs financiers** précis (mensualités, TAEG, assurance)
- **📊 Simulations de crédit** en temps réel
- **💬 Interface conviviale** (Streamlit et Flask)
- **🎯 Ton professionnel** de conseiller bancaire

## 📋 Prérequis

- Python 3.8+
- 4GB RAM minimum (8GB recommandé)
- Connexion internet pour télécharger les modèles

## 🔧 Installation

### 1. Cloner le projet
```bash
git clone <url-du-repo>
cd chatbot-bancaire
```

### 2. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 3. Vérifier l'installation
```bash
python -c "import torch; print('PyTorch version:', torch.__version__)"
python -c "import transformers; print('Transformers version:', transformers.__version__)"
```

## 🎯 Utilisation

### Option 1 : Interface Streamlit (Recommandée)

```bash
streamlit run app_streamlit.py
```

L'interface sera disponible sur : http://localhost:8501

### Option 2 : Interface Flask

```bash
python app_flask.py
```

L'interface sera disponible sur : http://localhost:5000

### Option 3 : Test en ligne de commande

```bash
python chatbot_bancaire.py
```

## 📊 Exemples d'utilisation

### Simulations de crédit
```
👤 "Je voudrais simuler un crédit personnel de 50 000€ sur 5 ans"
🤖 [Simulation détaillée avec mensualités, coûts, TAEG]

👤 "Simulation prêt immobilier 200 000€ sur 20 ans avec assurance"
🤖 [Simulation avec assurance emprunteur incluse]
```

### Informations sur les produits
```
👤 "Qu'est-ce qu'un crédit immobilier ?"
🤖 [Description complète avec caractéristiques et avantages]

👤 "Quels sont les taux d'intérêt ?"
🤖 [Liste des taux par type de crédit]
```

### Demandes de crédit
```
👤 "Je veux faire une demande de crédit"
🤖 [Étapes détaillées et documents nécessaires]
```

## 🏗️ Architecture

```
📁 chatbot-bancaire/
├── 📄 requirements.txt              # Dépendances Python
├── 📄 dataset_bancaire.json         # Dataset d'entraînement
├── 📄 intent_classifier.py          # Classification d'intents
├── 📄 entity_extractor.py           # Extraction d'entités
├── 📄 credit_calculator.py          # Calculs financiers
├── 📄 chatbot_bancaire.py           # Chatbot principal
├── 📄 app_streamlit.py              # Interface Streamlit
├── 📄 app_flask.py                  # Interface Flask
└── 📁 intent_model/                 # Modèles entraînés
```

## 🧠 Modèles utilisés

### Classification d'intents
- **Modèle de base** : `distilbert-base-uncased`
- **Intents supportés** :
  - `simulation_credit` - Simulation de crédit
  - `demande_credit` - Demande de crédit
  - `information_produit` - Informations produits
  - `calcul_financier` - Calculs financiers
  - `support_client` - Support client
  - `modification_simulation` - Modification simulation

### Extraction d'entités
- **Modèle NER** : `dslim/bert-base-NER`
- **Entités extraites** :
  - `montant` - Montant du crédit (1000€ - 1500000€)
  - `duree` - Durée en années (1-25 ans)
  - `type_credit` - Type de crédit
  - `taux_interet` - Taux d'intérêt
  - `assurance` - Préférence assurance
  - `revenus` - Revenus mensuels

## 💰 Taux d'intérêt (fictifs mais réalistes)

| Type de Crédit | Taux Minimum | Taux Maximum | Taux Défaut |
|----------------|--------------|--------------|-------------|
| Personnel | 4.5% | 7.2% | 5.8% |
| Immobilier | 2.8% | 4.1% | 3.2% |
| Automobile | 3.2% | 5.8% | 4.2% |
| Travaux | 5.1% | 8.3% | 6.5% |

## 🔧 Configuration avancée

### Entraînement personnalisé

```python
from intent_classifier import IntentClassifier

# Créer un nouveau classifieur
classifier = IntentClassifier()

# Entraîner avec votre dataset
classifier.train(dataset_path="mon_dataset.json", output_dir="./mon_modele")

# Charger le modèle entraîné
classifier.load_trained_model("./mon_modele")
```

### Ajout de nouveaux types de crédit

```python
# Dans credit_calculator.py
self.rates['nouveau_type'] = {
    'min': 3.0,
    'max': 6.0,
    'default': 4.5
}
```

## 📈 Performance

### Métriques typiques
- **Précision classification** : 85-95%
- **Temps de réponse** : < 2 secondes
- **Précision extraction entités** : 90-95%

### Optimisations
- Modèles pré-entraînés pour un démarrage rapide
- Cache des calculs financiers
- Validation des entrées utilisateur

## 🛠️ Développement

### Structure du code
```python
# Exemple d'utilisation programmatique
from chatbot_bancaire import ChatbotBancaire

chatbot = ChatbotBancaire()
chatbot.load_models()

# Traitement d'un message
result = chatbot.process_message("Simuler crédit 50 000€ sur 5 ans")
print(f"Intent: {result['intent']}")
print(f"Entités: {result['entities']}")
print(f"Réponse: {result['response']}")
```

### Tests
```bash
# Test du classifieur
python intent_classifier.py

# Test de l'extracteur
python entity_extractor.py

# Test du calculateur
python credit_calculator.py

# Test complet du chatbot
python chatbot_bancaire.py
```

## 🚀 Déploiement

### Déploiement local
```bash
# Avec Docker
docker build -t chatbot-bancaire .
docker run -p 8501:8501 chatbot-bancaire

# Avec Python
python app_streamlit.py
```

### Déploiement cloud
- **Heroku** : Compatible avec les fichiers `requirements.txt`
- **AWS/GCP** : Utiliser les instances avec GPU pour de meilleures performances
- **Azure** : Déploiement via Azure App Service

## 🔒 Sécurité

- Validation des entrées utilisateur
- Limitation des montants de crédit
- Pas de stockage de données personnelles
- Logs d'audit pour le debugging

## 📝 Logs et monitoring

```python
# Activation des logs détaillés
import logging
logging.basicConfig(level=logging.INFO)

# Monitoring des performances
chatbot.get_conversation_summary(user_id)
```

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Commit les changements (`git commit -am 'Ajout nouvelle fonctionnalité'`)
4. Push vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Créer une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🆘 Support

### Problèmes courants

**Erreur : "CUDA out of memory"**
```bash
# Solution : Utiliser CPU uniquement
export CUDA_VISIBLE_DEVICES=""
python app_streamlit.py
```

**Erreur : "Model not found"**
```bash
# Solution : Réentraîner le modèle
python intent_classifier.py
```

**Erreur : "Port already in use"**
```bash
# Solution : Changer le port
streamlit run app_streamlit.py --server.port 8502
```



---

**🏦 Chatbot Bancaire** - Votre assistant intelligent pour tous vos projets de crédit ! 

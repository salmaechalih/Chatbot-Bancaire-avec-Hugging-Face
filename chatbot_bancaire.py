import json
import time
from typing import Dict, Any, Optional
from intent_classifier import IntentClassifier
from entity_extractor import EntityExtractor
from credit_calculator import CreditCalculator
from simple_intent_classifier import SimpleIntentClassifier

class ChatbotBancaire:
    def __init__(self):
        """
        Initialise le chatbot bancaire avec tous ses composants
        """
        print("🏦 Initialisation du Chatbot Bancaire...")
        
        # Initialisation des composants
        self.intent_classifier = IntentClassifier()
        self.simple_classifier = SimpleIntentClassifier()  # Classificateur de secours
        self.entity_extractor = EntityExtractor()
        self.credit_calculator = CreditCalculator(10000,20,3.5)
        self.use_simple_classifier = False  # Flag pour basculer vers le classificateur simple
        
        # Contexte de conversation
        self.conversation_context = {}
        
        # Réponses types pour chaque intent
        self.responses = {
            'simulation_credit': {
                'default': "Je vais vous aider à simuler votre crédit. Pour cela, j'ai besoin de quelques informations : quel montant souhaitez-vous emprunter et sur quelle durée ?",
                'with_params': "Parfait ! Je vais faire votre simulation de crédit."
            },
            'demande_credit': {
                'default': "Parfait ! Je vais vous accompagner dans votre demande de crédit. Voici les étapes à suivre :"
            },
            'information_produit': {
                'default': "Je vais vous expliquer nos produits de crédit. Que souhaitez-vous savoir ?"
            },
            'calcul_financier': {
                'default': "Je vais vous aider avec vos calculs financiers. Que voulez-vous calculer ?"
            },
            'support_client': {
                'default': "Je suis là pour vous aider ! Comment puis-je vous assister ?"
            },
            'modification_simulation': {
                'default': "Je vais modifier votre simulation avec les nouveaux paramètres."
            }
        }
        
        # Informations sur les produits
        self.product_info = {
            'personnel': {
                'name': 'Crédit Personnel',
                'description': 'Un crédit flexible pour tous vos projets personnels',
                'features': ['Montant : 1 000€ à 75 000€', 'Durée : 12 à 84 mois', 'Taux : 4.5% à 7.2%'],
                'advantages': ['Usage libre', 'Délai de réponse rapide', 'Assurance optionnelle']
            },
            'immobilier': {
                'name': 'Crédit Immobilier',
                'description': 'Le financement idéal pour votre projet immobilier',
                'features': ['Montant : 50 000€ à 1 500 000€', 'Durée : 7 à 25 ans', 'Taux : 2.8% à 4.1%'],
                'advantages': ['Taux avantageux', 'Durée longue possible', 'Assurance obligatoire incluse']
            },
            'automobile': {
                'name': 'Crédit Automobile',
                'description': 'Financez votre véhicule en toute simplicité',
                'features': ['Montant : 5 000€ à 100 000€', 'Durée : 12 à 84 mois', 'Taux : 3.2% à 5.8%'],
                'advantages': ['Taux compétitifs', 'Délai de réponse rapide', 'Financement 100% possible']
            },
            'travaux': {
                'name': 'Crédit Travaux',
                'description': 'Réalisez vos travaux de rénovation',
                'features': ['Montant : 3 000€ à 50 000€', 'Durée : 12 à 60 mois', 'Taux : 5.1% à 8.3%'],
                'advantages': ['Financement des travaux', 'Devis obligatoire', 'Assurance optionnelle']
            }
        }
        
        print("✅ Chatbot Bancaire initialisé avec succès !")
    
    def load_models(self, intent_model_path: str = "./intent_model") -> bool:
        """
        Charge les modèles entraînés avec fallback vers le classificateur simple
        """
        print("🔄 Chargement des modèles...")
        
        # Tentative de chargement du modèle d'intent avancé
        try:
            intent_loaded = self.intent_classifier.load_trained_model(intent_model_path)
            
            if not intent_loaded:
                print("⚠️  Modèle d'intent non trouvé. Entraînement en cours...")
                self.intent_classifier.train()
                intent_loaded = True
                
            if intent_loaded:
                print("✅ Modèle d'intent avancé chargé !")
                self.use_simple_classifier = False
                
        except Exception as e:
            print(f"⚠️  Erreur avec le modèle avancé : {e}")
            print("🔄 Basculement vers le classificateur simple...")
            self.use_simple_classifier = True
        
        if self.use_simple_classifier:
            print("✅ Classificateur simple activé !")
        
        print("✅ Modèles chargés avec succès !")
        return True
    
    def process_message(self, message: str, user_id: str = "default") -> Dict[str, Any]:
        """
        Traite un message utilisateur et retourne la réponse
        """
        print(f"\n👤 Utilisateur ({user_id}): {message}")
        
        # Initialisation du contexte utilisateur si nécessaire
        if user_id not in self.conversation_context:
            self.conversation_context[user_id] = {
                'last_intent': None,
                'last_entities': {},
                'simulation_history': [],
                'conversation_count': 0
            }
        
        context = self.conversation_context[user_id]
        context['conversation_count'] += 1
        
        # Classification de l'intent avec fallback
        if self.use_simple_classifier:
            # Utilisation du classificateur simple
            simple_result = self.simple_classifier.predict(message)
            intent = simple_result['intent']
            confidence = simple_result['confidence']
            entities = simple_result['entities']
            entity_confidence = confidence  # Même confiance pour les entités simples
        else:
            # Tentative avec le modèle avancé
            try:
                intent_result = self.intent_classifier.predict_intent_with_confidence(message)
                intent = intent_result['intent']
                confidence = intent_result['confidence']
            except Exception as e:
                print(f"❌ Erreur lors de la classification d'intent : {e}")
                print("🔄 Basculement vers le classificateur simple...")
                self.use_simple_classifier = True
                simple_result = self.simple_classifier.predict(message)
                intent = simple_result['intent']
                confidence = simple_result['confidence']
                entities = simple_result['entities']
                entity_confidence = confidence
            
            # Extraction des entités (seulement si modèle avancé fonctionne)
            if not self.use_simple_classifier:
                try:
                    entity_result = self.entity_extractor.extract_entities_with_validation(message)
                    entities = entity_result['validated_entities']
                    entity_confidence = entity_result['confidence']
                except Exception as e:
                    print(f"❌ Erreur lors de l'extraction d'entités : {e}")
                    # Fallback vers l'extraction simple
                    entities = self.simple_classifier.extract_entities(message)
                    entity_confidence = 0.5
        
        # Mise à jour du contexte
        context['last_intent'] = intent
        context['last_entities'] = entities
        
        # Génération de la réponse
        response = self.generate_response(intent, entities, context, confidence, entity_confidence,user_id)
        
        # Sauvegarde de la simulation si applicable
        if intent == 'simulation_credit' and entities:
            self.save_simulation(user_id, entities, response)
        
        result = {
            'intent': intent,
            'confidence': confidence,
            'entities': entities,
            'entity_confidence': entity_confidence,
            'response': response,
            'context': context
        }
        
        print(f"🤖 Chatbot: {response}")
        return result
    
    def generate_response(self, intent: str, entities: Dict[str, Any], context: Dict[str, Any], 
                         intent_confidence: float, entity_confidence: float, user_id: str) -> str:
        """
        Génère une réponse adaptée selon l'intent et les entités
        """
        # Vérification de la confiance (seuil adapté selon le classificateur utilisé)
        confidence_threshold = 0.1 if self.use_simple_classifier else 0.5
        if intent_confidence < confidence_threshold:
            return "Je ne suis pas sûr de bien comprendre votre demande. Pouvez-vous reformuler ?"
        
        if intent == 'simulation_credit':
            return self.generate_simulation_response(user_id,entities, context)
        
        elif intent == 'demande_credit':
            return self.generate_credit_request_response(entities, context)
        
        elif intent == 'information_produit':
            return self.generate_product_info_response(entities, context)
        
        elif intent == 'calcul_financier':
            return self.generate_financial_calc_response(entities, context)
        
        elif intent == 'support_client':
            return self.generate_support_response(entities, context)
        
        elif intent == 'modification_simulation':
            return self.generate_modification_response(entities, context)
        
        else:
            return "Je ne comprends pas votre demande. Pouvez-vous reformuler ?"
    
    def generate_simulation_response(self,user_id: str, entities: Dict[str, Any], context: Dict[str, Any]) -> str:
        """
        Génère une réponse pour une simulation de crédit
        """
        # Vérification des paramètres nécessaires
        required_params = ['montant', 'duree']
        missing_params = [param for param in required_params if param not in entities]
        
        if missing_params:
            return f"Pour faire votre simulation, il me manque : {', '.join(missing_params)}. Pouvez-vous me les préciser ?"
        
        # Récupération des paramètres avec conversion
        try:
            montant = int(entities['montant'])
            duree = int(entities['duree'])
        except (ValueError, TypeError):
            return "❌ Erreur : montant et durée doivent être des nombres."
        
        credit_type = entities.get('type_credit', 'personnel')
        with_insurance = entities.get('assurance', False)
        
        try:
            # Calcul de la simulation
            simulation = self.credit_calculator.simulate_credit(
                capital=montant,
                duration_years=duree,
                credit_type=credit_type,
                with_insurance=with_insurance
            )
            
            # Formatage de la réponse
            response = self.credit_calculator.format_simulation_result(simulation)
            
            # Ajout d'une proposition d'assurance si pas déjà incluse
            if not with_insurance and credit_type != 'immobilier':
                response += "\n\nSouhaitez-vous ajouter une assurance emprunteur à cette simulation ?"
            # ✅ Sauvegarde de la simulation dans l'historique
            self.save_simulation(
            user_id,
            {
                'montant': montant,
                'duree': duree,
                'type_credit': credit_type,
                'assurance': with_insurance
            },
            response
            )
        
            return response
            
        except ValueError as e:
            return f"❌ Erreur dans les paramètres : {e}"
        except Exception as e:
            return f"❌ Erreur lors du calcul : {e}"
    
    def generate_credit_request_response(self, entities: Dict[str, Any], context: Dict[str, Any]) -> str:
        """
        Génère une réponse pour une demande de crédit
        """
        response = """📋 **Étapes de la demande de crédit :**

1️⃣ **Vérification d'éligibilité**
   - Revenus minimum : 1500€/mois
   - Âge : 18-75 ans
   - Résidence en France

2️⃣ **Documents nécessaires :**
   - Pièce d'identité
   - Justificatifs de revenus (3 derniers bulletins)
   - Justificatif de domicile
   - RIB

3️⃣ **Rendez-vous conseiller :**
   Souhaitez-vous prendre rendez-vous avec un conseiller pour finaliser votre demande ?

⏰ **Durée de traitement :** 48-72h après réception du dossier complet

💡 **Conseil :** Avez-vous déjà fait une simulation ? C'est recommandé avant de faire votre demande."""
        
        return response
    
    def generate_product_info_response(self, entities: Dict[str, Any], context: Dict[str, Any]) -> str:
        """
        Génère une réponse pour les informations sur les produits
        """
        credit_type = entities.get('type_credit', None)
        
        if credit_type and credit_type in self.product_info:
            product = self.product_info[credit_type]
            
            response = f"""🏦 **{product['name']}**

📝 **Description :**
{product['description']}

📊 **Caractéristiques :**
"""
            for feature in product['features']:
                response += f"• {feature}\n"
            
            response += "\n✅ **Avantages :**\n"
            for advantage in product['advantages']:
                response += f"• {advantage}\n"
            
            response += f"\n💡 **Conseil :** Souhaitez-vous une simulation personnalisée pour ce type de crédit ?"
            
            return response
        else:
            # Affiche tous les produits si aucun type précis n'est donné
            response = "🏦 **Tous nos produits de crédit :**\n\n"
            for product in self.product_info.values():
                response += f"**{product['name']}**\n"
                response += f"📝 Description : {product['description']}\n"
                response += "📊 Caractéristiques :\n"
                for feature in product['features']:
                    response += f"• {feature}\n"
                response += "✅ Avantages :\n"
                for advantage in product['advantages']:
                    response += f"• {advantage}\n"
                response += "\n"
            return response


    
    def generate_financial_calc_response(self, entities: Dict[str, Any], context: Dict[str, Any]) -> str:
        """
        Génère une réponse pour les calculs financiers
        """
        # Vérification s'il y a une simulation précédente
        if context.get('simulation_history'):
            last_simulation = context['simulation_history'][-1]
            
            response = """💰 **Calculs financiers :**

📊 **Détail des coûts :**
• Coût du crédit (hors assurance) : {total_interest:,.0f}€
• Frais de dossier : {filing_fees}€
• Coût total : {total_cost:,.0f}€

📈 **Comparaisons possibles :**
• Avec/sans assurance
• Différentes durées
• Différents montants

Que souhaitez-vous calculer précisément ?""".format(
                total_interest=last_simulation.get('total_interest', 0),
                filing_fees=last_simulation.get('filing_fees', 0),
                total_cost=last_simulation.get('total_paid', 0)
            )
            
            return response
        # ✅ Si aucune simulation, mais montant et durée fournis → calcul TAEG direct
        elif 'montant' in entities and 'duree' in entities:
         try:
            montant = int(entities['montant'])
            duree = int(entities['duree'])
            taux = self.credit_calculator.taux_annuel
            taeg = self.credit_calculator.calculer_taeg(montant, duree, taux)
            return f"📈 Le TAEG pour un crédit de {montant}€ sur {duree} ans à {taux}% est de **{taeg}%**."
         except Exception as e:
            return f"❌ Erreur lors du calcul du TAEG : {e}"
    
    # ❌ Si pas assez d'infos
        else:
         return "Pour calculer le TAEG, précisez au moins le montant et la durée du crédit."
    def generate_support_response(self, entities: Dict[str, Any], context: Dict[str, Any]) -> str:
        """
        Génère une réponse pour le support client
        """
        response = """🔧 **Support Client**

Je suis là pour vous aider ! Voici les options disponibles :

📞 **Contact conseiller :**
• Téléphone : 01 23 45 67 89
• Horaires : Lun-Ven 9h-18h, Sam 9h-12h
• Email : conseiller@banque.fr

💬 **Chat en direct :**
• Disponible 24h/24
• Temps de réponse : < 2 minutes

📧 **Email support :**
• support@banque.fr
• Réponse sous 24h

🔐 **Mot de passe oublié :**
• Cliquez sur "Mot de passe oublié" sur la page de connexion
• Un lien de réinitialisation vous sera envoyé par email

Que puis-je faire pour vous aider davantage ?"""
        
        return response
    
    def generate_modification_response(self, entities: Dict[str, Any], context: Dict[str, Any]) -> str:
        """
        Génère une réponse pour la modification de simulation
        """
        if not context.get('simulation_history'):
            return "Je n'ai pas de simulation précédente à modifier. Pouvez-vous d'abord faire une simulation ?"
        
        # Récupération de la dernière simulation
        last_simulation = context['simulation_history'][-1]
        
        # Création d'une nouvelle simulation avec les paramètres modifiés
        new_params = last_simulation.copy()
        new_params.update(entities)
        
        try:
            new_simulation = self.credit_calculator.simulate_credit(
                capital=new_params['montant'],
                duration_years=new_params['duree'],
                credit_type=new_params.get('type_credit', 'personnel'),
                with_insurance=new_params.get('assurance', False)
            )
            
            # Comparaison avec l'ancienne simulation
            comparison = self.credit_calculator.compare_simulations(last_simulation, new_simulation)
            
            return f"✅ **Simulation modifiée**\n\n{comparison}"
            
        except Exception as e:
            return f"❌ Erreur lors de la modification : {e}"
    
    def save_simulation(self, user_id: str, entities: Dict[str, Any], response: str):
        """
        Sauvegarde une simulation dans l'historique
        """
        try:
            simulation = self.credit_calculator.simulate_credit(
                capital=entities['montant'],
                duration_years=entities['duree'],
                credit_type=entities.get('type_credit', 'personnel'),
                with_insurance=entities.get('assurance', False)
            )
            print(f"💾 Sauvegarde simulation pour {user_id} | montant={entities['montant']} | durée={entities['duree']}")
            
            self.conversation_context[user_id]['simulation_history'].append(simulation)
            
            # Limitation de l'historique à 5 simulations
            if len(self.conversation_context[user_id]['simulation_history']) > 5:
                self.conversation_context[user_id]['simulation_history'].pop(0)
                
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde de la simulation : {e}")
    
    def get_conversation_summary(self, user_id: str) -> Dict[str, Any]:
        """
        Retourne un résumé de la conversation
        """
        if user_id not in self.conversation_context:
            return {}
        
        context = self.conversation_context[user_id]
        
        return {
            'conversation_count': context['conversation_count'],
            'last_intent': context['last_intent'],
            'simulation_count': len(context['simulation_history']),
            'last_simulation': context['simulation_history'][-1] if context['simulation_history'] else None
        }

# Fonction pour tester le chatbot
def test_chatbot():
    """
    Teste le chatbot avec des exemples
    """
    chatbot = ChatbotBancaire()
    
    # Test de chargement des modèles
    if not chatbot.load_models():
        print("❌ Impossible de charger les modèles")
        return
    
    # Exemples de test
    test_messages = [
        "Bonjour, je voudrais simuler un crédit personnel de 50 000€ sur 5 ans",
        "Qu'est-ce qu'un crédit immobilier ?",
        "Je veux faire une demande de crédit",
        "Calculez-moi le TAEG",
        "Je voudrais changer la durée à 7 ans",
        "Comment contacter un conseiller ?"
    ]
    
    print("\n🧪 Test du Chatbot Bancaire")
    print("=" * 50)
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n--- Test {i} ---")
        result = chatbot.process_message(message, f"user_{i}")
        
        print(f"🎯 Intent détecté: {result['intent']} (confiance: {result['confidence']:.3f})")
        if result['entities']:
            print(f"🔍 Entités extraites: {result['entities']}")
        
        print(f"📊 Résumé conversation: {chatbot.get_conversation_summary(f'user_{i}')}")
        from credit_calculator import calculer_mensualite
from entity_extractor import extract_entities

def handle_simulation(message):
    entities = extract_entities(message)
    montant = entities["montant"]
    duree = entities["duree"]
    type_credit = entities["type_credit"]

    if not montant or not duree:
        return "Pouvez-vous préciser le montant et la durée du crédit ?"

    mensualite = calculer_mensualite(float(montant), duree, taux_annuel=0.02)
    return f"Pour un crédit {type_credit} de {montant}€ sur {duree} ans, la mensualité estimée est de {mensualite:.2f}€/mois."


if __name__ == "__main__":
    # Test du chatbot
    test_chatbot() 
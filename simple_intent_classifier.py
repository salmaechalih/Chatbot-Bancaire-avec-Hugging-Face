#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import json
from typing import Dict, Tuple

class SimpleIntentClassifier:
    """
    Classificateur d'intent simple basé sur des mots-clés
    Alternative rapide au modèle Transformer en cas de problème
    """
    
    def __init__(self):
        """Initialise le classificateur avec des mots-clés prédéfinis"""
        self.intent_keywords = {
            'simulation_credit': [
                'simuler', 'simulation', 'calculer', 'calcul', 'mensualité', 'mensualités',
                'crédit', 'prêt', 'emprunt', 'emprunter', 'financement', 'taux',
                '€', 'euros', 'euro', 'mois', 'ans', 'année', 'années'
            ],
            'demande_credit': [
                'demande', 'demander', 'solliciter', 'obtenir', 'faire',
                'démarche', 'démarches', 'étape', 'étapes', 'procédure',
                'condition', 'conditions', 'dossier'
            ],
            'information_produit': [
                'qu\'est-ce', 'qu\'est', 'expliquer', 'expliquez', 'différence', 'différences',
                'avantage', 'avantages', 'caractéristique', 'caractéristiques',
                'fonctionne', 'fonctionnement', 'type', 'types', 'assurance'
            ],
            'calcul_financier': [
                'taeg', 'coût', 'total', 'amortissement', 'intérêt', 'intérêts',
                'remboursement', 'rembourser', 'tableau', 'montant'
            ],
            'support_client': [
                'contacter', 'conseiller', 'contact', 'aider', 'aide',
                'problème', 'comprendre', 'expliquer', 'horaire', 'horaires',
                'mot de passe', 'identifiant', 'support', 'joindre'
            ],
            'modification_simulation': [
                'modifier', 'modification', 'changer', 'changement',
                'nouveau', 'nouvelle', 'autre', 'différent'
            ]
        }
        
        # Expressions régulières pour détecter des montants et durées
        self.amount_pattern = re.compile(r'(\d+(?:\s*\d+)*)\s*€|(\d+(?:\s*\d+)*)\s*euros?')
        self.duration_pattern = re.compile(r'(\d+)\s*(?:an|ans|année|années|mois)')
        
    def extract_entities(self, text: str) -> Dict[str, str]:
        """Extrait les entités simples du texte"""
        entities = {}
        
        # Extraction du montant
        amount_match = self.amount_pattern.search(text)
        if amount_match:
            amount = amount_match.group(1) or amount_match.group(2)
            amount = amount.replace(' ', '')
            entities['montant'] = amount
            
        # Extraction de la durée
        duration_match = self.duration_pattern.search(text)
        if duration_match:
            duration = duration_match.group(1)
            entities['duree'] = duration
            
        # Détection du type de crédit
        text_lower = text.lower()
        if 'personnel' in text_lower:
            entities['type_credit'] = 'personnel'
        elif 'immobilier' in text_lower:
            entities['type_credit'] = 'immobilier'
        elif 'automobile' in text_lower or 'auto' in text_lower or 'voiture' in text_lower:
            entities['type_credit'] = 'automobile'
        elif 'travaux' in text_lower:
            entities['type_credit'] = 'travaux'
            
        return entities
    
    def classify_intent(self, text: str) -> Tuple[str, float]:
        """
        Classifie l'intent du texte en utilisant la correspondance de mots-clés
        
        Returns:
            Tuple[str, float]: (intent, confidence_score)
        """
        text_lower = text.lower()
        
        # Calcul des scores pour chaque intent
        intent_scores = {}
        
        for intent, keywords in self.intent_keywords.items():
            score = 0
            total_keywords = len(keywords)
            
            # Compte les mots-clés trouvés
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    # Bonus si le mot-clé est un mot complet
                    if re.search(r'\b' + re.escape(keyword.lower()) + r'\b', text_lower):
                        score += 2
                    else:
                        score += 1
            
            # Normalise le score avec boost si plusieurs mots-clés correspondent
            if total_keywords > 0:
                normalized_score = score / total_keywords
                # Boost si score élevé
                if normalized_score > 0.3:
                    normalized_score = min(normalized_score * 1.5, 1.0)
                intent_scores[intent] = normalized_score
        
        # Trouve l'intent avec le meilleur score
        if intent_scores:
            best_intent = max(intent_scores, key=intent_scores.get)
            confidence = min(intent_scores[best_intent], 1.0)  # Cap à 1.0
            
            # Seuil minimal de confiance
            if confidence >= 0.1:
                return best_intent, confidence
        
        # Cas par défaut
        return 'support_client', 0.1
    
    def predict(self, text: str) -> Dict[str, any]:
        """
        Prédit l'intent et extrait les entités
        
        Returns:
            Dict contenant intent, confidence et entities
        """
        intent, confidence = self.classify_intent(text)
        entities = self.extract_entities(text)
        
        return {
            'intent': intent,
            'confidence': confidence,
            'entities': entities
        }

if __name__ == "__main__":
    # Test rapide
    classifier = SimpleIntentClassifier()
    
    test_phrases = [
        "Je voudrais simuler un crédit personnel de 50 000€ sur 5 ans",
        "Qu'est-ce qu'un crédit immobilier ?",
        "Comment contacter un conseiller ?",
        "Je veux faire une demande de crédit",
        "Calculez-moi le TAEG"
    ]
    
    print("🧪 Test du classificateur simple")
    print("=" * 50)
    
    for phrase in test_phrases:
        result = classifier.predict(phrase)
        print(f"\nPhrase: {phrase}")
        print(f"Intent: {result['intent']} (confiance: {result['confidence']:.2%})")
        if result['entities']:
            print(f"Entités: {result['entities']}")

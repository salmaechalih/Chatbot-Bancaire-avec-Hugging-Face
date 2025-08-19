#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from chatbot_bancaire import ChatbotBancaire

def test_chatbot_simple():
    """Test rapide du chatbot avec le classificateur simple"""
    print("🧪 Test du Chatbot Bancaire (version corrigée)")
    print("=" * 60)
    
    # Initialisation
    chatbot = ChatbotBancaire()
    chatbot.load_models()
    
    # Questions de test
    questions = [
        "Je voudrais simuler un crédit personnel de 50 000€ sur 5 ans",
        "Qu'est-ce qu'un crédit immobilier ?",
        "Comment contacter un conseiller ?",
        "Je veux faire une demande de crédit",
        "Calculez-moi le TAEG"
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n{'='*60}")
        print(f"🔸 Test {i}: {question}")
        print('='*60)
        
        result = chatbot.process_message(question, "test_user")
        
        print(f"Intent détecté: {result['intent']}")
        print(f"Confiance: {result['confidence']:.1%}")
        print(f"Entités: {result['entities']}")
        print(f"\n📝 Réponse complète:")
        print(result['response'])

if __name__ == "__main__":
    test_chatbot_simple()

import json
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from datasets import Dataset
import re

class IntentClassifier:
    def __init__(self, model_name="distilbert-base-uncased"):
        """
        Initialise le classifieur d'intents avec un modèle Hugging Face
        """
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = None
        self.intent_labels = []
        self.label2id = {}
        self.id2label = {}
        
    def load_dataset(self, dataset_path="dataset_bancaire.json"):
        """
        Charge le dataset d'entraînement
        """
        with open(dataset_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Préparation des données d'entraînement
        texts = []
        labels = []
        
        for intent_data in data['intents']:
            intent_name = intent_data['intent']
            if intent_name not in self.label2id:
                self.label2id[intent_name] = len(self.label2id)
                self.id2label[len(self.id2label)] = intent_name
                self.intent_labels.append(intent_name)
            
            for example in intent_data['examples']:
                texts.append(example)
                labels.append(self.label2id[intent_name])
        
        return texts, labels
    
    def prepare_dataset(self, texts, labels):
        """
        Prépare le dataset pour l'entraînement
        """
        # Tokenisation
        encodings = self.tokenizer(
            texts,
            truncation=True,
            padding=True,
            max_length=128,
            return_tensors="pt"
        )
        
        # Création du dataset
        dataset = Dataset.from_dict({
            'input_ids': encodings['input_ids'],
            'attention_mask': encodings['attention_mask'],
            'labels': labels
        })
        
        return dataset
    
    def train(self, dataset_path="dataset_bancaire.json", output_dir="./intent_model"):
        """
        Entraîne le modèle de classification d'intents
        """
        print("🔄 Chargement du dataset...")
        texts, labels = self.load_dataset(dataset_path)
        
        print(f"📊 Dataset chargé : {len(texts)} exemples, {len(self.intent_labels)} intents")
        print(f"🎯 Intents : {', '.join(self.intent_labels)}")
        
        # Division train/test
        train_texts, test_texts, train_labels, test_labels = train_test_split(
            texts, labels, test_size=0.2, random_state=42, stratify=labels
        )
        
        # Préparation des datasets
        train_dataset = self.prepare_dataset(train_texts, train_labels)
        test_dataset = self.prepare_dataset(test_texts, test_labels)
        
        # Initialisation du modèle
        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.model_name,
            num_labels=len(self.intent_labels),
            id2label=self.id2label,
            label2id=self.label2id
        )
        
        # Configuration de l'entraînement
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=3,
            per_device_train_batch_size=8,
            per_device_eval_batch_size=8,
            warmup_steps=100,
            weight_decay=0.01,
            logging_dir=f"{output_dir}/logs",
            logging_steps=10,
            evaluation_strategy="steps",
            eval_steps=50,
            save_steps=100,
            load_best_model_at_end=True,
            metric_for_best_model="accuracy"
        )
        
        # Entraînement
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=test_dataset,
            compute_metrics=self.compute_metrics
        )
        
        print("🚀 Début de l'entraînement...")
        trainer.train()
        
        # Évaluation
        print("📈 Évaluation du modèle...")
        results = trainer.evaluate()
        print(f"Accuracy: {results['eval_accuracy']:.4f}")
        
        # Sauvegarde du modèle
        trainer.save_model(output_dir)
        self.tokenizer.save_pretrained(output_dir)
        
        # Sauvegarde des mappings
        with open(f"{output_dir}/label_mappings.json", 'w', encoding='utf-8') as f:
            json.dump({
                'label2id': self.label2id,
                'id2label': self.id2label,
                'intent_labels': self.intent_labels
            }, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Modèle sauvegardé dans {output_dir}")
        return results
    
    def load_trained_model(self, model_path="./intent_model"):
        """
        Charge un modèle entraîné
        """
        try:
            self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            
            # Chargement des mappings
            with open(f"{model_path}/label_mappings.json", 'r', encoding='utf-8') as f:
                mappings = json.load(f)
                self.label2id = mappings['label2id']
                self.id2label = mappings['id2label']
                self.intent_labels = mappings['intent_labels']
            
            print(f"✅ Modèle chargé depuis {model_path}")
            print(f"🎯 Intents disponibles : {', '.join(self.intent_labels)}")
            return True
        except Exception as e:
            print(f"❌ Erreur lors du chargement du modèle : {e}")
            return False
    
    def predict_intent(self, text, return_confidence=False):
        """
        Prédit l'intent d'un texte donné
        """
        if self.model is None:
            raise ValueError("Le modèle n'est pas chargé. Utilisez load_trained_model() ou train()")
        
        # Tokenisation
        inputs = self.tokenizer(
            text,
            truncation=True,
            padding=True,
            max_length=128,
            return_tensors="pt"
        )
        
        # Prédiction
        with torch.no_grad():
            outputs = self.model(**inputs)
            probabilities = torch.softmax(outputs.logits, dim=-1)
            predicted_id = torch.argmax(probabilities, dim=-1).item()
            confidence = probabilities[0][predicted_id].item()
        
        predicted_intent = self.id2label[predicted_id]
        
        if return_confidence:
            return predicted_intent, confidence
        else:
            return predicted_intent
    
    def predict_intent_with_confidence(self, text):
        """
        Prédit l'intent avec le niveau de confiance
        """
        intent, confidence = self.predict_intent(text, return_confidence=True)
        
        # Récupération des probabilités pour tous les intents
        inputs = self.tokenizer(
            text,
            truncation=True,
            padding=True,
            max_length=128,
            return_tensors="pt"
        )
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            probabilities = torch.softmax(outputs.logits, dim=-1)
        
        # Création du dictionnaire des confiances
        confidences = {}
        for intent_id, intent_name in self.id2label.items():
            confidences[intent_name] = probabilities[0][intent_id].item()
        
        return {
            'intent': intent,
            'confidence': confidence,
            'all_confidences': confidences
        }
    
    def compute_metrics(self, eval_pred):
        """
        Calcule les métriques d'évaluation
        """
        predictions, labels = eval_pred
        predictions = np.argmax(predictions, axis=1)
        
        accuracy = accuracy_score(labels, predictions)
        
        return {
            'accuracy': accuracy
        }

# Fonction utilitaire pour tester le classifieur
def test_intent_classifier():
    """
    Teste le classifieur d'intents
    """
    classifier = IntentClassifier()
    
    # Test avec des phrases d'exemple
    test_phrases = [
        "Je voudrais simuler un crédit de 50 000€",
        "Comment faire pour demander un prêt ?",
        "Qu'est-ce qu'un crédit personnel ?",
        "J'ai oublié mon mot de passe",
        "Calculez-moi le TAEG",
        "Je voudrais changer la durée"
    ]
    
    print("🧪 Test du classifieur d'intents...")
    for phrase in test_phrases:
        try:
            result = classifier.predict_intent_with_confidence(phrase)
            print(f"📝 '{phrase}'")
            print(f"   🎯 Intent: {result['intent']}")
            print(f"   📊 Confiance: {result['confidence']:.3f}")
            print()
        except Exception as e:
            print(f"❌ Erreur pour '{phrase}': {e}")

if __name__ == "__main__":
    # Test du classifieur
    test_intent_classifier() 
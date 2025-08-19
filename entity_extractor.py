import re
import json
import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification
from typing import Dict, List, Any, Tuple

class EntityExtractor:
    def __init__(self, model_name="dslim/bert-base-NER"):
        """
        Initialise l'extracteur d'entités avec un modèle Hugging Face
        """
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForTokenClassification.from_pretrained(model_name)
        
        # Patterns regex pour l'extraction d'entités spécifiques au domaine bancaire
        self.patterns = {
            'montant': [
                r'(\d{1,3}(?:\s\d{3})*)\s*(?:€|euros?)',
                r'(\d+)\s*k\s*(?:€|euros?)',
                r'(\d+(?:[,.]\d+)?)\s*(?:€|euros?)'
            ],
            'duree': [
                r'(\d+)\s*(?:ans?|années?)',
                r'(\d+)\s*mois',
                r'sur\s*(\d+)\s*(?:ans?|années?)',
                r'(\d+)\s*années?'
            ],
            'type_credit': [
                r'(?:crédit|prêt)\s+(personnel|immobilier|automobile|travaux|rénovation)',
                r'(personnel|immobilier|automobile|travaux|rénovation)\s+(?:crédit|prêt)',
                r'prêt\s+(auto|voiture)',
                r'crédit\s+(auto|voiture)'
            ],
            'taux_interet': [
                r'(\d+(?:[,.]\d+)?)\s*%',
                r'(\d+(?:[,.]\d+)?)\s*pour\s*cent',
                r'taux\s*(?:de\s*)?(\d+(?:[,.]\d+)?)\s*%'
            ],
            'assurance': [
                r'(avec|sans)\s*assurance',
                r'assurance\s*(?:emprunteur)?\s*(avec|sans)',
                r'(oui|non)\s*(?:pour\s*l\'assurance)?'
            ],
            'revenus': [
                r'(\d+(?:[,.]\d+)?)\s*(?:€|euros?)\s*(?:par\s*mois|mensuels?)',
                r'(\d+(?:[,.]\d+)?)\s*(?:€|euros?)\s*/mois',
                r'revenus?\s*(?:de\s*)?(\d+(?:[,.]\d+)?)\s*(?:€|euros?)'
            ]
        }
        
        # Mapping des types de crédit
        self.credit_type_mapping = {
            'auto': 'automobile',
            'voiture': 'automobile',
            'rénovation': 'renovation'
        }
    
    def extract_entities_regex(self, text: str) -> Dict[str, Any]:
        """
        Extrait les entités en utilisant des patterns regex
        """
        entities = {}
        
        # Extraction du montant
        for pattern in self.patterns['montant']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Nettoyage et conversion du montant
                montant_str = matches[0].replace(' ', '').replace(',', '.')
                if 'k' in montant_str.lower():
                    montant_str = montant_str.lower().replace('k', '000')
                entities['montant'] = float(montant_str)
                break
        
        # Extraction de la durée
        for pattern in self.patterns['duree']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                duree = int(matches[0])
                # Si la durée est en mois, convertir en années
                if 'mois' in text.lower():
                    duree = duree // 12
                entities['duree'] = duree
                break
        
        # Extraction du type de crédit
        for pattern in self.patterns['type_credit']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                credit_type = matches[0].lower()
                # Mapping des synonymes
                if credit_type in self.credit_type_mapping:
                    credit_type = self.credit_type_mapping[credit_type]
                entities['type_credit'] = credit_type
                break
        
        # Extraction du taux d'intérêt
        for pattern in self.patterns['taux_interet']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                taux_str = matches[0].replace(',', '.')
                entities['taux_interet'] = float(taux_str)
                break
        
        # Extraction de l'assurance
        for pattern in self.patterns['assurance']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                assurance = matches[0].lower()
                if assurance in ['oui', 'avec']:
                    entities['assurance'] = True
                elif assurance in ['non', 'sans']:
                    entities['assurance'] = False
                break
        
        # Extraction des revenus
        for pattern in self.patterns['revenus']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                revenus_str = matches[0].replace(',', '.')
                entities['revenus'] = float(revenus_str)
                break
        
        return entities
    
    def extract_entities_ner(self, text: str) -> List[Dict[str, Any]]:
        """
        Extrait les entités en utilisant le modèle NER de Hugging Face
        """
        # Tokenisation
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            return_offsets_mapping=True
        )
        
        # Prédiction
        with torch.no_grad():
            outputs = self.model(**inputs)
            predictions = torch.argmax(outputs.logits, dim=-1)
        
        # Extraction des entités
        entities = []
        offset_mapping = inputs['offset_mapping'][0]
        
        current_entity = None
        current_text = ""
        
        for i, (prediction, offset) in enumerate(zip(predictions[0], offset_mapping)):
            if offset[0] == 0 and offset[1] == 0:  # Token spécial
                continue
            
            label = self.model.config.id2label[prediction.item()]
            
            if label.startswith('B-'):  # Beginning of entity
                if current_entity:
                    entities.append({
                        'text': current_text.strip(),
                        'type': current_entity,
                        'start': current_start,
                        'end': offset[0]
                    })
                
                current_entity = label[2:]  # Remove 'B-' prefix
                current_text = text[offset[0]:offset[1]]
                current_start = offset[0]
                
            elif label.startswith('I-') and current_entity and label[2:] == current_entity:
                # Inside of entity
                current_text += text[offset[0]:offset[1]]
                
            elif label == 'O':  # Outside of entity
                if current_entity:
                    entities.append({
                        'text': current_text.strip(),
                        'type': current_entity,
                        'start': current_start,
                        'end': offset[0]
                    })
                    current_entity = None
                    current_text = ""
        
        # Ajouter la dernière entité si elle existe
        if current_entity:
            entities.append({
                'text': current_text.strip(),
                'type': current_entity,
                'start': current_start,
                'end': len(text)
            })
        
        return entities
    
    def extract_entities(self, text: str) -> Dict[str, Any]:
        """
        Extrait toutes les entités d'un texte en combinant regex et NER
        """
        # Extraction avec regex (spécifique au domaine bancaire)
        regex_entities = self.extract_entities_regex(text)
        
        # Extraction avec NER (entités générales)
        ner_entities = self.extract_entities_ner(text)
        
        # Combinaison des résultats
        entities = regex_entities.copy()
        
        # Ajout des entités NER pertinentes
        for entity in ner_entities:
            if entity['type'] in ['MONEY', 'CARDINAL', 'DATE']:
                # Traitement des entités numériques détectées par NER
                if entity['type'] == 'MONEY' and 'montant' not in entities:
                    # Tentative d'extraction de montant depuis l'entité NER
                    amount_match = re.search(r'(\d+(?:[,.]\d+)?)', entity['text'])
                    if amount_match:
                        entities['montant'] = float(amount_match.group(1).replace(',', '.'))
                
                elif entity['type'] == 'CARDINAL' and 'duree' not in entities:
                    # Tentative d'extraction de durée depuis l'entité NER
                    if any(word in text.lower() for word in ['ans', 'années', 'mois']):
                        entities['duree'] = int(entity['text'])
        
        return entities
    
    def validate_entities(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valide et nettoie les entités extraites
        """
        validated_entities = {}
        
        # Validation du montant
        if 'montant' in entities:
            montant = entities['montant']
            if 1000 <= montant <= 1500000:
                validated_entities['montant'] = montant
        
        # Validation de la durée
        if 'duree' in entities:
            duree = entities['duree']
            if 1 <= duree <= 25:
                validated_entities['duree'] = duree
        
        # Validation du type de crédit
        if 'type_credit' in entities:
            valid_types = ['personnel', 'immobilier', 'automobile', 'travaux', 'renovation']
            if entities['type_credit'] in valid_types:
                validated_entities['type_credit'] = entities['type_credit']
        
        # Validation du taux d'intérêt
        if 'taux_interet' in entities:
            taux = entities['taux_interet']
            if 1.0 <= taux <= 15.0:
                validated_entities['taux_interet'] = taux
        
        # Validation de l'assurance
        if 'assurance' in entities:
            validated_entities['assurance'] = entities['assurance']
        
        # Validation des revenus
        if 'revenus' in entities:
            revenus = entities['revenus']
            if 1000 <= revenus <= 50000:
                validated_entities['revenus'] = revenus
        
        return validated_entities
    
    def extract_entities_with_validation(self, text: str) -> Dict[str, Any]:
        """
        Extrait et valide les entités d'un texte
        """
        entities = self.extract_entities(text)
        validated_entities = self.validate_entities(entities)
        
        return {
            'raw_entities': entities,
            'validated_entities': validated_entities,
            'confidence': self.calculate_extraction_confidence(entities, validated_entities)
        }
    
    def calculate_extraction_confidence(self, raw_entities: Dict, validated_entities: Dict) -> float:
        """
        Calcule un score de confiance pour l'extraction
        """
        if not raw_entities:
            return 0.0
        
        # Nombre d'entités validées vs total
        validation_ratio = len(validated_entities) / len(raw_entities)
        
        # Bonus pour les entités importantes
        important_entities = ['montant', 'duree', 'type_credit']
        important_count = sum(1 for entity in important_entities if entity in validated_entities)
        important_bonus = important_count / len(important_entities) * 0.3
        
        confidence = validation_ratio * 0.7 + important_bonus
        
        return min(confidence, 1.0)

# Fonction utilitaire pour tester l'extracteur
def test_entity_extractor():
    """
    Teste l'extracteur d'entités
    """
    extractor = EntityExtractor()
    
    test_phrases = [
        "Je voudrais simuler un crédit personnel de 50 000€ sur 5 ans",
        "Simulation prêt immobilier 200 000€ sur 20 ans avec assurance",
        "Crédit automobile 25 000€ sur 4 ans à 3.5%",
        "Je gagne 3500€ par mois",
        "Prêt travaux 35 000€ sur 7 ans sans assurance"
    ]
    
    print("🧪 Test de l'extracteur d'entités...")
    for phrase in test_phrases:
        print(f"\n📝 '{phrase}'")
        result = extractor.extract_entities_with_validation(phrase)
        
        print(f"   🔍 Entités extraites :")
        for entity_type, value in result['validated_entities'].items():
            print(f"      - {entity_type}: {value}")
        
        print(f"   📊 Confiance: {result['confidence']:.3f}")



def extract_entities(message):
    montant_match = re.search(r'(\d[\d\s]*\d)[€]?', message)
    duree_match = re.search(r'(\d+)\s*(ans|années)', message)
    type_match = re.search(r'crédit\s+(immobilier|personnel)', message)

    montant = montant_match.group(1).replace(" ", "") if montant_match else None
    duree = int(duree_match.group(1)) if duree_match else None
    type_credit = type_match.group(1) if type_match else "immobilier"

    return {
        "montant": montant,
        "duree": duree,
        "type_credit": type_credit
    }


if __name__ == "__main__":
    # Test de l'extracteur
    test_entity_extractor() 
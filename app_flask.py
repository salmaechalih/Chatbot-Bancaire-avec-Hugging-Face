from flask import Flask, render_template, request, jsonify, session
import json
import time
from chatbot_bancaire import ChatbotBancaire

app = Flask(__name__)
app.secret_key = 'chatbot_bancaire_secret_key_2024'

# Initialisation du chatbot
chatbot = None

def initialize_chatbot():
    """
    Initialise le chatbot
    """
    global chatbot
    if chatbot is None:
        chatbot = ChatbotBancaire()
        if not chatbot.load_models():
            raise Exception("Impossible d'initialiser le chatbot")
    return chatbot

@app.route('/')
def index():
    """
    Page d'accueil
    """
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """
    Endpoint pour le chat
    """
    try:
        # Initialisation du chatbot
        chatbot = initialize_chatbot()
        
        # Récupération des données
        data = request.get_json()
        message = data.get('message', '').strip()
        user_id = data.get('user_id', 'default')
        
        if not message:
            return jsonify({
                'success': False,
                'error': 'Message vide'
            })
        
        # Traitement du message
        result = chatbot.process_message(message, user_id)
        
        # Préparation de la réponse
        response = {
            'success': True,
            'response': result['response'],
            'intent': result['intent'],
            'confidence': result['confidence'],
            'entities': result['entities'],
            'entity_confidence': result['entity_confidence'],
            'timestamp': time.time()
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/simulate', methods=['POST'])
def simulate_credit():
    """
    Endpoint pour les simulations de crédit
    """
    try:
        data = request.get_json()
        
        # Validation des paramètres
        required_params = ['montant', 'duree']
        for param in required_params:
            if param not in data:
                return jsonify({
                    'success': False,
                    'error': f'Paramètre manquant : {param}'
                })
        
        # Récupération des paramètres
        montant = float(data['montant'])
        duree = int(data['duree'])
        credit_type = data.get('type_credit', 'personnel')
        with_insurance = data.get('with_insurance', False)
        
        # Calcul de la simulation
        chatbot = initialize_chatbot()
        simulation = chatbot.credit_calculator.simulate_credit(
            capital=montant,
            duration_years=duree,
            credit_type=credit_type,
            with_insurance=with_insurance
        )
        
        return jsonify({
            'success': True,
            'simulation': simulation
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/products')
def get_products():
    """
    Endpoint pour récupérer les informations sur les produits
    """
    try:
        chatbot = initialize_chatbot()
        return jsonify({
            'success': True,
            'products': chatbot.product_info
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/rates')
def get_rates():
    """
    Endpoint pour récupérer les taux d'intérêt
    """
    try:
        chatbot = initialize_chatbot()
        return jsonify({
            'success': True,
            'rates': chatbot.credit_calculator.rates
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/health')
def health_check():
    """
    Endpoint de vérification de santé
    """
    try:
        chatbot = initialize_chatbot()
        return jsonify({
            'status': 'healthy',
            'chatbot_initialized': chatbot is not None,
            'timestamp': time.time()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': time.time()
        })

if __name__ == '__main__':
    # Création du dossier templates s'il n'existe pas
    import os
    os.makedirs('templates', exist_ok=True)
    
    # Création du template HTML
    create_html_template()
    
    print("🚀 Démarrage du serveur Flask...")
    print("📱 Interface disponible sur : http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

def create_html_template():
    """
    Crée le template HTML pour l'interface
    """
    html_content = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🏦 Chatbot Bancaire</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .chat-container {
            background: #2d2d2d;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.3);
            width: 90%;
            max-width: 1200px;
            height: 80vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        .chat-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
        }
        
        .chat-header h1 {
            font-size: 24px;
            margin-bottom: 5px;
        }
        
        .chat-header p {
            opacity: 0.9;
            font-size: 14px;
        }
        
        .chat-body {
            flex: 1;
            display: flex;
            overflow: hidden;
        }
        
        .chat-messages {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            background: #1a1a1a;
        }
        
        .chat-sidebar {
            width: 300px;
            background: #2d2d2d;
            border-left: 1px solid #555555;
            padding: 20px;
            overflow-y: auto;
        }
        
        .message {
            margin-bottom: 15px;
            display: flex;
            align-items: flex-start;
        }
        
        .message.user {
            justify-content: flex-end;
        }
        
        .message.bot {
            justify-content: flex-start;
        }
        
        .message-content {
            max-width: 70%;
            padding: 12px 16px;
            border-radius: 18px;
            word-wrap: break-word;
            white-space: pre-wrap;
        }
        
        .message.user .message-content {
            background: #007bff;
            color: white;
        }
        
        .message.bot .message-content {
            background: #3d3d3d;
            color: #ffffff;
            border: 1px solid #555555;
        }
        
        .message-avatar {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 8px;
            font-size: 16px;
        }
        
        .message.user .message-avatar {
            background: #007bff;
            color: white;
        }
        
        .message.bot .message-avatar {
            background: #6c757d;
            color: white;
        }
        
        .chat-input {
            padding: 20px;
            background: #2d2d2d;
            border-top: 1px solid #555555;
            display: flex;
            gap: 10px;
        }
        
        .chat-input textarea {
            flex: 1;
            padding: 12px;
            border: 1px solid #555555;
            border-radius: 25px;
            resize: none;
            font-family: inherit;
            font-size: 14px;
            background: #1a1a1a;
            color: #ffffff;
        }
        
        .chat-input button {
            padding: 12px 24px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 14px;
            transition: background 0.3s;
        }
        
        .chat-input button:hover {
            background: #0056b3;
        }
        
        .chat-input button:disabled {
            background: #6c757d;
            cursor: not-allowed;
        }
        
        .sidebar-section {
            margin-bottom: 20px;
        }
        
        .sidebar-section h3 {
            color: #ffffff;
            margin-bottom: 10px;
            font-size: 16px;
        }
        
        .example-question {
            background: #3d3d3d;
            padding: 10px;
            border-radius: 8px;
            margin-bottom: 8px;
            cursor: pointer;
            transition: background 0.3s;
            font-size: 14px;
            color: #ffffff;
        }
        
        .example-question:hover {
            background: #4d4d4d;
        }
        
        .detection-info {
            background: #3d3d3d;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
        }
        
        .detection-info h4 {
            margin-bottom: 10px;
            color: #ffffff;
        }
        
        .confidence-bar {
            width: 100%;
            height: 8px;
            background: #555555;
            border-radius: 4px;
            overflow: hidden;
            margin: 5px 0;
        }
        
        .confidence-fill {
            height: 100%;
            transition: width 0.3s;
        }
        
        .confidence-high {
            background: #28a745;
        }
        
        .confidence-medium {
            background: #ffc107;
        }
        
        .confidence-low {
            background: #dc3545;
        }
        
        .entity-item {
            background: #4d4d4d;
            padding: 8px 12px;
            border-radius: 6px;
            margin-bottom: 5px;
            border-left: 3px solid #007bff;
            color: #ffffff;
        }
        
        .loading {
            display: none;
            text-align: center;
            padding: 20px;
            color: #cccccc;
        }
        
        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #007bff;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        @media (max-width: 768px) {
            .chat-body {
                flex-direction: column;
            }
            
            .chat-sidebar {
                width: 100%;
                height: 200px;
                border-left: none;
                border-top: 1px solid #e9ecef;
            }
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <h1>🏦 Chatbot Bancaire</h1>
            <p>Votre assistant spécialisé dans les crédits</p>
        </div>
        
        <div class="chat-body">
            <div class="chat-messages" id="chatMessages">
                <div class="loading" id="loading">
                    <div class="spinner"></div>
                    <p>Traitement en cours...</p>
                </div>
            </div>
            
            <div class="chat-sidebar">
                <div class="sidebar-section">
                    <h3>💡 Exemples de questions</h3>
                    <div class="example-question" onclick="sendExample('Je voudrais simuler un crédit personnel de 50 000€ sur 5 ans')">
                        Simuler un crédit personnel
                    </div>
                    <div class="example-question" onclick="sendExample('Qu\\'est-ce qu\\'un crédit immobilier ?')">
                        Information crédit immobilier
                    </div>
                    <div class="example-question" onclick="sendExample('Je veux faire une demande de crédit')">
                        Demande de crédit
                    </div>
                    <div class="example-question" onclick="sendExample('Calculez-moi le TAEG')">
                        Calcul TAEG
                    </div>
                    <div class="example-question" onclick="sendExample('Comment contacter un conseiller ?')">
                        Contact conseiller
                    </div>
                </div>
                
                <div class="sidebar-section">
                    <h3>🎯 Détection</h3>
                    <div id="detectionInfo">
                        <p style="color: #cccccc; font-style: italic;">En attente d'un message...</p>
                    </div>
                </div>
                
                <div class="sidebar-section">
                    <h3>📊 Taux d'intérêt</h3>
                    <div style="font-size: 14px; color: #ffffff;">
                        <p><strong>Crédit Personnel :</strong> 4.5% - 7.2%</p>
                        <p><strong>Crédit Immobilier :</strong> 2.8% - 4.1%</p>
                        <p><strong>Crédit Automobile :</strong> 3.2% - 5.8%</p>
                        <p><strong>Crédit Travaux :</strong> 5.1% - 8.3%</p>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="chat-input">
            <textarea 
                id="messageInput" 
                placeholder="Tapez votre message ici..."
                rows="1"
                onkeypress="handleKeyPress(event)"
            ></textarea>
            <button onclick="sendMessage()" id="sendButton">📤 Envoyer</button>
        </div>
    </div>

    <script>
        let userId = 'user_' + Date.now();
        let isProcessing = false;

        // Message de bienvenue
        window.onload = function() {
            addMessage(`🏦 **Bienvenue sur votre Assistant Bancaire !**

Je suis votre conseiller virtuel spécialisé dans les crédits. Je peux vous aider à :

📊 **Simuler des crédits** - Calculer vos mensualités et coûts totaux
📋 **Demander un crédit** - Vous accompagner dans les démarches
🏦 **Informations produits** - Expliquer nos différents types de crédit
💰 **Calculs financiers** - Analyser les coûts et comparer les options
🔧 **Support client** - Répondre à vos questions

**Comment puis-je vous aider aujourd'hui ?**

💡 **Conseil :** Commencez par me dire quel type de crédit vous intéresse et le montant souhaité.`, 'bot');
        };

        function addMessage(content, sender) {
            const messagesContainer = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}`;
            
            const avatar = document.createElement('div');
            avatar.className = 'message-avatar';
            avatar.textContent = sender === 'user' ? '👤' : '🤖';
            
            const messageContent = document.createElement('div');
            messageContent.className = 'message-content';
            messageContent.innerHTML = content;
            
            messageDiv.appendChild(avatar);
            messageDiv.appendChild(messageContent);
            messagesContainer.appendChild(messageDiv);
            
            // Scroll vers le bas
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }

        function updateDetectionInfo(result) {
            const detectionInfo = document.getElementById('detectionInfo');
            
            let html = `
                <div class="detection-info">
                    <h4>Intent détecté</h4>
                    <p style="color: #007bff; font-weight: bold;">${result.intent}</p>
                </div>
                
                <div class="detection-info">
                    <h4>Confiance</h4>
                    <div class="confidence-bar">
                        <div class="confidence-fill ${getConfidenceClass(result.confidence)}" style="width: ${result.confidence * 100}%"></div>
                    </div>
                    <p style="font-size: 12px; margin-top: 5px;">${(result.confidence * 100).toFixed(1)}%</p>
                </div>
            `;
            
            if (result.entities && Object.keys(result.entities).length > 0) {
                html += `
                    <div class="detection-info">
                        <h4>Entités détectées</h4>
                `;
                
                for (const [type, value] of Object.entries(result.entities)) {
                    html += `<div class="entity-item"><strong>${type}:</strong> ${value}</div>`;
                }
                
                html += `</div>`;
            }
            
            detectionInfo.innerHTML = html;
        }

        function getConfidenceClass(confidence) {
            if (confidence > 0.8) return 'confidence-high';
            if (confidence > 0.6) return 'confidence-medium';
            return 'confidence-low';
        }

        function showLoading() {
            document.getElementById('loading').style.display = 'block';
            document.getElementById('sendButton').disabled = true;
            isProcessing = true;
        }

        function hideLoading() {
            document.getElementById('loading').style.display = 'none';
            document.getElementById('sendButton').disabled = false;
            isProcessing = false;
        }

        async function sendMessage() {
            if (isProcessing) return;
            
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            
            if (!message) return;
            
            // Ajouter le message utilisateur
            addMessage(message, 'user');
            input.value = '';
            
            // Afficher le loading
            showLoading();
            
            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        message: message,
                        user_id: userId
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    // Ajouter la réponse du bot
                    addMessage(result.response, 'bot');
                    
                    // Mettre à jour les informations de détection
                    updateDetectionInfo(result);
                } else {
                    addMessage(`❌ Erreur : ${result.error}`, 'bot');
                }
            } catch (error) {
                addMessage(`❌ Erreur de connexion : ${error.message}`, 'bot');
            } finally {
                hideLoading();
            }
        }

        function sendExample(question) {
            document.getElementById('messageInput').value = question;
            sendMessage();
        }

        function handleKeyPress(event) {
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                sendMessage();
            }
        }

        // Auto-resize du textarea
        document.getElementById('messageInput').addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 100) + 'px';
        });
    </script>
</body>
</html>
"""
    
    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("✅ Template HTML créé dans templates/index.html") 
    
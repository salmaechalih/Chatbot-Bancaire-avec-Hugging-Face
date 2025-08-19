import streamlit as st
import json
import time
from chatbot_bancaire import ChatbotBancaire

# Configuration de la page
st.set_page_config(
    page_title="🏦 Chatbot Bancaire",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé avec thème sombre
st.markdown("""
<style>
    /* Thème sombre global */
    .main {
        background-color: #1e1e1e !important;
        color: #ffffff !important;
    }
    
    /* Messages de chat */
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .user-message {
        background-color: #2d3748 !important;
        border-left: 4px solid #4a90e2 !important;
        color: #ffffff !important;
    }
    .bot-message {
        background-color: #1a202c !important;
        border-left: 4px solid #9c27b0 !important;
        color: #ffffff !important;
    }
    .message-header {
        font-weight: bold;
        margin-bottom: 0.5rem;
        color: #ffffff !important;
    }
    .message-content {
        white-space: pre-wrap;
        color: #ffffff !important;
    }
    
    /* Boutons */
    .stButton > button {
        width: 100%;
        margin-top: 0.5rem;
        background-color: #4a90e2 !important;
        color: white !important;
        border: none !important;
    }
    .stButton > button:hover {
        background-color: #357abd !important;
    }
    
    /* Sidebar */
    .sidebar .sidebar-content {
        background-color: #2d2d2d !important;
        color: #ffffff !important;
    }
    
    /* Champs de saisie */
    .stTextArea > div > div > textarea {
        background-color: #2d2d2d !important;
        color: #ffffff !important;
        border: 1px solid #555555 !important;
    }
    
    /* Titres et textes */
    .stMarkdown {
        color: #ffffff !important;
    }
    .stHeader {
        color: #ffffff !important;
    }
    .stSubheader {
        color: #ffffff !important;
    }
    .stCaption {
        color: #cccccc !important;
    }
    
    /* Zones d'information */
    .stSuccess {
        background-color: #2d3748 !important;
        color: #4caf50 !important;
        border: 1px solid #4caf50 !important;
    }
    .stWarning {
        background-color: #2d3748 !important;
        color: #ff9800 !important;
        border: 1px solid #ff9800 !important;
    }
    .stError {
        background-color: #2d3748 !important;
        color: #f44336 !important;
        border: 1px solid #f44336 !important;
    }
    
    /* Spinner */
    .stSpinner > div {
        background-color: #4a90e2 !important;
    }
</style>
""", unsafe_allow_html=True)

def initialize_chatbot():
    if 'chatbot' not in st.session_state:
        with st.spinner("🏦 Initialisation du Chatbot Bancaire..."):
            chatbot = ChatbotBancaire()
            if chatbot.load_models():
                st.session_state.chatbot = chatbot
                st.success("✅ Chatbot initialisé avec succès !")
            else:
                st.error("❌ Erreur lors de l'initialisation du chatbot")
                return None
    return st.session_state.chatbot

def display_message(message, is_user=True):
    if is_user:
        st.markdown(f"""
        <div class="chat-message user-message">
            <div class="message-header">👤 Vous</div>
            <div class="message-content">{message}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-message bot-message">
            <div class="message-header">🤖 Assistant Bancaire</div>
            <div class="message-content">{message}</div>
        </div>
        """, unsafe_allow_html=True)

def display_chat_history():
    if 'chat_history' in st.session_state:
        for message in st.session_state.chat_history:
            display_message(message['content'], message['is_user'])

def add_message_to_history(content, is_user=True):
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    st.session_state.chat_history.append({
        'content': content,
        'is_user': is_user,
        'timestamp': time.time()
    })

def clear_chat_history():
    if 'chat_history' in st.session_state:
        st.session_state.chat_history = []

def process_user_message(message):
    if 'user_id' not in st.session_state:
        st.session_state.user_id = f"user_{int(time.time())}"
    add_message_to_history(message, is_user=True)
    with st.spinner("🤖 Traitement en cours..."):
        try:
            result = st.session_state.chatbot.process_message(message, st.session_state.user_id)
            add_message_to_history(result['response'], is_user=False)
            st.session_state.last_result = result
        except Exception as e:
            error_message = f"❌ Erreur lors du traitement : {str(e)}"
            add_message_to_history(error_message, is_user=False)
            st.error(error_message)
    st.session_state.clear_input = True

def display_welcome_message():
    welcome_message = """🏦 **Bienvenue sur votre Assistant Bancaire !**

Je suis votre conseiller virtuel spécialisé dans les crédits. Je peux vous aider à :

📊 **Simuler des crédits** - Calculer vos mensualités et coûts totaux  
📋 **Demander un crédit** - Vous accompagner dans les démarches  
🏦 **Informations produits** - Expliquer nos différents types de crédit  
💰 **Calculs financiers** - Analyser les coûts et comparer les options  
🔧 **Support client** - Répondre à vos questions

**Comment puis-je vous aider aujourd'hui ?**

💡 **Conseil :** Commencez par me dire quel type de crédit vous intéresse et le montant souhaité."""
    
    if 'chat_history' not in st.session_state or not st.session_state.chat_history:
        add_message_to_history(welcome_message, is_user=False)

def main():
    st.title("🏦 Chatbot Bancaire - Assistant Crédit")
    st.markdown("---")
    
    chatbot = initialize_chatbot()
    if chatbot is None:
        st.error("Impossible d'initialiser le chatbot. Veuillez réessayer.")
        return
    
    with st.sidebar:
        st.header("📊 Informations")
        if 'user_id' in st.session_state:
            summary = chatbot.get_conversation_summary(st.session_state.user_id)
            if summary:
                st.subheader("📈 Statistiques")
                st.write(f"Messages échangés : {summary.get('conversation_count', 0)}")
                st.write(f"Simulations effectuées : {summary.get('simulation_count', 0)}")
                if summary.get('last_intent'):
                    st.write(f"Dernier intent : {summary['last_intent']}")
        st.markdown("---")
        st.subheader("💡 Exemples de questions")
        example_questions = [
            "Je voudrais simuler un crédit personnel de 50 000€ sur 5 ans",
            "Qu'est-ce qu'un crédit immobilier ?",
            "Je veux faire une demande de crédit",
            "Calculez-moi le TAEG",
            "Comment contacter un conseiller ?"
        ]
        for question in example_questions:
            if st.button(question, key=f"example_{question[:20]}"):
                st.session_state.temp_input = question
        st.markdown("---")
        if st.button("🗑️ Effacer l'historique"):
            clear_chat_history()
        st.subheader("📊 Taux d'intérêt")
        st.write("**Crédit Personnel :** 4.5% - 7.2%")
        st.write("**Crédit Immobilier :** 2.8% - 4.1%")
        st.write("**Crédit Automobile :** 3.2% - 5.8%")
        st.write("**Crédit Travaux :** 5.1% - 8.3%")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("💬 Conversation")
        display_chat_history()

        if "temp_input" not in st.session_state:
            st.session_state.temp_input = ""

        if "clear_input" in st.session_state and st.session_state.clear_input:
            st.session_state.temp_input = ""
            st.session_state.clear_input = False

        user_input = st.text_area(
            "Votre message :",
            key="temp_input",
            height=100,
            placeholder="Ex: Je voudrais simuler un crédit personnel de 50 000€ sur 5 ans"
        )

        col_send, col_clear = st.columns(2)

        with col_send:
            if st.button("📤 Envoyer", type="primary"):
                if user_input.strip():
                    process_user_message(user_input)

        with col_clear:
            if st.button("🗑️ Effacer"):
                st.session_state.temp_input = ""
    
    with col2:
        st.subheader("🎯 Détection")
        if 'last_result' in st.session_state:
            result = st.session_state.last_result
            st.write("**Intent :**")
            st.success(result['intent'])
            st.write("**Confiance :**")
            confidence = result['confidence']
            if confidence > 0.8:
                st.success(f"{confidence:.1%}")
            elif confidence > 0.6:
                st.warning(f"{confidence:.1%}")
            else:
                st.error(f"{confidence:.1%}")
            if result['entities']:
                st.write("**Entités détectées :**")
                for entity_type, value in result['entities'].items():
                    st.write(f"• {entity_type}: {value}")
            if result['entity_confidence'] > 0:
                st.write("**Confiance entités :**")
                entity_conf = result['entity_confidence']
                if entity_conf > 0.8:
                    st.success(f"{entity_conf:.1%}")
                elif entity_conf > 0.6:
                    st.warning(f"{entity_conf:.1%}")
                else:
                    st.error(f"{entity_conf:.1%}")

if __name__ == "__main__":
    display_welcome_message()
    main()

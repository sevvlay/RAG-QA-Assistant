
# --- Gerekli Kütüphaneler ---
import streamlit as st
import google.generativeai as genai
from sentence_transformers import SentenceTransformer
import pandas as pd
import numpy as np
import os
from streamlit.errors import StreamlitAPIException, StreamlitSecretNotFoundError
from sklearn.metrics.pairwise import cosine_similarity

# --- Sayfa Ayarları ---
st.set_page_config(
    page_title="RAG Bilgi Asistanı",
    page_icon="🧠",
    layout="wide"
)

# --- CSS ile Küçük Dokunuşlar ---
st.markdown("""
<style>
    /* Buton stili (isteğe bağlı) */
    .stButton>button {
        border-radius: 20px;
        border: 2px solid #FF4B4B;
        color: #FF4B4B;
        background-color: transparent;
    }
    .stButton>button:hover {
        border-color: #FF6B6B;
        color: #FF6B6B;
    }

    /* --- YENİ EKLENEN KISIM: Sidebar metin rengini siyah yap --- */
    [data-testid="stSidebar"] {
        background-color: #f0f2f6; /* Kenar çubuğu arka plan rengi (açık tema için) */
    }
    [data-testid="stSidebar"] .stMarkdown p, 
    [data-testid="stSidebar"] .stHeader, 
    [data-testid="stSidebar"] .stTextArea label,
    [data-testid="stSidebar"] label {
        color: black !important; /* Sidebar içindeki metinleri siyah yap */
    }
    
</style>
""", unsafe_allow_html=True)

# --- 1. İlk Kurulum ve Modelleri Yükleme ---
@st.cache_resource
def load_models_and_data():
    print("Loading models and data...")
    local_model = SentenceTransformer('all-mpnet-base-v2')
    try:
        df_final = pd.read_pickle("my_rag_library_local.pkl")
    except FileNotFoundError:
        st.error("Kütüphane dosyası (my_rag_library_local.pkl) bulunamadı.")
        return None, None, None
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
    except (KeyError, StreamlitSecretNotFoundError, StreamlitAPIException):
        try:
            api_key = os.environ.get('GOOGLE_API_KEY')
            if not api_key: raise ValueError("GOOGLE_API_KEY not found")
            genai.configure(api_key=api_key)
        except Exception as e:
            st.error(f"API Key yapılandırılamadı. Hata: {e}")
            return None, None, None
    generative_model = genai.GenerativeModel('models/gemini-2.5-flash')
    print("Models and data loaded.")
    return local_model, generative_model, df_final

# --- 2. RAG Fonksiyonları ---
def find_best_passages_local(query, dataframe, local_model, top_k=3):
    query_embedding = local_model.encode(query)
    doc_embeddings = np.stack(dataframe['Embeddings'].to_numpy())
    similarities = cosine_similarity(query_embedding.reshape(1, -1), doc_embeddings)[0]
    top_indices = np.argsort(similarities)[-top_k:][::-1]
    return "\n---\n".join(dataframe.iloc[top_indices]['description'].tolist())

def generate_answer(query, dataframe, local_model, generative_model):
    context = find_best_passages_local(query, dataframe, local_model)
    prompt = f"""
    You are a helpful bot. Answer the user's QUESTION based ONLY on the CONTEXT provided.
    If the answer is not in a context, say "I couldn't find an answer in the provided documents."
    CONTEXT: {context}
    QUESTION: {query}
    ANSWER:
    """
    try:
        response = generative_model.generate_content(prompt)
        clean_response = response.text.strip()
        return clean_response
    except Exception as e:
        return f"Cevap üretme sırasında bir hata oluştu: {e}"

# --- 3. Streamlit Arayüz Kodu ---
st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>🧠 RAG Bilgi Asistanı</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>SQuAD veri setini kullanan RAG tabanlı bir chatbot demosu</p>", unsafe_allow_html=True)
st.divider()

local_model, generative_model, df_final = load_models_and_data()

with st.sidebar:
    st.image("https://streamlit.io/images/brand/streamlit-logo-secondary-colormark-darktext.svg", width=200) 
    st.header("❓ Soru Sor")
    st.markdown("SQuAD veri setindeki (Wikipedia makaleleri) bilgilere dayanarak sorularınızı yanıtlamaya çalışırım.")
    user_query = st.text_area("Sorunuz:", placeholder="Which NFL team won Super Bowl 50?", height=100) 
    submit_button = st.button("🚀 Cevap Al")

if local_model and generative_model and (df_final is not None):
    if submit_button:
        if user_query:
            answer_placeholder = st.empty()
            answer_placeholder.info("⏳ Cevabınız aranıyor ve oluşturuluyor...")
            answer = generate_answer(user_query, df_final, local_model, generative_model)
            answer_placeholder.empty()
            st.subheader("🤖 Asistanın Cevabı:")
            st.markdown(f"> {answer}") 
        else:
            st.warning("⚠️ Lütfen bir soru girin.")
else:
    st.error("❌ Modeller veya veri yüklenemediği için uygulama başlatılamadı.")

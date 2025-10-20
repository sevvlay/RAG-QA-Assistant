
# --- Gerekli Kütüphaneler ---
import streamlit as st
import google.generativeai as genai
from sentence_transformers import SentenceTransformer
import pandas as pd
import numpy as np
import os
# Hata türünü içe aktarıyoruz
from streamlit.errors import StreamlitAPIException, StreamlitSecretNotFoundError
# Kosinüs Benzerliği için
from sklearn.metrics.pairwise import cosine_similarity 

# --- 1. İlk Kurulum ve Modelleri Yükleme ---
@st.cache_resource
def load_models_and_data():
    print("Loading models and data...")
    
    # Kullandığımız en son doğru model
    local_model = SentenceTransformer('all-mpnet-base-v2') 
    
    # Kütüphanemizi (df_final) yükle
    try:
        df_final = pd.read_pickle("my_rag_library_local.pkl") 
    except FileNotFoundError:
        st.error("Kütüphane dosyası (my_rag_library_local.pkl) bulunamadı.")
        return None, None, None
    
    # Gemini API'yi yapılandır
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
        
    except (KeyError, StreamlitSecretNotFoundError, StreamlitAPIException):
        try:
            api_key = os.environ.get('GOOGLE_API_KEY')
            if not api_key:
                raise ValueError("GOOGLE_API_KEY not found in os.environ")
            genai.configure(api_key=api_key)
        except Exception as e:
            st.error(f"API Key yapılandırılamadı (os.environ). Hata: {e}")
            return None, None, None
    
    # Çalıştığını bildiğimiz model
    generative_model = genai.GenerativeModel('models/gemini-2.5-flash') 
    
    print("Models and data loaded.")
    return local_model, generative_model, df_final

# --- 2. RAG Fonksiyonları (Kosinüs Benzerliği ile) ---
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
        return response.text
    except Exception as e:
        return f"Cevap üretme sırasında bir hata oluştu: {e}"

# --- 3. Streamlit Arayüz Kodu ---
st.title("📚 RAG Bilgi Asistanı")
st.caption("SQuAD veri setini kullanan RAG tabanlı bir chatbot demosu")

local_model, generative_model, df_final = load_models_and_data()

if local_model and generative_model and (df_final is not None):
    user_query = st.text_input("Kütüphaneye bir soru sorun:", placeholder="Which NFL team represented the AFC at Super Bowl 50?")
    if st.button("Gönder"):
        if user_query:
            with st.spinner("Cevabınız aranıyor..."):
                answer = generate_answer(user_query, df_final, local_model, generative_model)
                st.success("Cevap:")
                st.write(answer)
        else:
            st.warning("Lütfen bir soru girin.")

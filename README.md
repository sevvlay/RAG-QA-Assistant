# RAG-QA-Assistant
# Akbank GenAI Bootcamp: RAG Bilgi Asistanı

Bu proje, Akbank & Global AI Hub tarafından düzenlenen GenAI Bootcamp'in bitirme projesi olarak geliştirilmiştir.

## [cite_start]1. Projenin Amacı (Project Goal) [cite: 9]

[cite_start]Bu projenin temel amacı, **Retrieval Augmented Generation (RAG)** mimarisine dayalı bir chatbot (bilgi asistanı) başarıyla oluşturmak ve dağıtmaktır[cite: 2]. Başlangıçta kitaplarla ilgili bir veri seti hedeflenmiş olsa da, veri seti bulma ve erişimdeki zorluklar nedeniyle proje, sağlam ve güvenilir **Stanford Question Answering Dataset (SQuAD)** kullanılarak adapte edilmiştir.

[cite_start]Asistan, kullanıcının sorduğu soruyu alıp, SQuAD bilgi tabanından (Wikipedia makaleleri kütüphanesi gibi davranan) en alakalı metin parçalarını almak ve bu alınan bilgilere dayanarak kapsamlı, insan benzeri bir cevap üretmek için Google'ın Gemini modelini kullanmak üzere tasarlanmıştır[cite: 2]. Sistemin önemli bir özelliği, bilgi tabanında bulunmayan sorular için cevap uydurmak yerine "Bilmiyorum" diyebilmesidir.

## [cite_start]2. Veri Seti Hakkında Bilgi (Dataset Info) [cite: 10]

Projede, Hugging Face `datasets` kütüphanesi aracılığıyla erişilen **Stanford Question Answering Dataset (SQuAD)** kullanılmıştır.

* **Kaynak:** Wikipedia makalelerinden türetilmiştir.
* **Kullanılan Bölüm:** Geliştirme sürecini hızlandırmak ve API limitlerine takılmamak amacıyla veri setinin `train` bölümünün yalnızca ilk **2000 satırı** (`train[:2000]`) kullanılmıştır.
* **Hazırlık:** Yüklenen ham veriden tekrar eden metin parçaları (`context`/`description`) çıkarılmış ve RAG sistemi için temiz bir doküman kütüphanesi oluşturulmuştur. Bu işlemler sonucunda daha az sayıda benzersiz doküman elde edilmiştir.

## [cite_start]3. Kullanılan Yöntemler ve Çözüm Mimarisi (Methods & Architecture) [cite: 11, 23]

Proje, RAG mimarisi temel alınarak geliştirilmiştir. Akış genel olarak şu şekildedir:

1.  **Soru Alma:** Kullanıcıdan bir soru alınır.
2.  **Soru Embedding:** Kullanıcının sorusu, lokal bir `sentence-transformers` modeli (`all-mpnet-base-v2`) kullanılarak anlamsal bir vektöre dönüştürülür.
3.  **Vektör Arama (Retrieval):** Bu soru vektörü, önceden hesaplanmış ve depolanmış doküman vektörleri (SQuAD metinlerinin embedding'leri) ile **Kosinüs Benzerliği (Cosine Similarity)** metriği kullanılarak karşılaştırılır. Soruya en çok benzeyen ilk `k` (örneğin 3) doküman bulunur.
4.  **Bağlam (Context) Hazırlama:** Bulunan doküman metinleri birleştirilerek Gemini modeline sunulacak bağlam oluşturulur.
5.  **Zenginleştirilmiş Komut (Augmented Prompt):** Hazırlanan bağlam ve kullanıcının orijinal sorusu, Gemini'a özel talimatlar içeren bir komut şablonuna yerleştirilir. Bu şablon, modelin sadece verilen bağlamı kullanmasını ve cevap bağlamda yoksa "Bilmiyorum" demesini söyler.
6.  **Cevap Üretme (Generation):** Zenginleştirilmiş komut, Google Gemini API'sinin güçlü dil modeline (`models/gemini-2.5-flash`) gönderilir.
7.  **Sonuç:** Modelin ürettiği nihai cevap kullanıcıya gösterilir.

**Kullanılan Teknolojiler:**

* **Dataset Loading:** Hugging Face `datasets`
* **Embedding Modeli (Lokal):** `sentence-transformers/all-mpnet-base-v2`
* **Vektör Karşılaştırma:** `scikit-learn` (Cosine Similarity)
* [cite_start]**Generation Modeli:** Google Gemini API (`models/gemini-2.5-flash`) [cite: 42]
* **Web Arayüzü:** Streamlit
* **Deployment:** Streamlit Community Cloud

## [cite_start]4. Elde Edilen Sonuçlar (Results) [cite: 12]

* RAG mimarisi başarıyla uygulanmış ve çalışan bir chatbot prototipi oluşturulmuştur.
* Sistem, SQuAD veri setinin kullanılan bölümünde bulunan konularla ilgili sorulara, ilgili metin parçalarını bularak tutarlı cevaplar üretebilmektedir.
* Veri setinin sınırlı olması nedeniyle, kapsam dışı veya veri setinde cevabı bulunmayan sorulara sistemin halüsinasyon görmek yerine "I couldn't find an answer in the provided documents." şeklinde doğru bir geri bildirim verdiği gözlemlenmiştir. Bu, RAG'ın güvenilirliğini artıran önemli bir özelliktir.
* Lokal embedding modeli kullanımı, API hız limitleri sorununu aşmada ve geliştirme sürecini hızlandırmada etkili olmuştur.

## [cite_start]5. Web Arayüzü & Çalıştırma Kılavuzu (Web Interface & Setup Guide) [cite: 13, 20, 21, 25]

### **Canlı Demo Linki:**

[cite_start][https://rag-app-assistant-24apsjvzcbho79iaanyg4a.streamlit.app/](https://rag-app-assistant-24apsjvzcbho79iaanyg4a.streamlit.app/) **<-- BURAYI KONTROL ET!** [cite: 13]

### **Lokalde Çalıştırma:**

1.  Bu GitHub deposunu klonlayın:
    ```bash
    git clone <repo-linkiniz>
    cd <repo-adini>
    ```
2.  Gerekli kütüphaneleri yükleyin:
    ```bash
    pip install -r requirements.txt
    ```
3.  Google Gemini API anahtarınızı bir ortam değişkeni olarak ayarlayın (veya Streamlit'in secrets mekanizmasını kullanın). Colab dışında `os.environ` kullanmak için:
    ```bash
    # Linux/macOS
    export GOOGLE_API_KEY='AIzaSy...' 
    # Windows (Command Prompt)
    set GOOGLE_API_KEY=AIzaSy...
    # Windows (PowerShell)
    $env:GOOGLE_API_KEY='AIzaSy...'
    ```
    *Not: Streamlit Secrets, deploy edilen uygulamalar için daha güvenli bir yöntemdir.*
4.  Streamlit uygulamasını çalıştırın:
    ```bash
    streamlit run app.py
    ```

Uygulama yerel makinenizde açılacaktır.

import streamlit as st
import pandas as pd
from textblob import TextBlob
import re
from googletrans import Translator

# Configuración de la página
st.set_page_config(
    page_title="Analizador de Texto Simple",
    page_icon="📊",
    layout="wide"
)

# Estilos visuales
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

* {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at top left, rgba(0,217,255,0.18), transparent 35%),
        linear-gradient(135deg, #07111F 0%, #0B1728 45%, #06101D 100%);
    color: #EAF7FF;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #071827 0%, #08111F 100%);
    border-right: 1px solid rgba(0,217,255,0.18);
}

[data-testid="stSidebar"] * {
    color: #EAF7FF;
}

.main-title {
    font-size: 3rem;
    font-weight: 800;
    line-height: 1.1;
    background: linear-gradient(90deg, #00D9FF, #0099FF, #7DEBFF);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.6rem;
}

.hero-card {
    padding: 2rem;
    border-radius: 28px;
    background: rgba(9, 23, 40, 0.82);
    border: 1px solid rgba(0,217,255,0.22);
    box-shadow: 0 24px 70px rgba(0,0,0,0.35);
    margin-bottom: 1.5rem;
}

.feature-card {
    padding: 1.1rem 1.25rem;
    border-radius: 20px;
    background: rgba(255,255,255,0.045);
    border: 1px solid rgba(0,217,255,0.16);
    min-height: 115px;
}

.metric-card {
    padding: 1.2rem;
    border-radius: 22px;
    background: rgba(8, 20, 36, 0.9);
    border: 1px solid rgba(0,217,255,0.18);
    box-shadow: 0 14px 40px rgba(0,0,0,0.20);
}

h1, h2, h3 {
    color: #EAF7FF !important;
    font-weight: 800 !important;
}

p, li, label, span {
    color: #C9E8F6;
}

.stButton > button {
    width: 100%;
    border: none;
    border-radius: 16px;
    padding: 0.8rem 1.2rem;
    background: linear-gradient(90deg, #00D9FF, #0099FF);
    color: #03111F;
    font-weight: 800;
    box-shadow: 0 12px 35px rgba(0,153,255,0.35);
    transition: all 0.25s ease;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 18px 45px rgba(0,217,255,0.45);
    filter: brightness(1.08);
}

textarea, input {
    border-radius: 16px !important;
}

[data-testid="stTextArea"] textarea {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(0,217,255,0.22);
    color: #EAF7FF;
}

[data-testid="stFileUploader"] {
    padding: 1rem;
    border-radius: 20px;
    background: rgba(255,255,255,0.045);
    border: 1px dashed rgba(0,217,255,0.32);
}

[data-testid="stExpander"] {
    background: rgba(255,255,255,0.045);
    border: 1px solid rgba(0,217,255,0.14);
    border-radius: 18px;
}

hr {
    border-color: rgba(0,217,255,0.18);
}

.footer {
    text-align: center;
    color: #9FDFF2;
    padding: 1rem;
    opacity: 0.9;
}
</style>
""", unsafe_allow_html=True)

# Encabezado principal
st.markdown("""
<div class="hero-card">
    <div class="main-title">📝 Analizador de Texto con TextBlob</div>
    <p style="font-size:1.1rem; max-width:900px;">
        Analiza textos en español con traducción automática al inglés para evaluar sentimiento,
        subjetividad, frases detectadas y frecuencia de palabras.
    </p>
</div>
""", unsafe_allow_html=True)

col_a, col_b, col_c = st.columns(3)

with col_a:
    st.markdown("""
    <div class="feature-card">
        <h4>📈 Sentimiento</h4>
        <p>Clasifica el tono del texto como positivo, negativo o neutral.</p>
    </div>
    """, unsafe_allow_html=True)

with col_b:
    st.markdown("""
    <div class="feature-card">
        <h4>💭 Subjetividad</h4>
        <p>Detecta qué tan objetivo o subjetivo es el contenido analizado.</p>
    </div>
    """, unsafe_allow_html=True)

with col_c:
    st.markdown("""
    <div class="feature-card">
        <h4>🔎 Palabras clave</h4>
        <p>Identifica las palabras más frecuentes eliminando palabras vacías.</p>
    </div>
    """, unsafe_allow_html=True)

# Barra lateral
st.sidebar.title("⚙️ Opciones")
st.sidebar.markdown("Configura la forma en que quieres ingresar el texto.")

modo = st.sidebar.selectbox(
    "Selecciona el modo de entrada:",
    ["Texto directo", "Archivo de texto"]
)

# Función para contar palabras sin depender de NLTK
def contar_palabras(texto):
    stop_words = set([
        "a", "al", "algo", "algunas", "algunos", "ante", "antes", "como", "con", "contra",
        "cual", "cuando", "de", "del", "desde", "donde", "durante", "e", "el", "ella",
        "ellas", "ellos", "en", "entre", "era", "eras", "es", "esa", "esas", "ese",
        "eso", "esos", "esta", "estas", "este", "esto", "estos", "ha", "había", "han",
        "has", "hasta", "he", "la", "las", "le", "les", "lo", "los", "me", "mi", "mía",
        "mías", "mío", "míos", "mis", "mucho", "muchos", "muy", "nada", "ni", "no", "nos",
        "nosotras", "nosotros", "nuestra", "nuestras", "nuestro", "nuestros", "o", "os", 
        "otra", "otras", "otro", "otros", "para", "pero", "poco", "por", "porque", "que", 
        "quien", "quienes", "qué", "se", "sea", "sean", "según", "si", "sido", "sin", 
        "sobre", "sois", "somos", "son", "soy", "su", "sus", "suya", "suyas", "suyo", 
        "suyos", "también", "tanto", "te", "tenéis", "tenemos", "tener", "tengo", "ti", 
        "tiene", "tienen", "todo", "todos", "tu", "tus", "tuya", "tuyas", "tuyo", "tuyos", 
        "tú", "un", "una", "uno", "unos", "vosotras", "vosotros", "vuestra", "vuestras", 
        "vuestro", "vuestros", "y", "ya", "yo",
        "about", "above", "after", "again", "against", "all", "am", "an", "and", 
        "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being", 
        "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't", 
        "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during", 
        "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", "have", 
        "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", 
        "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", 
        "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", 
        "let's", "more", "most", "mustn't", "my", "myself", "nor", "of", "off", "on",
        "once", "only", "other", "ought", "our", "ours", "ourselves", "out", "over",
        "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should",
        "shouldn't", "so", "some", "such", "than", "that", "that's", "the", "their",
        "theirs", "them", "themselves", "then", "there", "there's", "these", "they",
        "they'd", "they'll", "they're", "they've", "this", "those", "through", "to",
        "too", "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll",
        "we're", "we've", "were", "weren't", "what", "what's", "when", "when's",
        "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's",
        "with", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've",
        "your", "yours", "yourself", "yourselves"
    ])
    
    palabras = re.findall(r'\b\w+\b', texto.lower())
    palabras_filtradas = [
        palabra for palabra in palabras
        if palabra not in stop_words and len(palabra) > 2
    ]
    
    contador = {}
    for palabra in palabras_filtradas:
        contador[palabra] = contador.get(palabra, 0) + 1
    
    contador_ordenado = dict(sorted(contador.items(), key=lambda x: x[1], reverse=True))
    
    return contador_ordenado, palabras_filtradas

# Inicializar el traductor
translator = Translator()

# Función para traducir texto del español al inglés
def traducir_texto(texto):
    try:
        traduccion = translator.translate(texto, src='es', dest='en')
        return traduccion.text
    except Exception as e:
        st.error(f"Error al traducir: {e}")
        return texto

# Función para procesar el texto con TextBlob
def procesar_texto(texto):
    texto_original = texto
    texto_ingles = traducir_texto(texto)
    blob = TextBlob(texto_ingles)
    
    sentimiento = blob.sentiment.polarity
    subjetividad = blob.sentiment.subjectivity
    
    frases_originales = [
        frase.strip() for frase in re.split(r'[.!?]+', texto_original)
        if frase.strip()
    ]
    
    frases_traducidas = [
        frase.strip() for frase in re.split(r'[.!?]+', texto_ingles)
        if frase.strip()
    ]
    
    frases_combinadas = []
    for i in range(min(len(frases_originales), len(frases_traducidas))):
        frases_combinadas.append({
            "original": frases_originales[i],
            "traducido": frases_traducidas[i]
        })
    
    contador_palabras, palabras = contar_palabras(texto_ingles)
    
    return {
        "sentimiento": sentimiento,
        "subjetividad": subjetividad,
        "frases": frases_combinadas,
        "contador_palabras": contador_palabras,
        "palabras": palabras,
        "texto_original": texto_original,
        "texto_traducido": texto_ingles
    }

# Función para crear visualizaciones
def crear_visualizaciones(resultados):
    st.markdown("## 📊 Resultados del análisis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.subheader("Análisis de Sentimiento y Subjetividad")
        
        sentimiento_norm = (resultados["sentimiento"] + 1) / 2
        
        st.write("**Sentimiento:**")
        st.progress(sentimiento_norm)
        
        if resultados["sentimiento"] > 0.05:
            st.success(f"📈 Positivo ({resultados['sentimiento']:.2f})")
        elif resultados["sentimiento"] < -0.05:
            st.error(f"📉 Negativo ({resultados['sentimiento']:.2f})")
        else:
            st.info(f"📊 Neutral ({resultados['sentimiento']:.2f})")
        
        st.write("**Subjetividad:**")
        st.progress(resultados["subjetividad"])
        
        if resultados["subjetividad"] > 0.5:
            st.warning(f"💭 Alta subjetividad ({resultados['subjetividad']:.2f})")
        else:
            st.info(f"📋 Baja subjetividad ({resultados['subjetividad']:.2f})")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.subheader("Palabras más frecuentes")
        if resultados["contador_palabras"]:
            palabras_top = dict(list(resultados["contador_palabras"].items())[:10])
            st.bar_chart(palabras_top)
        else:
            st.info("No se encontraron palabras relevantes.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("## 🌐 Texto traducido")
    with st.expander("Ver traducción completa"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Texto Original (Español):**")
            st.text(resultados["texto_original"])
        
        with col2:
            st.markdown("**Texto Traducido (Inglés):**")
            st.text(resultados["texto_traducido"])
    
    st.markdown("## 🧩 Frases detectadas")
    
    if resultados["frases"]:
        for i, frase_dict in enumerate(resultados["frases"][:10], 1):
            frase_original = frase_dict["original"]
            frase_traducida = frase_dict["traducido"]
            
            try:
                blob_frase = TextBlob(frase_traducida)
                sentimiento = blob_frase.sentiment.polarity
                
                if sentimiento > 0.05:
                    emoji = "😊"
                elif sentimiento < -0.05:
                    emoji = "😟"
                else:
                    emoji = "😐"
                
                st.write(f"{i}. {emoji} **Original:** *\"{frase_original}\"*")
                st.write(f"   **Traducción:** *\"{frase_traducida}\"* (Sentimiento: {sentimiento:.2f})")
                st.write("---")
            except:
                st.write(f"{i}. **Original:** *\"{frase_original}\"*")
                st.write(f"   **Traducción:** *\"{frase_traducida}\"*")
                st.write("---")
    else:
        st.write("No se detectaron frases.")

# Lógica principal según el modo seleccionado
st.markdown("## ✍️ Entrada de texto")

if modo == "Texto directo":
    st.subheader("Escribe o pega tu texto")
    texto = st.text_area(
        "",
        height=220,
        placeholder="Escribe o pega aquí el texto que deseas analizar..."
    )
    
    if st.button("Analizar texto"):
        if texto.strip():
            with st.spinner("Analizando texto..."):
                resultados = procesar_texto(texto)
                crear_visualizaciones(resultados)
        else:
            st.warning("Por favor, ingresa algún texto para analizar.")

elif modo == "Archivo de texto":
    st.subheader("Carga un archivo de texto")
    archivo = st.file_uploader("", type=["txt", "csv", "md"])
    
    if archivo is not None:
        try:
            contenido = archivo.getvalue().decode("utf-8")
            
            with st.expander("Ver contenido del archivo"):
                st.text(contenido[:1000] + ("..." if len(contenido) > 1000 else ""))
            
            if st.button("Analizar archivo"):
                with st.spinner("Analizando archivo..."):
                    resultados = procesar_texto(contenido)
                    crear_visualizaciones(resultados)
        
        except Exception as e:
            st.error(f"Error al procesar el archivo: {e}")

# Información adicional
with st.expander("📚 Información sobre el análisis"):
    st.markdown("""
    ### Sobre el análisis de texto
    
    - **Sentimiento**: varía de -1, muy negativo, a 1, muy positivo.
    - **Subjetividad**: varía de 0, muy objetivo, a 1, muy subjetivo.
    
    ### Requisitos mínimos
    
    Esta aplicación utiliza:
    
    ```txt
    streamlit
    textblob
    pandas
    googletrans
    ```
    """)

# Pie de página
st.markdown("---")
st.markdown(
    '<div class="footer">Desarrollado con ❤️ usando Streamlit y TextBlob</div>',
    unsafe_allow_html=True
)

import streamlit as st
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import io

try:
    import PyPDF2
except ImportError:
    st.error("🔧 **PyPDF2 missing!** Add to requirements.txt")
    st.stop()

from openai import OpenAI

st.set_page_config(page_title="PDF Q&A", layout="wide")
st.title("📄 PDF Q&A Bot")

# API Key
api_key = st.sidebar.text_input("🔑 OpenAI API Key", type="password")
if not api_key:
    st.stop()

client = OpenAI(api_key=api_key)

@st.cache_data
def pdf_to_text(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text

def split_text(text, chunk_size=400):
    words = text.split()
    return [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), 200)]

uploaded_file = st.file_uploader("📁 Upload PDF", type="pdf")

if uploaded_file:
    text = pdf_to_text(uploaded_file)
    chunks = split_text(text)
    st.session_state.chunks = chunks
    
    with st.spinner("Creating embeddings..."):
        embeddings = []
        for chunk in chunks:
            emb = client.embeddings.create(input=chunk, model="text-embedding-3-small").data[0].embedding
            embeddings.append(emb)
        st.session_state.embeddings = np.array(embeddings)
    
    st.success(f"✅ Ready! {len(chunks)} chunks")

if "embeddings" in st.session_state:
    question = st.text_input("💬 Ask question:")
    if question:
        q_emb = client.embeddings.create(input=question, model="text-embedding-3-small").data[0].embedding
        similarities = cosine_similarity([q_emb], st.session_state.embeddings)[0]
        top_idx = np.argmax(similarities)
        
        context = st.session_state.chunks[top_idx]
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": f"Context: {context}\n\nQuestion: {question}\nAnswer:"}]
        )
        
        st.write(f"**Q:** {question}")
        st.write(f"**A:** {response.choices[0].message.content}")
        st.caption(f"Score: {similarities[top_idx]:.1%}")

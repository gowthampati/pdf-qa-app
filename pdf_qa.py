import streamlit as st
try:
    import PyPDF2
except ImportError:
    st.error("Install PyPDF2: pip install PyPDF2")
    st.stop()

from openai import OpenAI
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(page_title="PDF Q&A", layout="wide")

st.title("📄 PDF Question Answering")
st.markdown("*Upload PDF → Ask questions → Get GPT answers!*")

# API Key (Secret management)
api_key = st.sidebar.text_input("🔑 OpenAI API Key", type="password")
if not api_key:
    st.info("👈 **Get free key:** [platform.openai.com/api-keys](https://platform.openai.com/api-keys)")
    st.stop()

@st.cache_data
def extract_text(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    return "".join([page.extract_text() or "" for page in reader.pages])

def chunk_text(text, size=500):
    words = text.split()
    return [" ".join(words[i:i+size]) for i in range(0, len(words), size//2)]

# File upload
uploaded_file = st.file_uploader("📁 **Upload PDF**", type="pdf")

if uploaded_file:
    with st.spinner("🔄 Extracting text..."):
        text = extract_text(uploaded_file)
        if not text.strip():
            st.error("❌ No text found in PDF!")
            st.stop()
        
        chunks = chunk_text(text)
        st.session_state.chunks = chunks
        st.success(f"✅ **{len(chunks)} chunks** extracted")
        
        st.caption("**Preview:** " + text[:200] + "...")

# Embeddings
client = OpenAI(api_key=api_key)
if "chunks" in st.session_state and "embeddings" not in st.session_state:
    with st.spinner("🧠 Creating embeddings..."):
        try:
            st.session_state.embeddings = np.array([
                client.embeddings.create(
                    input=chunk[:8192],  # Token limit
                    model="text-embedding-3-small"
                ).data[0].embedding
                for chunk in st.session_state.chunks
            ])
            st.success("✅ **Embeddings ready!** Ask away 👇")
        except Exception as e:
            st.error(f"❌ OpenAI Error: {str(e)[:100]}")
            st.info("💡 Check API key & quota")

# Question Answering
if "embeddings" in st.session_state:
    col1, col2 = st.columns([3, 1])
    
    with col1:
        question = st.text_input("💬 **Ask about the PDF:**")
    
    with col2:
        if st.button("🗑️ **Clear**"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    if question:
        with st.spinner("🔍 Searching... 🤖 Answering..."):
            # Similarity search
            q_embedding = np.array([client.embeddings.create(
                input=question, model="text-embedding-3-small"
            ).data[0].embedding])
            
            similarities = cosine_similarity(q_embedding, st.session_state.embeddings)[0]
            top_indices = np.argsort(similarities)[-3:][::-1]
            
            context = "\n\n".join([st.session_state.chunks[i] for i in top_indices])
            
            # GPT Answer
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{
                    "role": "user",
                    "content": f"""Answer using ONLY this context. 
If not found, say "I don't know".

CONTEXT:
{context}

QUESTION: {question}

ANSWER:"""
                }],
                temperature=0.1,
                max_tokens=300
            )
            
            answer = response.choices[0].message.content.strip()
            
            # Results
            st.markdown("---")
            st.markdown(f"### ❓ **{question}**")
            st.markdown(f"### 🤖 **{answer}**")
            
            with st.expander("📊 **Context & Scores**"):
                for i, idx in enumerate(top_indices):
                    st.caption(f"**{i+1}.** {similarities[idx]:.1%} | {st.session_state.chunks[idx][:200]}...")

st.markdown("---")
st.markdown("*Made with ❤️ using Streamlit + OpenAI*")

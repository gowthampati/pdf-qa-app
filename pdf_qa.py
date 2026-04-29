import streamlit as st
import PyPDF2
import openai
from openai import OpenAI
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import tiktoken
import re

# Page config
st.set_page_config(page_title="PDF Q&A", page_icon="📄", layout="wide")

# Sidebar for API key
st.sidebar.title("Configuration")
openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password", help="Enter your OpenAI API key")
if not openai_api_key:
    st.sidebar.warning("Please add your OpenAI API key to continue.")
    st.stop()

client = OpenAI(api_key=openai_api_key)

# Initialize session state
if "documents" not in st.session_state:
    st.session_state.documents = []
if "embeddings" not in st.session_state:
    st.session_state.embeddings = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Custom functions
@st.cache_data
def extract_text_from_pdf(pdf_file):
    """Extract text from PDF file"""
    text = ""
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text

def split_text(text, chunk_size=1000, chunk_overlap=200):
    """Split text into overlapping chunks"""
    chunks = []
    words = text.split()
    for i in range(0, len(words), chunk_size - chunk_overlap):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks

def get_embedding(text, model="text-embedding-ada-002"):
    """Get embedding from OpenAI"""
    response = client.embeddings.create(
        input=text,
        model=model
    )
    return np.array(response.data[0].embedding)

def cosine_similarity_search(query_embedding, document_embeddings, documents, top_k=3):
    """Find most similar documents using cosine similarity"""
    similarities = cosine_similarity([query_embedding], document_embeddings)[0]
    top_indices = np.argsort(similarities)[::-1][:top_k]
    return [documents[i] for i in top_indices], similarities[top_indices]

def get_gpt_response(question, context, model="gpt-3.5-turbo"):
    """Generate answer using GPT with context"""
    prompt = f"""Use the following context to answer the question. If the answer is not in the context, say "I don't know".

Context:
{context}

Question: {question}

Answer:"""
    
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=500
    )
    return response.choices[0].message.content.strip()

# Main app
st.title("📄 PDF Question Answering")
st.markdown("Upload a PDF and ask questions about its content!")

# File uploader
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    # Process PDF
    with st.spinner("Processing PDF..."):
        text = extract_text_from_pdf(uploaded_file)
        chunks = split_text(text)
        
        # Create embeddings
        st.session_state.documents = chunks
        st.session_state.embeddings = []
        progress_bar = st.progress(0)
        
        for i, chunk in enumerate(chunks):
            embedding = get_embedding(chunk)
            st.session_state.embeddings.append(embedding)
            progress_bar.progress((i + 1) / len(chunks))
        
        st.session_state.embeddings = np.array(st.session_state.embeddings)
        st.success(f"✅ PDF processed! Created {len(chunks)} chunks with embeddings.")
        
        st.info(f"Document preview (first 500 chars):")
        st.text(text[:500] + "..." if len(text) > 500 else text)

# Chat interface
col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("💬 Ask a question")
    question = st.text_input("Enter your question:", key="question_input")

with col2:
    if st.button("Clear Chat", type="secondary"):
        st.session_state.chat_history = []
        st.rerun()

if question and len(st.session_state.documents) > 0:
    with st.spinner("Searching and generating answer..."):
        # Get query embedding
        query_embedding = get_embedding(question)
        
        # Find relevant chunks
        relevant_chunks, scores = cosine_similarity_search(
            query_embedding, 
            st.session_state.embeddings, 
            st.session_state.documents
        )
        
        context = "\n\n".join(relevant_chunks)
        
        # Generate answer
        answer = get_gpt_response(question, context)
        
        # Store in chat history
        st.session_state.chat_history.append({
            "question": question,
            "answer": answer,
            "context": context[:1000] + "..." if len(context) > 1000 else context,
            "scores": scores
        })
        
        question = ""  # Clear input

# Display chat history
if st.session_state.chat_history:
    st.subheader("📚 Chat History")
    
    for i, chat in enumerate(st.session_state.chat_history[-10:], 1):  # Show last 10
        with st.expander(f"Q: {chat['question'][:100]}..."):
            st.markdown(f"**Answer:** {chat['answer']}")
            
            with st.expander("📋 Context & Scores"):
                col1, col2 = st.columns(2)
                with col1:
                    st.text_area("Context", chat['context'], height=150, disabled=True)
                with col2:
                    st.metric("Similarity Scores", f"{chat['scores'][0]:.3f}, {chat['scores'][1]:.3f}, {chat['scores'][2]:.3f}")

# Instructions
with st.expander("ℹ️ How to use"):
    st.markdown("""
    1. **Add your OpenAI API key** in the sidebar
    2. **Upload a PDF** file
    3. **Wait for processing** (creates embeddings)
    4. **Ask questions** about the PDF content
    5. **View answers** with relevant context
    
    **Features:**
    - Semantic search using embeddings
    - Cosine similarity ranking
    - GPT-powered answers with context
    - "I don't know" if answer not found
    - Chat history with context preview
    """)

# Footer
st.markdown("---")
st.markdown("Built with ❤️ using Streamlit + OpenAI")
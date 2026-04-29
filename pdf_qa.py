# Add this to your pdf_qa.py for React-like components!

import streamlit as st
import streamlit.components.v1 as components

# Custom React-like UI Components
def ChatBubble(message, isUser=True, score=None):
    """React-style chat bubble"""
    with st.container():
        col1, col2 = st.columns([1, 10])
        with col1:
            if isUser:
                st.markdown("👤")
            else:
                st.markdown("🤖")
        with col2:
            bg_color = "#E3F2FD" if isUser else "#F5F5F5"
            st.markdown(
                f"""
                <div style='background-color: {bg_color}; 
                           padding: 12px 16px; 
                           border-radius: 18px; 
                           margin: 8px 0;
                           box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                    {message}
                </div>
                """, 
                unsafe_allow_html=True
            )
            if score:
                st.caption(f"🔍 Confidence: {score:.1%}", help="Cosine similarity score")

def ProgressCard(title, progress, color="blue"):
    """React-style progress card"""
    st.markdown(
        f"""
        <div style='background: white; 
                    padding: 16px; 
                    border-radius: 12px; 
                    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                    border-left: 4px solid {color};'>
            <h4 style='margin: 0 0 8px 0; color: #333;'>{title}</h4>
            <div style='background: #f0f0f0; height: 8px; border-radius: 4px; overflow: hidden;'>
                <div style='background: {color}; height: 100%; width: {progress*100}\%; transition: width 0.3s ease;'></div>
            </div>
            <small style='color: #666; margin-top: 4px;'>{progress*100:.0f}%</small>
        </div>
        """, 
        unsafe_allow_html=True
    )

def FileCard(filename, size, status="ready"):
    """React-style file upload card"""
    status_color = {"ready": "#4CAF50", "processing": "#FF9800", "error": "#F44336"}[status]
    st.markdown(
        f"""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white; padding: 20px; border-radius: 16px; 
                    text-align: center; box-shadow: 0 8px 32px rgba(0,0,0,0.2);'>
            <div style='font-size: 48px; margin-bottom: 12px;'>📄</div>
            <h3 style='margin: 0 0 8px 0;'>{filename}</h3>
            <p style='margin: 0 0 12px 0; opacity: 0.9;'>{size} MB</p>
            <div style='width: 24px; height: 24px; border: 3px solid {status_color};
                        border-top: 3px solid transparent; 
                        border-radius: 50%; animation: spin 1s linear infinite;
                        display: inline-block;'>
            </div>
        </div>
        <style>
        @keyframes spin {{ 0\% {{ transform: rotate(0deg); }} 100\% {{ transform: rotate(360deg); }} }}
        </style>
        """, 
        unsafe_allow_html=True
    )

# Enhanced UI with React-style components
st.title("📄 PDF Q&A Bot")
st.markdown("### Modern UI with React-inspired Components")

# File Upload with Card
uploaded_file = st.file_uploader("Choose PDF", type="pdf", help="Supports up to 100MB")
if uploaded_file:
    FileCard(uploaded_file.name, f"{uploaded_file.size/1e6:.1f}", "processing")

# Progress Cards
if st.button("🔄 Process PDF"):
    col1, col2, col3 = st.columns(3)
    with col1:
        ProgressCard("Text Extraction", 0.7)
    with col2:
        ProgressCard("Embeddings", 0.4, "#FF6B6B")
    with col3:
        ProgressCard("Ready to Query", 0.2, "#4ECDC4")

# Chat Interface
st.markdown("---")
st.markdown("### 💬 Chat")

if "messages" not in st.session_state:
    st.session_state.messages = []

question = st.text_input("Ask about PDF:")
if st.button("Send") and question:
    # Simulate response
    ChatBubble(question, isUser=True)
    with st.spinner("Thinking..."):
        st.session_state.messages.append({"text": "AI processes PDF using embeddings and cosine similarity to find relevant chunks, then GPT generates answer.", "score": 0.92})
    
for msg in st.session_state.messages[-3:]:
    ChatBubble(msg["text"], isUser=False, score=msg.get("score"))

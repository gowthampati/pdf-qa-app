How it Works (30 sec)
mermaid

Copy code
graph TD
    A[PDF Upload] --> B[Extract Text<br/>PyPDF2]
    B --> C[Split Chunks<br/>400 words each]
    C --> D[OpenAI Embeddings<br/>1536D vectors]
    E[Your Question] --> F[Q Embedding]
    F --> G[Cosine Similarity<br/>Top 3 matches]
    G --> H[GPT-4o-mini Answer]
    H --> I[✅ Final Answer]
🚀 Quick Start
Local Run
bash

Copy code
pip install -r requirements.txt
streamlit run pdf_qa.py
Deploy Live (Free!)
Fork this repo
Streamlit Cloud → Deploy
Add OpenAI API key
✅ Live in 2 mins!
🔑 Get OpenAI API Key (Free $5 credit)
platform.openai.com
Create account → New secret key
Copy → Paste in app sidebar
🛠️ Tech Stack

Copy code
Frontend: Streamlit
PDF: PyPDF2
Search: OpenAI Embeddings + Cosine Similarity
AI: GPT-4o-mini
Math: NumPy + scikit-learn
Deployment: Streamlit Cloud
📊 Features
✅ Semantic Search - Understands meaning, not just keywords
✅ GPT Answers - Context-aware responses
✅ Safety - "I don't know" if no match
✅ Fast - <2 sec response
✅ Cheap - ₹0.05 per PDF
✅ Mobile-friendly
💾 File Structure

Copy code
pdf-qa-app/
├── pdf_qa.py          # Main app
├── requirements.txt   # Dependencies
├── README.md         # This file!
└── .streamlit/       # Theme config

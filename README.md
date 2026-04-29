graph TD
    A[PDF Upload] --> B[Extract Text<br/>PyPDF2]
    B --> C[Split Chunks<br/>400 words each]
    C --> D[OpenAI Embeddings<br/>1536D vectors]
    E[Your Question] --> F[Q Embedding]
    F --> G[Cosine Similarity<br/>Top 3 matches]
    G --> H[GPT-4o-mini Answer]
    H --> I[✅ Final Answer]

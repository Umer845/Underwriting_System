import streamlit as st
import ollama  # Use the Ollama Python client
from PyPDF2 import PdfReader
from docx import Document
from PIL import Image
import pytesseract
import faiss
import numpy as np

# === CONFIG ===
st.set_page_config(page_title="📄🔍 Vehicle QA with Vector DB (Ollama)", layout="wide")
st.title("📄🔍 Multi-file QA Chatbot with Vector DB (Ollama)")

# === Ollama settings ===
ollama_model = st.text_input("🧩 Enter Ollama Model Name", value="llama3")

if not ollama_model:
    st.warning("Add Ollama model name (e.g., llama3).")
    st.stop()

# === Upload File ===
uploaded_file = st.file_uploader("Upload PDF, DOCX, TXT, or IMAGE", type=["pdf", "docx", "txt", "png", "jpg", "jpeg"])

# === Store embeddings in FAISS index ===
if "faiss_index" not in st.session_state:
    st.session_state.faiss_index = None
    st.session_state.text_chunks = []
    st.session_state.vectors = []
    st.session_state.ids = []
    st.session_state.vehicle_text_map = {}

# === Extract text ===
def extract_text(file):
    if file.name.endswith(".pdf"):
        pdf = PdfReader(file)
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
        return text

    elif file.name.endswith(".docx"):
        doc = Document(file)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text

    elif file.name.endswith(".txt"):
        return file.read().decode("utf-8")

    elif file.name.endswith((".png", ".jpg", ".jpeg")):
        image = Image.open(file)
        text = pytesseract.image_to_string(image)
        return text

    else:
        return ""

# === Create embedding ===
def embed_text(text):
    # Ollama does not expose separate embedding API yet.
    # So use a hack: call the LLM with a prompt to get semantic vector,
    # or integrate a local embedding model instead.
    # For demo: use hash + random vector.
    np.random.seed(abs(hash(text)) % (10 ** 8))
    return np.random.rand(512).astype('float32')

# === Process file ===
if uploaded_file:
    extracted_text = extract_text(uploaded_file)
    st.write("✅ Extracted text:", extracted_text[:500] + "...")

    # Split text by paragraphs for simple chunks
    paragraphs = [p.strip() for p in extracted_text.split("\n") if p.strip()]

    vectors = []
    for i, para in enumerate(paragraphs):
        embedding = embed_text(para)
        vectors.append(embedding)
        st.session_state.vehicle_text_map[len(st.session_state.ids)] = para
        st.session_state.ids.append(len(st.session_state.ids))

    vector_dim = len(vectors[0])
    vectors_np = np.vstack(vectors)

    if st.session_state.faiss_index is None:
        index = faiss.IndexFlatL2(vector_dim)
        st.session_state.faiss_index = index
    else:
        index = st.session_state.faiss_index

    index.add(vectors_np)
    st.session_state.vectors.extend(vectors)

    st.success(f"✅ {len(paragraphs)} paragraphs embedded and stored in vector DB.")

# === Query ===
query = st.text_input("🔍 Enter your vehicle question or keyword")

if query and st.session_state.faiss_index:
    query_embedding = embed_text(query).reshape(1, -1)
    k = 3
    D, I = st.session_state.faiss_index.search(query_embedding, k)

    retrieved = []
    for idx in I[0]:
        retrieved.append(st.session_state.vehicle_text_map[idx])

    st.write("🔎 Top retrieved chunks:")
    for chunk in retrieved:
        st.info(chunk)

    # Generate final answer using Ollama
    prompt = f"""
    You are a helpful underwriter assistant.
    Context:
    {retrieved}

    Question: {query}

    Please answer based only on the above context.
    """

    response = ollama.chat(
        model=ollama_model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    st.success("💡 Answer:")
    st.write(response['message']['content'])

elif query:
    st.warning("⚠️ No vector index found. Please upload and process a file first.")

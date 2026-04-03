import os
import streamlit as st
from rag_pipeline import create_vector_store, get_answer

st.set_page_config(page_title="DocuQuery", layout="wide")

st.title("DocuQuery - PDF Question Answering")

st.write("Upload a PDF and ask questions based on its content.")

if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None

uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

if uploaded_file is not None:
    os.makedirs("uploads", exist_ok=True)
    file_path = os.path.join("uploads", uploaded_file.name)

    with open(file_path, "wb") as f:
        f.write(uploaded_file.read())

    with st.spinner("Processing document..."):
        st.session_state.vectorstore = create_vector_store(file_path)

    st.success("Document ready!")

if st.session_state.vectorstore:
    query = st.text_input("Enter your question")

    if query:
        with st.spinner("Generating answer..."):
            answer, docs = get_answer(st.session_state.vectorstore, query)

        st.subheader("Answer")
        st.write(answer)

        with st.expander("View Retrieved Context"):
            for i, doc in enumerate(docs):
                st.markdown(f"**Chunk {i+1}:**")
                st.write(doc.page_content)
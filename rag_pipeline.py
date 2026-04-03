from dotenv import load_dotenv
load_dotenv()

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.embeddings import HuggingFaceEmbeddings


def create_vector_store(file_path):     
    loader = PyPDFLoader(file_path)
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=120
    )
    chunks = splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vectorstore = FAISS.from_documents(chunks, embeddings)

    return vectorstore


def format_context(docs):
    context_parts = []
    for i, doc in enumerate(docs):
        context_parts.append(f"Chunk {i+1}:\n{doc.page_content}")
    return "\n\n".join(context_parts)


def get_answer(vectorstore, query):
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

    docs = retriever.invoke(query)

    if not docs:
        return "No relevant content found.", []

    context = format_context(docs)

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0
    )

    prompt = f"""
You are a helpful assistant answering questions strictly based on the provided context.

Rules:
- Only use the information from the context
- If the answer is not in the context, say: "I could not find this in the document"
- Do not make up information
- Keep answers clear and concise

Context:
{context}

Question:
{query}

Answer:
"""

    response = llm.invoke(prompt)
    return response.content, docs
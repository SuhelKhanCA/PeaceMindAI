from langchain_community.document_loaders import JSONLoader
import json
from pathlib import Path
import os

# Set USER_AGENT environment variable
os.environ["USER_AGENT"] = "PeaceMindAI/1.0"

file_path1 = Path('C:\\Users\\suhel\\Documents\\GitHub\\PeaceMindAI\\peacemindai\\chat\\data_source\\Intents.json')
file_path2 = Path('C:\\Users\\suhel\\Documents\\GitHub\\PeaceMindAI\\peacemindai\\chat\\data_source\\Huggingface-mental-health-data.json')

from langchain_community.document_loaders import JSONLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_core.documents import Document
from langchain_groq import ChatGroq
from langchain.memory import ConversationBufferMemory
import json
import os

from dotenv import load_dotenv
load_dotenv()

# -------- Initialize the LLM --------
def initialize_llm():
    llm = ChatGroq(
        temperature=0,
        groq_api_key=os.getenv('API_KEY'),
        # groq_api_key="",
        model_name="llama-3.3-70b-versatile"
    )
    return llm

# -------- Load JSON and PDF Data --------
def load_documents():
    docs = []

    # Load and flatten Intents.json
    with open(file_path1, "r", encoding="utf-8") as f:
        intent_data = json.load(f)
    for intent in intent_data["intents"]:
        patterns = "; ".join(intent.get("patterns", []))
        responses = " ".join(intent.get("responses", []))
        content = f"Intent: {intent['tag']}\nUser Patterns: {patterns}\nBot Responses: {responses}"
        docs.append(Document(page_content=content, metadata={"source": "intents"}))

# Load and clean Huggingface mental health data
    loader_hf = JSONLoader(
        file_path=file_path2,
        jq_schema=".rows[]",
        content_key=".row.text",
        is_content_key_jq_parsable=True,
        text_content=True
    )
    hf_docs = loader_hf.load()
    for doc in hf_docs:
        text = doc.page_content.replace("<HUMAN>:", "").replace("<ASSISTANT>:", "").strip()
        docs.append(Document(page_content=text, metadata={"source": "huggingface"}))

    # Load PDF
    pdf_loader = PyPDFLoader("C:\\Users\\suhel\\Documents\\GitHub\\PeaceMindAI\\peacemindai\\chat\\data_source\\mental_health_Document.pdf")
    pdf_docs = pdf_loader.load()
    docs.extend(pdf_docs)

    # Web Based Loader
    w_loader=WebBaseLoader("https://www.who.int/news-room/questions-and-answers/item/stress")
    w_doc=w_loader.load()
    docs.extend(w_doc)
    return docs

# -------- Create or Load Vector DB --------
def create_or_load_vector_db(docs, db_path="./chroma_db"):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    split_docs = text_splitter.split_documents(docs)

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    if not os.path.exists(db_path):
        vector_db = Chroma.from_documents(split_docs, embeddings, persist_directory=db_path)
        vector_db.persist()
    else:
        vector_db = Chroma(persist_directory=db_path, embedding_function=embeddings)

    return vector_db

# -------- Setup QA Chain --------
def setup_qa_chain(vector_db, llm):
    retriever = vector_db.as_retriever()
    prompt_template = """
    You are a compassionate AI Psychotherapist with expertise in mental health counseling.
    
    Previous Conversation History:
    {chat_history}
    
    Context from Knowledge Base:
    {context}
    
    Current User Query: {question}
    
    Instructions:
    - For the greetings word Hi, Hello, Hey , hlow, hye greet them back in one sentence only
    - Keep response brief as possible in the beggining of conversation until user has asked 4 to 5 questions
    - Use the provided context and conversation history to provide a comprehensive and empathetic response
    - Maintain consistency with previous responses and build upon the conversation
    - If the context doesn't contain relevant information, rely on your training as a mental health professional
    - Always maintain a supportive and non-judgmental tone
    - If the user is in crisis or needs immediate help, provide appropriate crisis resources
    - Keep responses focused on mental health and emotional well-being
    - Ensure responses are clear, actionable, and helpful
    
    Response:
    """
    PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question", "chat_history"])
    
    # Create a memory object to store chat history
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        input_key="question",
        return_messages=True
    )
    
    # Create a custom chain that combines retrieval and memory
    from langchain.chains import ConversationalRetrievalChain
    
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        combine_docs_chain_kwargs={"prompt": PROMPT}
    )
    return qa_chain

# -------- Main Function --------
def main():
    print("Initializing PeaceMindAI Mental Health Chatbot...")
    llm = initialize_llm()

    docs = load_documents()
    vector_db = create_or_load_vector_db(docs)

    qa_chain = setup_qa_chain(vector_db, llm)

    while True:
        query = input("\nHuman: ")
        if query.lower() in ["exit", "quit", "bye"]:
            print("Chatbot: Take care of yourself. Goodbye!")
            break
        response = qa_chain.run(query)
        print(f"Chatbot: {response}")

if __name__ == "__main__":
    main()
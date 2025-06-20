import streamlit as st
import os
import re
import requests
from bs4 import BeautifulSoup
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from PyPDF2 import PdfReader
import pytesseract
from PIL import Image
import pandas as pd
import uuid

# Set Streamlit page config
st.set_page_config(page_title="AI Document Chatbot", page_icon="📚", layout="wide")

# Inject Tailwind CSS and custom styles
st.markdown(
    """
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <style>
        body {
            font-family: 'Inter', sans-serif;
            background-color: #f9fafb;
        }
        .sidebar .sidebar-content {
            background-color: #ffffff;
            border-right: 1px solid #e5e7eb;
        }
        .stButton>button {
            background-color: #2563eb;
            color: white;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            font-weight: 500;
        }
        .stButton>button:hover {
            background-color: #1d4ed8;
        }
        .question-input {
            border: 1px solid #d1d5db;
            border-radius: 8px;
            padding: 0.75rem;
            width: 100%;
        }
        .answer-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
        }
        .answer-table th, .answer-table td {
            border: 1px solid #e5e7eb;
            padding: 0.75rem;
            text-align: left;
        }
        .answer-table th {
            background-color: #f3f4f6;
            font-weight: 600;
            color: #374151;
        }
        .answer-table td {
            background-color: #ffffff;
            color: #4b5563;
        }
        .answer-table tr:hover {
            background-color: #f9fafb;
        }
        .answer-table a {
            color: #2563eb;
            text-decoration: none;
        }
        .answer-table a:hover {
            text-decoration: underline;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# App Header
st.markdown(
    """
    <div class="text-center">
        <h1 class="text-3xl font-bold text-gray-900 mb-2">📚 AI Document Chatbot</h1>
        <p class="text-gray-600">Upload documents or add URLs, ask questions, and get accurate answers with citations and themes.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Sidebar: API Key, Document Upload, and URL Input
st.sidebar.header("⚙️ Configuration")
api_key = st.sidebar.text_input(
    "Google Gemini API Key",
    type="password",
    help="Required for Google Generative AI services.",
)

if api_key:
    os.environ["GOOGLE_API_KEY"] = api_key

st.sidebar.header("📂 Upload Documents")
uploaded_files = st.sidebar.file_uploader(
    "Upload PDFs, images (JPG/PNG), or text files",
    type=["pdf", "jpg", "png", "txt"],
    accept_multiple_files=True,
)

st.sidebar.header("🌐 Add URL")
url_input = st.sidebar.text_input(
    "Enter a URL to fetch content from:",
    placeholder="https://example.com",
)

# Cache document metadata
@st.cache_data
def extract_text_from_file(file, file_name):
    """
    Extracts text from PDF, image, or text file, handling encoding issues.
    """
    try:
        text = ""
        metadata = []
        if file_name.endswith(".pdf"):
            pdf_reader = PdfReader(file)
            for page_num, page in enumerate(pdf_reader.pages, 1):
                page_text = page.extract_text() or ""
                page_text = re.sub(r'[\ud800-\udfff]', '', page_text)
                text += page_text
                metadata.append({"doc_id": str(uuid.uuid4()), "page": page_num, "text": page_text, "source": file_name})
        elif file_name.endswith((".jpg", ".png")):
            img = Image.open(file)
            page_text = pytesseract.image_to_string(img)
            page_text = re.sub(r'[\ud800-\udfff]', '', page_text)
            text += page_text
            metadata.append({"doc_id": str(uuid.uuid4()), "page": 1, "text": page_text, "source": file_name})
        elif file_name.endswith(".txt"):
            page_text = file.read().decode("utf-8", errors="ignore")
            page_text = re.sub(r'[\ud800-\udfff]', '', page_text)
            text += page_text
            metadata.append({"doc_id": str(uuid.uuid4()), "page": 1, "text": page_text, "source": file_name})
        return text, metadata
    except Exception as e:
        st.error(f"Error processing {file_name}: {e}")
        return "", []

@st.cache_data
def extract_text_from_url(url):
    """
    Extracts text from a URL using requests and BeautifulSoup.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        # Extract text from paragraphs, headings, etc.
        text = ""
        for tag in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            tag_text = tag.get_text(strip=True)
            tag_text = re.sub(r'[\ud800-\udfff]', '', tag_text)
            text += tag_text + "\n"
        metadata = [{"doc_id": str(uuid.uuid4()), "page": 1, "text": text, "source": url}]
        return text, metadata
    except Exception as e:
        st.error(f"Error fetching content from URL {url}: {e}")
        return "", []

@st.cache_data
def get_text_chunks(text, metadata):
    """
    Splits text into chunks and associates metadata.
    """
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_text(text)
    chunk_metadata = []
    for i, chunk in enumerate(chunks):
        chunk_metadata.append(metadata[i % len(metadata)])
        chunk_metadata[-1]["paragraph"] = i + 1
    return chunks, chunk_metadata

@st.cache_resource
def get_vector_store(chunks, chunk_metadata):
    """
    Creates FAISS vector store from text chunks.
    """
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = FAISS.from_texts(chunks, embedding=embeddings, metadatas=chunk_metadata)
    vector_store.save_local("faiss_index")
    return vector_store

def get_conversational_chain():
    """
    Creates QA chain with custom prompt.
    """
    prompt_template = """
    YOU ARE A HIGHLY DISCIPLINED, EVIDENCE-DRIVEN QUESTION-ANSWERING AGENT TRAINED TO EXTRACT, ANALYZE, AND REPORT INFORMATION *EXCLUSIVELY* FROM THE PROVIDED CONTEXT. YOUR RESPONSES MUST BE THOROUGH, FACTUALLY PRECISE, AND METICULOUSLY SOURCED.

    ###INSTRUCTIONS###

    - YOU MUST PROVIDE A COMPREHENSIVE AND ACCURATE ANSWER TO THE USER'S QUESTION *USING ONLY THE INFORMATION FOUND IN THE GIVEN CONTEXT*
    - PRESENT THE ANSWER IN BULLET POINTS FOR CLARITY AND READABILITY
    - ALL CLAIMS OR FACTS MUST BE SUPPORTED BY CLEAR CITATIONS IN THE FORMAT: `(Document ID: [ID], Page: [X], Paragraph: [Y], Source: [Source])`
    - IF THE CONTEXT DOES *NOT* CONTAIN SUFFICIENT INFORMATION TO ANSWER, RESPOND EXACTLY: `"Answer is not available in the context."`
    - DO NOT FABRICATE, ASSUME, OR HALLUCINATE ANY INFORMATION OUTSIDE THE PROVIDED MATERIAL

    ###CHAIN OF THOUGHTS TO FOLLOW###

    1. **UNDERSTAND** the user's question carefully and precisely
    2. **IDENTIFY** all key elements and concepts within the question
    3. **SCAN** the provided context for all *relevant sections* tied to the query
    4. **EXTRACT** the factual content that addresses the question directly
    5. **VERIFY** the relevance and accuracy of the extracted information
    6. **CITE** all supporting evidence in the required format: `(Document ID: [ID], Page: [X], Paragraph: [Y], Source: [Source])`
    7. **RESPOND** with a clear, complete, and well-structured answer in bullet points using only the validated context
    8. **RETURN** "Answer is not available in the context" if *no* relevant information exists

    ###WHAT NOT TO DO###

    - DO NOT INVENT INFORMATION NOT PRESENT IN THE CONTEXT
    - NEVER OMIT REQUIRED CITATIONS — THEY ARE MANDATORY FOR EVERY CLAIM
    - DO NOT PROVIDE VAGUE OR INCOMPLETE ANSWERS
    - NEVER PARAPHRASE IF IT RISKS ALTERING THE FACTUAL MEANING OF SOURCE TEXT
    - AVOID GENERALIZATIONS NOT GROUNDED IN THE SPECIFIC CITED MATERIAL
    - DO NOT MENTION OR SPECULATE ABOUT DATA OUTSIDE THE GIVEN CONTEXT

    ###EXAMPLE RESPONSE FORMAT###

    **Question**: What is the primary benefit of hydrogen fuel mentioned in the context?

    **Answer**:
    - The primary benefit of hydrogen fuel is its zero-emission nature, which contributes significantly to reducing environmental pollution (Document ID: H-2023-01, Page: 4, Paragraph: 2, Source: hydrogen_report.pdf).
    
    Context:\n{context}\n
    Question:\n{question}\n
    
    Answer:
    """
    model = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.3)
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    return load_qa_chain(model, chain_type="stuff", prompt=prompt)

def get_theme_summary(docs, question):
    """
    Generates a summary of recurring themes using Gemini.
    """
    prompt_template = """
    YOU ARE A WORLD-CLASS DOCUMENT SYNTHESIS EXPERT SPECIALIZED IN ANALYZING MULTI-SOURCE TEXTUAL DATA TO EXTRACT THEMES AND KEY INSIGHTS. YOUR TASK IS TO EXAMINE THE PROVIDED DOCUMENT EXCERPTS AND SUMMARIZE RECURRING THEMES RELATED TO THE USER'S QUESTION IN A CONVERSATIONAL, EASY-TO-UNDERSTAND MANNER — WHILE MAINTAINING ACADEMIC RIGOR THROUGH ACCURATE CITATIONS.

    ###INSTRUCTIONS###

    - CAREFULLY READ all document excerpts provided
    - IDENTIFY recurring themes, patterns, or key insights SPECIFICALLY RELEVANT to the question: **"{question}"**
    - SUMMARIZE the themes in a NATURAL, CONVERSATIONAL TONE using BULLET POINTS for clarity
    - INCLUDE ACCURATE CITATIONS in the format: `(Document ID: [ID], Page: [X], Paragraph: [Y], Source: [Source])` IMMEDIATELY after each claim or thematic insight
    - DO NOT INCLUDE INFORMATION that cannot be directly traced to the context with a proper citation
    - MAINTAIN A BALANCE between ACCESSIBLE LANGUAGE and ANALYTICAL DEPTH

    ###CHAIN OF THOUGHTS TO FOLLOW###

    1. **UNDERSTAND** the question: parse what specific themes or insights should be sought
    2. **SCAN** all document excerpts to locate content related to the question
    3. **GROUP** related excerpts together by common themes or insights
    4. **ANALYZE** each group to extract the core idea represented
    5. **PHRASE** your findings in bullet points in a smooth, conversational tone
    6. **CITE** every theme with specific references using the format: `(Document ID: [ID], Page: [X], Paragraph: [Y], Source: [Source])`
    7. **VERIFY** that no part of the answer includes unstated assumptions or uncited claims

    ###WHAT NOT TO DO###

    - NEVER INVENT THEMES OR INSIGHTS THAT ARE NOT GROUNDED IN THE PROVIDED CONTEXT
    - DO NOT OMIT CITATIONS FOR ANY CLAIM OR GENERALIZATION
    - DO NOT REPEAT VERBATIM TEXT FROM THE DOCUMENTS WITHOUT INTERPRETING THE THEMES
    - NEVER WRITE IN A FORMAL, STILTED, OR OVERLY TECHNICAL TONE — THE SUMMARY SHOULD BE CONVERSATIONAL
    - AVOID LISTING QUOTES WITHOUT SYNTHESIZING MEANING OR GROUPING THEM INTO COHERENT THEMES

    ###EXAMPLE RESPONSE FORMAT###

    **Question**: What do the excerpts suggest about employee motivation in remote work settings?

    **Answer**:
    - **Flexibility boosts motivation**: Many employees feel more empowered and productive with flexible schedules (Document ID: RW-102, Page: 3, Paragraph: 1, Source: remote_work_study.pdf).
    - **Social interaction challenges**: Lack of social interaction can reduce team cohesion, negatively impacting motivation (Document ID: RW-098, Page: 5, Paragraph: 4, Source: remote_work_study.pdf).
    - **Communication tools help**: Platforms help maintain connection despite physical distance (Document ID: RW-115, Page: 2, Paragraph: 2, Source: remote_work_study.pdf).

    Excerpts:\n{context}\n

    Summary:
    """
    model = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.5)
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    context = "\n".join([f"Doc ID: {doc.metadata['doc_id']}, Page: {doc.metadata['page']}, Para: {doc.metadata['paragraph']}, Source: {doc.metadata['source']}\n{doc.page_content}" for doc in docs])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)
    response = chain({"input_documents": docs, "question": question}, return_only_outputs=True)
    return response["output_text"]

# Main Page: Question Input and Results
st.header("💬 Ask a Question")

# Use a form to control question submission with Ctrl + Enter
with st.form(key="question_form"):
    user_question = st.text_area(
        "Enter your question here (Press Ctrl + Enter to submit):",
        placeholder="E.g., What are the key findings in the uploaded documents?",
        height=100,
    )
    submit_button = st.form_submit_button(label="Submit Question")

# Process Documents, URL Content, and Query
if submit_button and user_question and api_key and (uploaded_files or url_input):
    with st.spinner("Processing documents and generating answer..."):
        try:
            all_chunks = []
            all_metadata = []

            # Process uploaded files
            if uploaded_files:
                for file in uploaded_files:
                    text, metadata = extract_text_from_file(file, file.name)
                    if text:
                        chunks, chunk_metadata = get_text_chunks(text, metadata)
                        all_chunks.extend(chunks)
                        all_metadata.extend(chunk_metadata)

            # Process URL content
            if url_input:
                url_text, url_metadata = extract_text_from_url(url_input)
                if url_text:
                    url_chunks, url_chunk_metadata = get_text_chunks(url_text, url_metadata)
                    all_chunks.extend(url_chunks)
                    all_metadata.extend(url_chunk_metadata)

            if all_chunks:
                # Create vector store
                vector_store = get_vector_store(all_chunks, all_metadata)

                # Perform similarity search
                embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
                new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
                docs = new_db.similarity_search(user_question, k=5)

                # Generate answer
                chain = get_conversational_chain()
                response = chain({"input_documents": docs, "question": user_question}, return_only_outputs=True)

                # Display Answer
                st.subheader("Answer")
                st.markdown(response["output_text"])

                # Display Citations in Improved Table
                st.subheader("Citations")
                citation_data = [
                    {
                        "Document ID": doc.metadata["doc_id"],
                        "Source": doc.metadata["source"],
                        "Page": doc.metadata["page"],
                        "Paragraph": doc.metadata["paragraph"],
                        "Content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                    }
                    for doc in docs
                ]
                df = pd.DataFrame(citation_data)
                # Convert DataFrame to HTML table with Tailwind styling
                html_table = df.to_html(index=False, escape=False, classes="answer-table")
                st.markdown(html_table, unsafe_allow_html=True)

                # Generate and Display Themes
                st.subheader("Recurring Themes")
                theme_summary = get_theme_summary(docs, user_question)
                st.markdown(theme_summary)

        except Exception as e:
            st.error(f"An error occurred: {e}")
else:
    if not api_key:
        st.warning("Please provide your Google Gemini API key.")
    if not (uploaded_files or url_input):
        st.warning("Please upload at least one document or provide a URL.")
    if not user_question:
        st.warning("Please enter a question.")
    if user_question and not submit_button:
        st.info("Press Ctrl + Enter to submit your question.")

# Footer
st.markdown(
    """
    <div class="text-center text-gray-500 mt-8">
        <hr class="border-gray-200 mb-4">
        <p>Powered by LangChain, Google Gemini, and FAISS</p>
    </div>
    """,
    unsafe_allow_html=True,
)

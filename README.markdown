# AI Document Chatbot 📚

A powerful Streamlit-based application to chat with your documents! Upload PDFs, images, or text files, provide URLs, and ask questions to get accurate answers with citations and recurring themes. Powered by LangChain, Google Gemini, and FAISS for advanced Retrieval-Augmented Generation (RAG).

This project is part of the Wasserstoff AI Intern Task by Shantanu Shinde.

---

## ✨ Features

- **Document Upload** 📄: Upload multiple PDFs, images (JPG/PNG), or text files for processing.
- **URL Content Extraction** 🌐: Provide a URL to fetch and process web content.
- **Question Answering** 💬: Ask questions and get detailed answers in bullet points, sourced from the documents.
- **Citations** 📑: View citations with Document ID, Source, Page, and Paragraph for transparency.
- **Theme Identification** 🔍: Discover recurring themes across documents with citations.
- **OCR Support** 🖼️: Extract text from images using Tesseract OCR.
- **User-Friendly UI** 🖥️: Built with Streamlit and styled using Tailwind CSS for a modern look.
- **Controlled Submission** ⏎: Submit questions using Ctrl + Enter to prevent accidental execution.

---

## 📸 Demo

Here’s how the app looks in action! (Replace the GIF paths with actual files you create.)

### Document Upload and URL Input
![Document Upload](docs/demo/document_upload.gif)

### Asking a Question
![Asking a Question](docs/demo/ask_question.gif)

### Viewing Results with Citations and Themes
![Results](docs/demo/results.gif)

---

## 🛠️ Tech Stack

| Technology            | Logo                                                                 | Description                                      |
|-----------------------|----------------------------------------------------------------------|--------------------------------------------------|
| **Python 3.11**       | <img src="https://www.python.org/static/community_logos/python-logo.png" width="50"> | Programming language used in a virtual environment. |
| **Streamlit**         | <img src="https://streamlit.io/images/brand/streamlit-logo-primary-colormark-darktext.png" width="50"> | Framework for building the web interface. |
| **LangChain**         | <img src="https://avatars.githubusercontent.com/u/108318121" width="50"> | Framework for building RAG applications. |
| **Google Gemini**     | <img src="https://developers.google.com/static/gemini/images/gemini-icon.png" width="50"> | Generative AI for answering questions and theme synthesis. |
| **FAISS**             | <img src="https://raw.githubusercontent.com/facebookresearch/faiss/main/.github/FAISS_logo.png" width="50"> | Vector store for efficient similarity search. |
| **PyPDF2**            | <img src="https://pypdf2.readthedocs.io/en/stable/_static/pypdf2-logo.png" width="50"> | Library for extracting text from PDFs. |
| **Tesseract OCR**     | <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/9/9a/Tesseract_OCR_Logo.png/50px-Tesseract_OCR_Logo.png" width="50"> | OCR engine for extracting text from images. |
| **Pillow**            | <img src="https://pillow.readthedocs.io/en/stable/_static/pillow-logo-dark-text.png" width="50"> | Image processing library for handling image uploads. |
| **Pandas**            | <img src="https://pandas.pydata.org/static/img/pandas_secondary.svg" width="50"> | Data manipulation for citation tables. |
| **Requests**          | <img src="https://requests.readthedocs.io/en/master/_static/requests-sidebar.png" width="50"> | HTTP library for fetching URL content. |
| **BeautifulSoup**     | <img src="https://www.crummy.com/software/BeautifulSoup/bs4/doc/_images/6.1.jpg" width="50"> | Library for parsing HTML content from URLs. |
| **Tailwind CSS**      | <img src="https://tailwindcss.com/_next/static/media/tailwindcss-mark.3c5441fc7a190fb1800d4a5c7f07ba4b1345fb2.svg" width="50"> | CSS framework for styling the UI. |

---

## 🚀 Getting Started

### Prerequisites
- **Python 3.11**: Ensure Python 3.11 is installed.
- **Tesseract OCR**: Install Tesseract for image processing.
  - **Windows**: Download and install from [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki).
  - **Linux**: `sudo apt-get install tesseract-ocr`.
  - **macOS**: `brew install tesseract`.

### Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/shantanushinde99/shantanu-shinde-wasserstoff-AiInternTask.git
   cd shantanu-shinde-wasserstoff-AiInternTask
   ```

2. **Create a Virtual Environment with Python 3.11**
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

   `requirements.txt` should contain:
   ```
   streamlit
   langchain
   langchain-google-genai
   faiss-cpu
   pypdf2
   pytesseract
   pillow
   pandas
   requests
   beautifulsoup4
   ```

4. **Run the Application**
   ```bash
   streamlit run app.py
   ```

5. **Access the App**
   Open your browser and go to `http://localhost:8501`.

---

## 📖 Usage

1. **Configure the App**:
   - Enter your Google Gemini API key in the sidebar.
   - Upload documents (PDFs, images, or text) or provide a URL to fetch content.

2. **Ask Questions**:
   - Type your question in the main area.
   - Press **Ctrl + Enter** to submit your question (prevents accidental submissions).

3. **View Results**:
   - **Answers**: Displayed in bullet points with citations.
   - **Citations**: Presented in a structured table with Document ID, Source, Page, Paragraph, and Content.
   - **Themes**: Recurring themes extracted from the documents, also in bullet points.

---

## 🗂️ Project Structure

```
shantanu-shinde-wasserstoff-AiInternTask/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── docs/               # Documentation and demo files
│   └── demo/           # Directory for demo GIFs
│       ├── document_upload.gif
│       ├── ask_question.gif
│       └── results.gif
├── uploads/            # Temporary directory for uploaded files (created at runtime)
└── faiss_index/        # Directory for FAISS index files (created at runtime)
```

---

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature`).
3. Make your changes.
4. Commit your changes (`git commit -m 'Add your feature'`).
5. Push to the branch (`git push origin feature/your-feature`).
6. Open a Pull Request.

---

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 📧 Contact

For questions or support, reach out to Shantanu Shinde via GitHub: [shantanushinde99](https://github.com/shantanushinde99).

---

**Built with ❤️ by Shantanu Shinde**
# 🩺 BioLens - AI-Powered Medical Intelligence

BioLens is an advanced AI-driven application that analyzes blood reports and provides detailed health insights. Built with a multi-model cascade system, BioLens ensures in-depth medical analysis and personalized recommendations.

---

## 🌟 Features
✅ Intelligent AI-driven report analysis with multi-model processing  
✅ In-context learning for personalized insights  
✅ Secure user authentication & session tracking  
✅ PDF report upload, validation, and text extraction (up to 20MB)  
✅ Real-time feedback & session history tracking  
✅ Modern, responsive UI powered by Streamlit  

---

## 🛠️ Tech Stack
🔹 **Frontend:** Streamlit 🖥️  
🔹 **AI Models:** Multi-model architecture via Groq 🤖  
   - **Primary:** LLaMA-3.3-70B-Versatile  
   - **Secondary:** LLaMA-3-8B-8192  
   - **Tertiary:** Mixtral-8x7B-32768  
   - **Fallback:** Gemma-7B-IT  

🔹 **Database:** Supabase 🗄️  
🔹 **PDF Processing:** PDFPlumber 📄  
🔹 **Authentication:** Supabase Auth 🔑  

---

## 🚀 Installation

### 📋 Requirements
- Python **3.12.8** 🐍  
- Streamlit **1.44.0**  
- Supabase account 🔐  
- Groq API key 🔑  
- PDFPlumber 📄  

### 📝 Setup
1️⃣ **Clone the repository:**  
   ```sh
   git clone https://github.com/ArchitJ6/BioLens.git
   cd BioLens
   ```
2️⃣ **Install dependencies:**  
   ```sh
   pip install -r requirements.txt
   ```
3️⃣ **Configure environment variables:**  
   Create a `.streamlit/secrets.toml` file and add:
   ```toml
   SUPABASE_URL = "your-supabase-url"
   SUPABASE_KEY = "your-supabase-key"
   GROQ_API_KEY = "your-groq-api-key"
   ```
4️⃣ **Run the application:**  
   ```sh
   streamlit run src/app.py
   ```

---

## 📂 Folder Structure
```
📦 BioLens
├── 📂 .streamlit
│   ├── config.toml
│   ├── secrets.toml

├── 📂 public
│   ├── 📂 database
│   │   ├── README.md
│
├── 📂 src
│   ├── 📂 agents
│   │   ├── analysisAgent.py
│   │   ├── modelManager.py
│   │   ├── services.py
│   │   ├── __init__.py
│   │
│   ├── 📂 auth
│   │   ├── service.py
│   │   ├── session.py
│   │   ├── __init__.py
│   │
│   ├── 📂 components
│   │   ├── auth.py
│   │   ├── footer.py
│   │   ├── form.py
│   │   ├── header.py
│   │   ├── sidebar.py
│   │   ├── __init__.py
│   │
│   ├── 📂 config
│   │   ├── prompt.py
│   │   ├── sample.py
│   │   ├── __init__.py
│   │
│   ├── 📂 utils
│   │   ├── pdfHelper.py
│   │   ├── validators.py
│   │   ├── __init__.py
│   │
│   ├── app.py
│
├── .gitignore
├── LICENSE
├── README.md
├── requirements.txt
```

---

## 📖 Database Setup
For details on setting up the database, refer to the [Database README](public/database/README.md).

---

## 🎯 Usage Demo
🚀 Upload a blood report (PDF) and receive a detailed AI-driven health analysis with personalized recommendations.

---

## 🤝 Contributing
Contributions are welcome! Feel free to fork the repo and submit a pull request. 😊

---

## 📜 License
This project is licensed under the terms of the [MIT License](LICENSE).

---

## ⚠️ Disclaimer
> This AI-generated analysis is for informational purposes only and is not a substitute for professional medical advice. Always consult a healthcare provider for accurate diagnosis and treatment.

---

## 🌟 Show Your Support
If you found this project helpful, ⭐️ star the repository and share it with others!

Happy coding! 💙
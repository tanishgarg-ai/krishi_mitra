🌾 Krishi-Mitra An Agentic AI-Powered Agricultural Assistant

Krishi-Mitra is an AI-driven agricultural assistant designed to empower farmers with real-time, data-driven insights related to crop health, market trends, weather conditions, and government schemes. Built using an agentic AI architecture, the system integrates computer vision, large language models, knowledge retrieval, and weather intelligence to provide intelligent, context-aware agricultural guidance.

🚀 Key Features

🌱 Crop Disease Detection Detects plant diseases from images using a ResNet-based CNN trained on the Plant Diseases Dataset.

📊 Market Analysis Engine Uses Groq LLM to analyze real-time crop price data and demand trends via data.gov APIs.

🌦️ Weather Intelligence Integrates IndianAPI Weather to assess real-time weather conditions and their impact on crop health and disease risk.

🏛️ Scheme Navigator Retrieves relevant government schemes and subsidies from a vectorized knowledge base.

🧠 Agentic Intelligence Uses LangGraph for autonomous reasoning and dynamic tool calling across vision, language, retrieval, and weather modules.

⚡ FastAPI Backend Ensures high-speed, asynchronous communication between AI modules and the frontend.

🌐 Multilingual Support Provides farmer-friendly responses in simple and regional languages.

🧠 System Architecture 
User (Farmer) 
    ↓ 
Frontend (Web) 
    ↓ 
FastAPI Backend 
    ↓
LangGraph Agent Orchestrator
    ↓
| ResNet CNN | Groq LLM | Weather |
    ↓
Final Context-Aware Response

🛠️ Technology Stack Category Technology Backend Framework FastAPI AI Core ResNet (PyTorch), Groq LLM Agent Framework LangGraph Weather API IndianAPI Weather Market Data data.gov APIs Knowledge Retrieval FAISS, Sentence-Transformers Deep Learning PyTorch Data Source Plant Diseases Dataset Language Python 📂 Project Structure ├── models/ │ ├── disease_model.py │ ├── market_model.py │ ├── tools.py # LangChain tools (disease, market, weather, schemes) ├── agent.py # LangGraph agent logic ├── main.py # FastAPI entry point ├── scheme.json # Government schemes data ├── requirements.txt └── README.md

⚙️ Installation & Setup 1️⃣ Clone the Repository git clone https://github.com/Sarabjitsharma/KrishiMitra.git cd Krishi-Mitra

2️⃣ Create Virtual Environment python -m venv venv source venv/bin/activate # Windows: venv\Scripts\activate

3️⃣ Install Dependencies pip install -r requirements.txt

4️⃣ Run the Backend uvicorn main:app --reload

🧪 Example Queries

“Detect disease in this crop image”

“What is the market price of wheat in Punjab?”

“Is current weather suitable for spraying crops?”

“Which government schemes are available for farmers?”

🎥 Project Demo

▶️ Demo Video:
Demo Video: https://drive.google.com/file/d/12ZVCXmb60-oLsCsPwBiFwJuoiuToPGzE/view?usp=sharing

🌱 Future Enhancements

Crop recommendation engine based on soil, weather, and market data

Irrigation advisory system

Farmer profile memory using FAISS

Voice-based assistant for rural accessibility

Offline support for low-connectivity regions

👨‍💻 Contributors

Sarabjit Sharma

Siddhant Walia

Tanish Garg

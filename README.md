<p align="left">
  <img src="EduRise/edurise/static/images/Logo.png" alt="EduRise Logo" width="120"/>
</p>

# EduRise

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Django](https://img.shields.io/badge/Django-5.2-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

**EduRise** is an **AI-powered educational decision support platform** focused on the **French education system**.  
It combines **Business Intelligence, Machine Learning, and Generative AI** to transform large-scale educational data into actionable insights for strategic planning and policy decision-making.

The platform supports monitoring and optimization of educational institutions, student enrollment, service availability (Restauration & Hébergement), and inclusive education programs (ULIS) at both national and regional levels.

---

## 🚀 Features

### 📊 Business Intelligence & Dashboards
- Embedded **Power BI dashboards** for interactive analytics  
- Regional, departmental, and institutional analysis  
- Enrollment trends and capacity indicators  
- Service coverage analysis (ULIS, Restauration, Hébergement)  
- Dashboards designed for **Row-Level Security (RLS)**  

### 🤖 Machine Learning & Advanced Analytics
- **Clustering models** for institutional and territorial profiling  
- **Classification models** for:
  - Service availability prediction  
  - Public/private imbalance detection  
  - ULIS demand forecasting  
- **Regression models** for student enrollment prediction  
- **Anomaly detection and multi-criteria scoring** to prioritize institutions requiring urgent interventions  

### 💬 RAG-Based Conversational Assistant
- Integrated **Retrieval-Augmented Generation (RAG) chatbot**  
- Enables conversational access to KPIs, institutional data, and ML insights  
- Supports intuitive, AI-assisted decision-making for non-technical users  

### 🔐 Platform & Access Management
- **Role-Based Access Control (RBAC)**  
- Secure, modular, and scalable architecture  
- Institutional and decision-maker–oriented user experience  

---

## 📂 Project Structure

The project is modularized into several Django applications, each handling a specific domain:

- **`users`**: User authentication, role management, and profile handling.
- **`institutions`**: Management of educational institutions and their metadata.
- **`services`**: Handles prediction logic for services like Restauration and Hébergement.
- **`enrollment`**: Analytics and management of student enrollment data.
- **`ulis`**: Specific management for ULIS (inclusive education units) programs.
- **`chatbot`**: The RAG-based conversational interface and logic.
- **`InstitutionPP`**: Advanced clustering and public/private classification analytics.

---

## 🧩 System Architecture

| Component | Description |
|---------|-------------|
| Frontend | HTML, CSS, JavaScript |
| Data Visualization | Power BI |
| Machine Learning | Python (Scikit-learn, XGBoost, CatBoost) |
| Generative AI | RAG (FAISS, SentenceTransformers) |
| Backend | Django |
| Database | PostgreSQL (Production) / SQLite (Dev) |
| Design Principle | Secure, institutional, data-centric |

---

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- git

### 1. Clone the Repository

```bash
git clone https://github.com/yessine-hakim/EduRise.git
cd edurise
```

### 2. Create a Virtual Environment

**On Windows:**
```bash
python -m venv env
```

**On macOS/Linux:**
```bash
python3 -m venv env
```

### 3. Activate the Virtual Environment

**On Windows:**
```bash
.\env\Scripts\activate
```

**On macOS/Linux:**
```bash
source env/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the Development Server

```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/` 

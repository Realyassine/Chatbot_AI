# Chatbot AI

**Chatbot AI Project** — A conversational AI chatbot built with Python, React+Vite, and Tailwind CSS.

## 🧠 Overview

This project is a lightweight, responsive chatbot interface designed for seamless user interaction. It leverages modern frontend technologies to provide a fast and intuitive experience.

## 🚀 Features
* **Python**: Lightweight backend to handle requests and securely forward them to the AI service.
* **React + Vite**: Utilizes Vite for rapid development and hot module replacement.
* **Tailwind CSS**: Employs utility-first CSS for efficient styling.


## 📁 Project Structure

```
Chatbot_AI/
├── backend/
│  └── .env
│  └── app.py
│  └── requirment.txt
├── frontend/
│  └── public/
│  └── src/
│     └── App.jsx
│     └── main.jsx
├── index.html
├── package.json
├── tailwind.config.js
├── postcss.config.js
├── vite.config.js
└── .eslintrc.js
```

## 🛠️ Getting Started

### Prerequisites

* Node.js (v16 or higher)
* npm 

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/Realyassine/Chatbot_AI.git
   cd Chatbot_AI
   ```



2. **Install dependencies:**

   ```bash
   npm install



3. **Run the project: **
   **Backend:**
      ```bash
      uvicorn app:app --reload
      ```
   **Frontend**
      ```bash
      npm run dev
      ```
      

4. **Open in browser:**

   Navigate to `http://localhost:5173` to view the application.

## 📦 Build for Production

To create an optimized production build:

```bash
npm run build

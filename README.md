# AI Supplier Search Agent
An Intelligent AI-Powered Supplier Search Agent with RAG-Chatbot Interface

## Features
- Real-time supplier search and filtering
- AI chatbot for supplier queries
- Interactive supplier listings
- Detailed supplier information view
- Filter by category, process, location, and more

## Tech Stack
### Frontend
- React + TypeScript
- Tailwind CSS
- Framer Motion
- Lucide Icons
- shadcn/ui components

### Backend
- Flask
- Pandas
- Scikit-learn
- TF-IDF Vectorization
- Cosine Similarity Search

## Setup

### Prerequisites
- Node.js
- Python 3.8+
- pip

### Backend Setup
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run Flask server
python index.py
```

### Frontend Setup
```bash
# Install dependencies
npm install

# Run development server
npm run dev
```

## Usage
1. Start both backend and frontend servers
2. Access the application at http://localhost:5173
3. Use the chat interface or filters to search suppliers
4. View detailed supplier information in the listings

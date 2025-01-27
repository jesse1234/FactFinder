# News Query and Fact-Check Application

Welcome to FactFinder, a News Query and Fact-Check Application! This project is designed to combat misinformation online by leveraging agentic RAG (Retrieval-Augmented Generation) with CrewAI for the agents, LangChain, and OpenAI. The application uses Flask for the backend and Streamlit for the frontend.

## Features

- **Agentic RAG with CrewAI**: Utilizes advanced AI agents to retrieve and generate accurate information.
- **LangChain Integration**: Enhances the language model capabilities for better context understanding.
- **OpenAI**: Powers the core AI functionalities for natural language processing.
- **Flask Backend**: Provides a robust and scalable backend service.
- **Streamlit Frontend**: Offers an interactive and user-friendly interface.

## Setup Instructions

To get started with this project, follow these steps:

### Prerequisites

- Python 3.8 or higher
- Git
- OpenAI API key

### Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/your-username/your-repo-name.git
   cd your-repo-name

2. **Set up virtual environment**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`

3. **Install dependencies**
    ```bash
    pip install -r requirements.txt

4. **Create a .env file and add your OpenAI API key**
    ```plaintext
    OPENAI_API_KEY = your-api-key-here

5. **Run the backend server**
    ```bash
    flask run

6. **Run frontend application**
    ```bash
    cd streamlit
    streamlit run home.py

### Usage

Once the application is running, you can access the Streamlit frontend by navigating to http://localhost:8501 in your web browser. Use the interface to query news and fact-check information.
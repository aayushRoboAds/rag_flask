from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_community.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
import os

# === Flask App Setup ===
app = Flask(__name__)
CORS(app)

# === Tool Function ===
@app.route('/query', methods=['POST'])
def get_product_details():
    data = request.get_json()

    if not data or 'query' not in data:
        return jsonify({'error': 'Missing "query" in request body'}), 400

    query_string = data['query']
    print(f"Received query: {query_string}")

    try:
        # Securely load API key from environment variable
        openai_api_key = os.environ.get('OPENAI_API_KEY')
        if not openai_api_key:
            return jsonify({'error': 'OpenAI API key not found'}), 500

        # Embedding & Vector DB Setup
        embedding_model = OpenAIEmbeddings(openai_api_key=openai_api_key)
        vector_db = FAISS.load_local("vector_db_index", embeddings=embedding_model, allow_dangerous_deserialization=True)
        retriever = vector_db.as_retriever()

        # LLM Setup
        llm = ChatOpenAI(temperature=0.2, model_name="gpt-4o-mini", openai_api_key=openai_api_key)
        rag_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

        # Run the query
        result = rag_chain.run(query_string)
        print(result)

        return jsonify({'response': result})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# === Flask Start ===
if __name__ == "__main__":
    print("Starting Flask app...")
    app.run(host="0.0.0.0", port=5000)

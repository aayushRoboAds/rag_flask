import os
import json
import shutil
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.vectorstores import FAISS
from langchain.document_loaders import UnstructuredExcelLoader

# Initialize app
app = Flask(__name__)
CORS(app)  # For production, restrict by origins with: CORS(app, resources={r"/api/*": {"origins": "https://yourdomain.com"}})

# Set up logging
logging.basicConfig(level=logging.INFO)

# Constants
UPLOAD_FOLDER = 'users'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- Utility Function ---
def get_openai_key():
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OpenAI API key not found in environment variables.")
    return api_key

def get_user_folder(userid):
    print( os.path.join(UPLOAD_FOLDER, secure_filename(userid)))
    return os.path.join(UPLOAD_FOLDER, secure_filename(userid))

# --- Route: Handle Query ---

@app.route('/query', methods=['POST'])
def get_product_details():
    data = request.get_json()

    if not data or 'query' not in data:
        return jsonify({'error': 'Missing "query" in request body'}), 400

    query_string = data['query']
    userid = data['userid']
    print(f"Received query from {userid}: {query_string}")

    try:
        # Securely load API key from environment variable
        openai_api_key = os.environ.get('OPENAI_API_KEY')
        if not openai_api_key:
            return jsonify({'error': 'OpenAI API key not found'}), 500

        # Embedding & Vector DB Setup
        embedding_model = OpenAIEmbeddings(openai_api_key=openai_api_key)
        print(f"Loading FAISS index for user {userid}...")
        try:
            vector_db = FAISS.load_local(f"users/{userid}", embeddings=embedding_model, allow_dangerous_deserialization=True)
        except Exception as load_error:
            return jsonify({'error': f'Failed to load FAISS index for user {userid}: {str(load_error)}'}), 500
        
        retriever = vector_db.as_retriever()

        # LLM Setup
        llm = ChatOpenAI(temperature=0.2, model_name="gpt-4o-mini", openai_api_key=openai_api_key)
        rag_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

        # Run the query
        result = rag_chain.invoke({"query": query_string})
        print(result)

        return jsonify({'response': result})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/video', methods=['POST'])
def get_product_video():
    data = request.get_json()

    if not data or 'query' not in data:
        return jsonify({'error': 'Missing "query" in request body'}), 400

    query_string = data['query']
    userid = data['userid']
    print(f"Received query from {userid}: {query_string}")
    prompt="Your output should be a single URL from the product base without any other text.Please provide a video link for the query: " 
    query_string=prompt+query_string
    try:
        # Securely load API key from environment variable
        openai_api_key = os.environ.get('OPENAI_API_KEY')
        if not openai_api_key:
            return jsonify({'error': 'OpenAI API key not found'}), 500

        # Embedding & Vector DB Setup
        embedding_model = OpenAIEmbeddings(openai_api_key=openai_api_key)
        vector_db = FAISS.load_local(f"users/{userid}", embeddings=embedding_model, allow_dangerous_deserialization=True)
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








# --- Route: Add User Document ---
@app.route('/adduser', methods=['POST'])
def upload_document():
    if 'file' not in request.files or 'userid' not in request.form:
        return jsonify({'error': 'Missing file or userid'}), 400

    file = request.files['file']
    userid = request.form['userid']

    return create_user_folder(file, userid)

def create_user_folder(file, userid):
    try:
        user_folder = get_user_folder(userid)
        os.makedirs(user_folder, exist_ok=True)

        file_path = os.path.join(user_folder, secure_filename(file.filename))
        file.save(file_path)

        loader = UnstructuredExcelLoader(file_path)
        docs = loader.load()

        embedding = OpenAIEmbeddings(api_key=get_openai_key())
        vector_store = FAISS.from_documents(documents=docs, embedding=embedding)
        vector_store.save_local(user_folder)

        return jsonify({'message': 'File uploaded and vector store created successfully'}), 200

    except Exception as e:
        app.logger.error(f"User Upload Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# --- Route: Modify User ---
@app.route('/modifyuser', methods=['POST'])
def modify_user():
    if 'file' not in request.files or 'userid' not in request.form:
        return jsonify({'error': 'Missing file or userid'}), 400

    file = request.files['file']
    userid = request.form['userid']
    user_folder = get_user_folder(userid)

    try:
        if os.path.exists(user_folder):
            shutil.rmtree(user_folder)
        os.makedirs(user_folder)

        return create_user_folder(file, userid)

    except Exception as e:
        app.logger.error(f"Modify Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# --- Route: Delete User ---
@app.route('/deleteuser', methods=['POST'])
def delete_user():
    userid = request.form.get('userid')
    if not userid:
        return jsonify({'error': 'Missing userid'}), 400

    user_folder = get_user_folder(userid)

    try:
        if os.path.exists(user_folder):
            shutil.rmtree(user_folder)
            return jsonify({'message': f'User {userid} deleted successfully'}), 200
        else:
            return jsonify({'error': 'User folder does not exist'}), 404

    except Exception as e:
        app.logger.error(f"Delete Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# --- Route: View Excel Files ---
@app.route('/viewuserexcelfiles', methods=['POST'])
def view_user_excel_files():
    userid = request.form.get('userid')
    if not userid:
        return jsonify({'error': 'Missing userid'}), 400

    user_folder = get_user_folder(userid)

    try:
        if os.path.exists(user_folder):
            files = [f for f in os.listdir(user_folder) if f.endswith(('.xlsx', '.xls'))]
            return jsonify({'files': files}), 200
        else:
            return jsonify({'error': 'User folder does not exist'}), 404

    except Exception as e:
        app.logger.error(f"View Excel Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# --- Route: View All Users ---
@app.route('/viewallusers', methods=['GET'])
def view_all_users():
    try:
        users = [d for d in os.listdir(UPLOAD_FOLDER) if os.path.isdir(os.path.join(UPLOAD_FOLDER, d))]
        return jsonify({'users': users}), 200
    except Exception as e:
        app.logger.error(f"View Users Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# --- App Entrypoint ---
if __name__ == "__main__":
    app.logger.info("Starting Flask app...")
    app.run(host="0.0.0.0", port=5000)

from flask import Flask, request, jsonify
from flask_cors import CORS
from github3 import login
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import requests

app = Flask(__name__)
CORS(app)  # This will allow all origins by default

@app.route('/api/generate-docs', methods=['POST'])
def generate_docs():
    try:
        # Get the data from the request
        data = request.get_json()
        code = data.get('code', None)
        repo_link = data.get('repoLink', None)

        if code:
            documentation = extract_docs_from_code(code)
        elif repo_link:
            documentation = extract_docs_from_repo(repo_link)
        else:
            return jsonify({'error': 'No code or repo link provided'}), 400

        response = {
            'documentation': documentation
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    print("Server running on port 5000 ...")
    app.run(debug=False, port=5000)

# Function to extract documentation from code using LangChain
def extract_docs_from_code(code):

    prompt = "Generate concise and accurate documentation for the following code:\n\n{code}"
    prompt_template = PromptTemplate(input_variables=["code"], template=prompt)

    # Assuming you have set up your LangChain model (like GPT-3.5 or any other LLM)
    llm_chain = LLMChain(prompt_template, llm='gpt-3.5-turbo')  # Modify LLM accordingly
    response = llm_chain.run({"code": code})
    return response

# Function to extract docs from repo by fetching code first
def extract_docs_from_repo(repo_link):
    code = fetch_code_from_github(repo_link)
    return extract_docs_from_code(code)

# Function to fetch repository code using GitHub API
def fetch_code_from_github(repo_link):
    # Extract owner and repo name from the link
    owner, repo = repo_link.split('/')[-2:]
    gh = login(token='your_github_token')
    repository = gh.repository(owner, repo)

    # Fetch files (for simplicity, assuming all code is in the root directory)
    files = []
    for content in repository.directory_contents("/"):
        if content.type == "file" and content.name.endswith(".py"):  # Assuming Python files
            files.append(content.decoded.decode("utf-8"))
    return "\n".join(files)
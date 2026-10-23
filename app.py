from dotenv import load_dotenv
import os
from langchain_groq import ChatGroq
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, SimpleJsonOutputParser
from flask import Flask, request, jsonify

load_dotenv()

api_key = os.environ.get("GROQ_API_KEY")

if not api_key:
    raise KeyError("Groq Environment Key not Found")

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    api_key=api_key)

prompt = ChatPromptTemplate.from_messages([
    ("system", "Please rewrite the sentence after correcting all the errors and polishing it"),
    ("human", "{sentence}")
])

parser = StrOutputParser()

polishing_chain = prompt | llm | parser

chain = RunnableParallel(
    original_sentence=lambda x: x["sentence"],
    polished_answer=polishing_chain
)




app = Flask(__name__)
@app.route("/")
def welcome_page():
    return """
    <div class = "container">
    <h1>Welcome to Sentence Polisher Version 1.1</h1>

    <input
        type="text"
        id="sentence"
        placeholder="Enter a Sentence">
    <button id="polishButton" onclick="getSentence()">Polish your Sentence</button>
    <p id = "result">Polished Answer:</p>
    </div>

    <style>
        h1 {
            color: white;
            text-align: center;
        }
        body {
            background-color : #101827;
        }
        button {
            padding : 12px 20px;
            margin : 15px 0;
            border-radius : 10px;
            border : none;
            background-color : #466ee5;
            color : white;
            width : 100%;
            box-sizing : border-box;
        }
        input {
            background-color : #1d293b;
            color : white;
            padding : 12px;
            border : 1px solid #46546b;
            border-radius : 10px;
            width: 100%;
            box-sizing : border-box;
        }
        .container {
            max-width: 500px;
            margin: 60px auto;
            padding: 30px;
            background-color: #1d293b;
            border-radius: 15px;
            }
        #result {
            background-color : #132c29;
            color : white;
            padding : 15px;
            border-radius : 10px;
            line-height : 1.6;
        }
    </style>

    <script>
    async function getSentence() {
        let sentence = document.getElementById("sentence").value;
        let button = document.getElementById("polishButton");
        button.disabled = true;
        document.getElementById("result").textContent = "Polishing your sentence..."

        try {
        let response = await fetch("/polish", {
                method : "POST",
                headers : {
                    "Content-Type" : "application/json" 
                },
                body : JSON.stringify({sentence: sentence}) 
                });
        let data = await response.json();

        if (!response.ok) {
        document.getElementById("result").textContent = data.error
        return;
        }
        document.getElementById("result").textContent = data.polished_answer;
        } catch (error) {
            document.getElementById("result").textContent = "There is an Error"
        } finally {
            button.disabled = false;
        }
    }
    </script>
    """


@app.route("/polish", methods=["POST"])
def polish_sentence():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Sentence is not available for correction"}), 400
    sentence = data.get("sentence", "")
    if not sentence.strip():
        return jsonify({"error": "Sentence cannot be empty"}), 400
    answer = chain.invoke({"sentence": sentence})
    return jsonify(answer)

if __name__ == "__main__":
    app.run()








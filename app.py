import os
import requests
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv

# Carica le variabili dal file .env
load_dotenv()
HUGGING_FACE_API_KEY = os.getenv("HUGGING_FACE_API_KEY")

app = Flask(__name__)

# Funzione per la valutazione dell'idea
def evaluate_idea(user_idea):
    headers = {"Authorization": f"Bearer {HUGGING_FACE_API_KEY}"}
    data = {
        "inputs": f"Evaluate this idea in 5 aspects: Creativity, Feasibility, Market Potential, Inspirations, Virality/Execution: {user_idea}",
        "parameters": {"max_length": 200}
    }

    try:
        response = requests.post(
            "https://api-inference.huggingface.co/models/tiiuae/falcon-7b-instruct",
            headers=headers,
            json=data
        )
        response.raise_for_status()  # Verifica se ci sono errori HTTP

        # Gestione della risposta se la richiesta è andata a buon fine
        if response.status_code == 200:
            result = response.json()
            return result[0]["generated_text"]
        else:
            return f"Error: {response.status_code}, {response.text}"

    except requests.exceptions.RequestException as e:
        return f"Request Error: {str(e)}"

# Funzione per analizzare la valutazione e dividerla nei 5 aspetti
def parse_evaluation(evaluation):
    aspects = {
        "Creativity": 0,
        "Feasibility": 0,
        "Market Potential": 0,
        "Inspirations": 0,
        "Virality/Execution": 0
    }

    import random
    for aspect in aspects:
        aspects[aspect] = random.randint(50, 100)  # Punteggio tra 50 e 100

    final_score = sum(aspects.values()) / len(aspects)

    return aspects, final_score

# Rotta per la homepage
@app.route('/')
def home():
    return render_template('index.html')

# Rotta per valutare l'idea
@app.route('/evaluate', methods=['POST'])
def evaluate():
    data = request.json
    user_idea = data.get("idea", "")
    
    if not user_idea:
        return jsonify({"error": "No idea provided"}), 400
    
    # Valutazione dell'idea tramite l'API di Hugging Face
    evaluation = evaluate_idea(user_idea)
    
    # Analizza la valutazione e restituisce un punteggio dettagliato
    aspects, final_score = parse_evaluation(evaluation)
    
    # Restituisce i risultati
    return jsonify({
        "evaluation": evaluation,
        "detailed_evaluation": aspects,
        "final_score": final_score
    })

# Rotta per la sezione "Docs"
@app.route('/docs')
def docs():
    return render_template('docs.html')

# Rotta per la sezione "Roadmap"
@app.route('/roadmap')
def roadmap():
    return render_template('roadmap.html')

# Avvia il server
if __name__ == '__main__':
    app.run(debug=True)

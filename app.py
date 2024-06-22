from flask import Flask, render_template, request, jsonify
from functions import generate_ai_response, evaluate_translation
import time
import random

app = Flask(__name__)

with open('ethical_questions.txt', 'r') as file:
    ethical_questions = [line.strip() for line in file if line.strip()]

ethical_question = random.choice(ethical_questions)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    return jsonify({'text': ethical_question})

@app.route('/get_machine_response', methods=['POST'])
def get_machine_response():
    '''
    Add call to chatgpt here
    '''
    machine_response = generate_ai_response(ethical_question)
    return jsonify({'text': machine_response})

@app.route('/compare_responses', methods=['POST'])
def compare_responses():
    data = request.get_json()
    human_response = data.get('human_response', '')
    machine_response = data.get('machine_response', '')
    time.sleep(1.5)
    # For now, we will always return "human" as the winner
    result = evaluate_translation(human_response, machine_response, ethical_question)
    if result == 1:
        winner = 'human'
    else if result == 0:
        winner = 'machine'
    else:
        winner = 'error'
    '''
    Add scoring function here
    '''
    return jsonify({'winner': winner})

if __name__ == '__main__':
    app.run(debug=True)


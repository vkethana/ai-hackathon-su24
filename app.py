from flask import Flask, render_template, request, jsonify
from functions import generate_ai_response, evaluate_translation, get_ethical_question
import time
import random

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    return jsonify({'question': get_ethical_question()})

@app.route('/get_machine_response', methods=['POST'])
def get_machine_response():
    data = request.get_json()
    print("DATA = ", data)
    ethical_question = data.get('ethical_question', '')

    machine_response = generate_ai_response(ethical_question)
    return jsonify({'text': machine_response})

@app.route('/compare_responses', methods=['POST'])
def compare_responses():
    data = request.get_json()
    human_response = data.get('human_response', '')
    machine_response = data.get('machine_response', '')
    ethical_question = data.get('ethical_question', '')
    time.sleep(1.5)
    # For now, we will always return "human" as the winner
    result = evaluate_translation(human_response, machine_response, ethical_question)
    if result == 1:
        winner = 'human'
    elif result == 0:
        winner = 'machine'
    else:
        winner = 'error'
    '''
    Add scoring function here
    '''
    return jsonify({'winner': winner})

if __name__ == '__main__':
    app.run(debug=True)


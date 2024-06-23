from flask import Flask, render_template, request, jsonify
from functions import generate_ai_response, evaluate_translation, get_ethical_question
import time
import random
from flask_socketio import SocketIO, join_room, leave_room, emit
import uuid

app = Flask(__name__)
DISABLE_API_CALLS = True

app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)
games = {}

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

    if DISABLE_API_CALLS: # Use to speed up debugging
        machine_response = "Lorem ipsum dolor sit amet, consectetur adipiscing elit"
    else:
      machine_response = generate_ai_response(ethical_question)
    return jsonify({'text': machine_response})

@app.route('/compare_responses', methods=['POST'])
def compare_responses():
    data = request.get_json()
    human_response = data.get('human_response', '')
    machine_response = data.get('machine_response', '')
    ethical_question = data.get('ethical_question', '')
    time.sleep(1.5)

    if DISABLE_API_CALLS:
      result = 1
    else:
      result = evaluate_translation(human_response, machine_response, ethical_question)

    if result == 1:
        winner = 'human'
    elif result == 0:
        winner = 'machine'
    else:
        winner = 'error'
    return jsonify({'winner': winner})

if __name__ == '__main__':
    socketio.run(app, debug=True)

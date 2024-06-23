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

@socketio.on('join_game')
def on_join_game(data):
    game_code = data['game_code']
    if game_code not in games:
        games[game_code] = {
            'players': [],
            'responses': {},
            'question': get_ethical_question()
        }

    if len(games[game_code]['players']) < 2:
        join_room(game_code)
        games[game_code]['players'].append(request.sid)

        if len(games[game_code]['players']) == 2:
            emit('start_game', {'question': games[game_code]['question']}, room=game_code)
        else:
            emit('waiting_for_player', room=game_code)
    else:
        emit('game_full')

@socketio.on('submit_multiplayer_response')
def on_submit_multiplayer_response(data):
    game_code = data['game_code']
    response = data['response']
    games[game_code]['responses'][request.sid] = response

    if len(games[game_code]['responses']) == 2:
        if DISABLE_API_CALLS:
            ai_response = "Lorem ipsum dolor sit amet, consectetur adipiscing elit"
        else:
            ai_response = generate_ai_response(games[game_code]['question'])

        results = {}
        for player, resp in games[game_code]['responses'].items():
            if DISABLE_API_CALLS:
                result = random.choice([0, 1])
            else:
                result = evaluate_translation(resp, ai_response, games[game_code]['question'])
            results[player] = 'win' if result == 1 else 'lose'

        emit('game_result', {
            'results': results,
            'ai_response': ai_response
        }, room=game_code)
        del games[game_code]

if __name__ == '__main__':
    socketio.run(app, debug=True)

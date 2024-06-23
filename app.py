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

@app.route('/create_multiplayer_game', methods=['POST'])
def create_multiplayer_game():
    print("Creating Multiplayer Game")
    game_id = str(uuid.uuid4())
    games[game_id] = {
        'players': [],
        'responses': {},
        'question': get_ethical_question()
    }
    return jsonify({'game_id': game_id})

@socketio.on('join')
def on_join(data):
    print("Joining Multiplayer Game")
    game_id = data['game_id']
    if game_id in games and len(games[game_id]['players']) < 2:
        print("Game_id", game_id, "exists!")
        print("Total games", games)

        join_room(game_id)
        games[game_id]['players'].append(request.sid)
        print("Players in game", games[game_id]['players'])
        if len(games[game_id]['players']) == 2:
            emit('start_game', {'question': games[game_id]['question']}, room=game_id)

@socketio.on('submit_response')
def on_submit_response(data):
    game_id = data['game_id']
    response = data['response']
    games[game_id]['responses'][request.sid] = response

    if len(games[game_id]['responses']) == 2:
        # Both players have submitted, get AI response and compare
        ai_response = generate_ai_response(games[game_id]['question'])
        results = {}
        for player, resp in games[game_id]['responses'].items():
            result = evaluate_translation(resp, ai_response, games[game_id]['question'])
            results[player] = 'win' if result == 1 else 'lose'
        emit('game_result', {
            'results': results,
            'ai_response': ai_response
        }, room=game_id)
        # Clean up the game
        del games[game_id]

if __name__ == '__main__':
    socketio.run(app, debug=True)

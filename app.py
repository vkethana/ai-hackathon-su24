from flask import Flask, render_template, request, jsonify
from functions import generate_ai_response, evaluate_translation, get_ethical_question
import time
import random
from flask_socketio import SocketIO, join_room, leave_room, emit
import uuid

app = Flask(__name__)
DISABLE_API_CALLS = True

app.config['SECRET_KEY'] = 'my_secret'
socketio = SocketIO(app)
games = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    question = get_ethical_question()
    print("Question = ", question)
    return jsonify({'question': question})

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
def on_join(data):
    game_code = data['game_code']
    print("Joined with game code ", game_code)
    if game_code not in games:
        games[game_code] = {
            'players': [],
            'question': get_ethical_question(),
            'responses': {},
            'sid': {}
        }
        print("Made new game with code ", game_code)
    else:
        print("Joining existing game")

    if len(games[game_code]['players']) < 2:
        print("Game doesn't have 2 players")
        player_id = str(uuid.uuid4())
        join_room(game_code)
        games[game_code]['players'].append(player_id)
        games[game_code]['sid'][player_id] = request.sid
        emit('game_joined', {'player_id': player_id}, room=request.sid)
        print("Games now equals", games)

        if len(games[game_code]['players']) == 2:
            print("Both players joined, sending question")
            emit('game_ready', {'question': games[game_code]['question']}, room=game_code)
    else:
        emit('game_full', room=request.sid)

@socketio.on('submit_response')
def on_submit(data):
    game_code = data['game_code']
    player_id = data['player_id']
    response = data['response']

    games[game_code]['responses'][player_id] = response
    print("Received response from player ", player_id)
    print("Responses now equal ", games[game_code]['responses'])
    print("Games now equal ", games)

    if len(games[game_code]['responses']) == 2:
        print("Emitting both_responded")
        # send to both users
        # make JSON of both players' responses
        emit('both_responded', {'responses': games[game_code]['responses']}, room=game_code)
        #emit('both_responded', room=game_code)
        #other_player = [p for p in games[game_code]['players'] if p != player_id][0]
        #emit('both_responded', room=games[game_code]['sid'][other_player])

        player1, player2 = games[game_code]['players']
        '''
        result = evaluate_translation(games[game_code]['responses'][player1], 
                                      games[game_code]['responses'][player2], 
                                      games[game_code]['question'])
        '''
        time.sleep(1.5)
        result = 1

        winner = player1 if result == 1 else player2
        print("Emitting game result")
        print("Result is ", result)
        emit('game_result', {'winner': winner}, room=game_code)

        # Clean up the game
        del games[game_code]
    else:
      print("Both people haven't responded yet, so I will do nothing")

if __name__ == '__main__':
    socketio.run(app, debug=True)

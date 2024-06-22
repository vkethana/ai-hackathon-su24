from flask import Flask, render_template, request, jsonify
import time

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    lorem_text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
    return jsonify({'text': lorem_text})

@app.route('/get_machine_response', methods=['POST'])
def get_machine_response():
    '''
    Add call to chatgpt here
    '''
    machine_response = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
    return jsonify({'text': machine_response})

@app.route('/compare_responses', methods=['POST'])
def compare_responses():
    data = request.get_json()
    human_response = data.get('human_response', '')
    machine_response = data.get('machine_response', '')
    time.sleep(1.5)
    # For now, we will always return "human" as the winner
    winner = 'human' # or winner = 'machine'
    '''
    Add scoring function here
    '''
    return jsonify({'winner': winner})

if __name__ == '__main__':
    app.run(debug=True)


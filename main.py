from flask import Flask, render_template, jsonify, request
import openAiAPI
import os

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def home():
    if request.method == "POST":
        prompt = request.form.get('prompt', '')
        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400

        try:
            result = {'ai_answer': openAiAPI.get_open_ai_api_chat_response(prompt)}
            return jsonify(result)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return render_template('home.html', **locals())

if __name__ == '__main__':
    app.run(debug=True)

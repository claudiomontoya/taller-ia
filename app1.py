from flask import Flask, request, jsonify
from openai import OpenAI
import groq

app = Flask(__name__)

OPENAI_API_KEY = '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'
GROQ_API_KEY = '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'

openai_client = OpenAI(api_key=OPENAI_API_KEY)
groq_client = groq.Groq(api_key=GROQ_API_KEY)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('mensaje')
    params = data.get('params', {})

    if not user_message:
        return jsonify({"error": "Mensaje no enviado"}), 400

    openai_response = GptOpenai(user_message, params)
    groq_response = GptGroq(user_message, params)

    combined_response = {
        "openai_response": openai_response,
        "groq_response": groq_response
    }

    return jsonify(combined_response)

def GptOpenai(message, params):
    try:
        response = openai_client.chat.completions.create(
            model=params.get('model', "gpt-3.5-turbo"),
            messages=[
                {"role": "system", "content": "responde siempre en ingles."},
                {"role": "user", "content": message}
            ], temperature=params.get('temperature', 0.1),
           
            max_tokens=params.get('max_tokens', 500),
            top_p=params.get('top_p', 1.0)
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error OpenAI: {str(e)}"

def GptGroq(message, params):
    try:
        response = groq_client.chat.completions.create(
            model=params.get('model', "mixtral-8x7b-32768"),
            messages=[
                {"role": "system", "content": "Eres un asistente de ayuda."},
                {"role": "user", "content": message}
            ],
            temperature=params.get('temperature', 0.9),
            max_tokens=params.get('max_tokens', 500),
            top_p=params.get('top_p', 1.0)
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error Groq: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
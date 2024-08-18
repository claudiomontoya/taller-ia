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

    if not user_message:
        return jsonify({"error": "Mensaje no enviado"}), 400

    openai_response = GptOpenai(user_message)

    groq_response = GptGroq(user_message)

    combined_response = {
        "openai_response": openai_response,
        "groq_response": groq_response
    }

    return jsonify(combined_response)

def GptOpenai(message):
    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un asistente de ayuda."},
                {"role": "user", "content": message}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error OpenAI: {str(e)}"

def GptGroq(message):
    try:
        response = groq_client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[
                {"role": "system", "content": "Eres un asistente de ayuda."},
                {"role": "user", "content": message}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error Groq: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, request, jsonify
import groq
from uuid import uuid4

app = Flask(__name__)

GROQ_API_KEY = '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'
groq_client = groq.Groq(api_key=GROQ_API_KEY)

conversations = {}

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('mensaje')
    conversation_id = data.get('conversation_id')

    if not user_message:
        return jsonify({"error": "Mensaje no enviado"}), 400

    if not conversation_id:
        conversation_id = str(uuid4())
        conversations[conversation_id] = []

    response = process_with_groq(user_message, conversation_id)
    return jsonify({
        "respuesta": response,
        "conversation_id": conversation_id
    })

def process_with_groq(message, conversation_id):
    conversation = conversations.get(conversation_id, [])
    
    conversation.append({"role": "user", "content": message})
    conversation = conversation[-10:]
    
    try:
        response = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "Eres un asistente amigable y útil con buena memoria. Responde de manera concisa y personalizada basándote en el contexto de la conversación."},
                *conversation
            ],
            temperature=0.7,
            max_tokens=1500
        )
        
        assistant_message = response.choices[0].message.content     
        conversation.append({"role": "assistant", "content": assistant_message})
        conversations[conversation_id] = conversation
        
        return assistant_message
    except Exception as e:
        return f"Lo siento, ocurrió un error: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, request, jsonify
import groq
from uuid import uuid4

app = Flask(__name__)

GROQ_API_KEY = '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'
groq_client = groq.Groq(api_key=GROQ_API_KEY)



@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('mensaje')
    if not user_message:
        return jsonify({"error": "Mensaje no enviado"}), 400

    response = process_with_groq(user_message)
    return jsonify({
        "respuesta": response
    })

def process_with_groq(message):
    
   
    try:
        response = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "Eres un asistente amigable y útil con buena memoria. Responde de manera concisa y personalizada basándote en el contexto de la conversación."},
                {"role": "user", "content": message}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        
        assistant_message = response.choices[0].message.content           
        return assistant_message
    except Exception as e:
        return f"Lo siento, ocurrió un error: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
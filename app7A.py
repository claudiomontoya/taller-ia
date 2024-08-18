from flask import Flask, request, jsonify
import groq
from uuid import uuid4
from qdrant_client import QdrantClient
from qdrant_client.http import models
from openai import OpenAI

app = Flask(__name__)

GROQ_API_KEY = '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'
QDRANT_HOST = "7b69c29e-45d9-4688-bbd8-291100ea83f6.europe-west3-0.gcp.cloud.qdrant.io"
QDRANT_PORT = 6333
QDRANT_API_KEY = "_gSHg9KZHIsM419jTQjTQ2pm_Vz7GFC00epXuHBVANMotV20T5QliQ"
OPENAI_API_KEY = "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"

groq_client = groq.Groq(api_key=GROQ_API_KEY)
qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT, api_key=QDRANT_API_KEY)
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def generar_embedding(texto):
    response = openai_client.embeddings.create(
        model="text-embedding-ada-002",
        input=texto
    )
    return response.data[0].embedding

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('mensaje')
    if not user_message:
        return jsonify({"error": "Mensaje no enviado"}), 400

    response = process_with_groq_and_qdrant(user_message)
    return jsonify({
        "respuesta": response
    })

def process_with_groq_and_qdrant(message):
    try:
        search_results = search_in_qdrant(message)
        context = "Información relevante encontrada:\n"
        for result in search_results:
            context += f"- Título: {result.payload['titulo']}\n"
            context += f"  Descripción: {result.payload['descripcion']}\n"
            context += f"  Empresa: {result.payload['empresa']}\n"
            context += f"  Ubicación: {result.payload['region']}, {result.payload['comuna']}\n\n"
        prompt = f"""Basándote en la siguiente información y la pregunta del usuario, proporciona una respuesta útil y concisa.

Información relevante:
{context}

Pregunta del usuario: {message}

Respuesta:"""

        response = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "Eres un asistente amigable y útil. Responde de manera concisa y personalizada basándote en el contexto proporcionado y la pregunta del usuario."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2500
        )

        assistant_message = response.choices[0].message.content
        return assistant_message
    except Exception as e:
        return f"Lo siento, ocurrió un error: {str(e)}"

def search_in_qdrant(query):
    query_vector = generar_embedding(query)
    search_result = qdrant_client.search(
        collection_name="ofertas_trabajo",
        query_vector=query_vector,
        limit=5 
    )
    return search_result

if __name__ == '__main__':
    app.run(debug=True)
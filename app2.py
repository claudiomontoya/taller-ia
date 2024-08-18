from flask import Flask, request, jsonify
import groq
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List
app = Flask(__name__)

GROQ_API_KEY = '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'
groq_client = groq.Groq(api_key=GROQ_API_KEY)

class ProductInfo(BaseModel):
    producto: str = Field(description="Nombre del producto solo una palabra")
    descripcion: str = Field(description="Descripción emocional del producto")
    sinonimos: List[str] = Field(description="Lista de sinónimos o términos relacionados al producto")

parser = PydanticOutputParser(pydantic_object=ProductInfo)

prompt_template = PromptTemplate(
    template="Identifica el producto en el siguiente mensaje y genera una descripción emocional para él:\n{query}\n{format_instructions}",
    input_variables=["query"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('mensaje')

    if not user_message:
        return jsonify({"error": "Mensaje no enviado"}), 400

    response = process_with_groq(user_message)
    return jsonify(response)

def process_with_groq(message):
    try:
        _input = prompt_template.format_prompt(query=message)
        response = groq_client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[
                {"role": "system", "content": "Eres un asistente especializado en productos."},
                {"role": "user", "content": _input.to_string()}
            ],
            temperature=0.2,
            max_tokens=500
        )
        output = response.choices[0].message.content
        parsed_output = parser.parse(output)
        return parsed_output.dict()
    except Exception as e:
        return {"error": f"Error al procesar con Groq: {str(e)}"}

if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, request, jsonify
import groq
import json

app = Flask(__name__)

GROQ_API_KEY = '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'
groq_client = groq.Groq(api_key=GROQ_API_KEY)

def informacion_producto(producto):
    print("Informacion de producto")
    return f"Aquí tienes información sobre el producto: {producto}"

def reclamo(detalle):
    print("reclamo")
    return f"Lamento que tengas un problema. He registrado tu reclamo: {detalle}"

def comprar(producto):
    print("comprar")
    return f"Excelente elección. Aquí tienes los pasos para comprar: {producto}"

tools = [
    {
        "type": "function",
        "function": {
            "name": "informacion_producto",
            "description": "Obtener información sobre un producto del area de vehiculos como repuestos o ascesorios",
            "parameters": {
                "type": "object",
                "properties": {
                    "producto": {
                        "type": "string",
                        "description": "El nombre del producto sobre el que se quiere información solo repuestos o ascesorios de vehiculos"
                    }
                },
                "required": ["producto"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "reclamo",
            "description": "Registrar un reclamo o queja",
            "parameters": {
                "type": "object",
                "properties": {
                    "detalle": {
                        "type": "string",
                        "description": "Detalles del reclamo o queja"
                    }
                },
                "required": ["detalle"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "comprar",
            "description": "Iniciar proceso de compra de un producto",
            "parameters": {
                "type": "object",
                "properties": {
                    "producto": {
                        "type": "string",
                        "description": "El producto que se desea comprar"
                    }
                },
                "required": ["producto"]
            }
        }
    }
]

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
        response = groq_client.chat.completions.create(
            model="llama3-groq-8b-8192-tool-use-preview",
            messages=[
                {"role": "system", "content": "Eres un asistente que ayuda a los clientes con información de productos, reclamos y compras."},
                {"role": "user", "content": message}
            ],
            tools=tools,
            tool_choice="auto",
            temperature=0.9,
            max_tokens=1500
        )
        
        if response.choices[0].message.tool_calls:
            tool_call = response.choices[0].message.tool_calls[0]
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            if function_name == "informacion_producto":
                result = informacion_producto(function_args["producto"])
            elif function_name == "reclamo":
                result = reclamo(function_args["detalle"])
            elif function_name == "comprar":
                result = comprar(function_args["producto"])
            else:
                result = "No se pudo procesar la solicitud."
            
            return {"respuesta": result}
        else:
            return {"respuesta": response.choices[0].message.content}
    except Exception as e:
        return {"error": f"Error al procesar con Groq: {str(e)}"}

if __name__ == '__main__':
    app.run(debug=True)
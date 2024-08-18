import json
import uuid
from qdrant_client import QdrantClient
from qdrant_client.http import models
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor
import time

QDRANT_HOST = "7b69c29e-45d9-4688-bbd8-291100ea83f6.europe-west3-0.gcp.cloud.qdrant.io"
QDRANT_PORT = 6333
QDRANT_API_KEY = "_gSHg9KZHIsM419jTQjTQ2pm_Vz7GFC00epXuHBVANMotV20T5QliQ"
OPENAI_API_KEY = "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"

BATCH_SIZE = 10
MAX_WORKERS = 4

client = OpenAI(api_key=OPENAI_API_KEY)
qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT, api_key=QDRANT_API_KEY)

def generar_embedding(texto):
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=texto
    )
    return response.data[0].embedding

def procesar_oferta(oferta):
    try:
        texto_combinado = f"{oferta['titulo']} {oferta['descripcion']} {oferta['empresa']} {oferta['region']} {oferta['comuna']}"
        embedding = generar_embedding(texto_combinado)
        
        return models.PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload=oferta
        )
    except Exception as e:
        print(f"Error al procesar oferta: {str(e)}")
        return None

def procesar_lote(lote):
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        resultados = list(executor.map(procesar_oferta, lote))
    return [r for r in resultados if r is not None]

def cargar_en_qdrant(ofertas):
    qdrant_client.recreate_collection(
        collection_name="ofertas_trabajo2",
        vectors_config=models.VectorParams(size=1536, distance=models.Distance.COSINE)
    )
    
    total_ofertas = len(ofertas)
    ofertas_cargadas = 0
    tiempo_inicio = time.time()

    for i in range(0, total_ofertas, BATCH_SIZE):
        lote = ofertas[i:i+BATCH_SIZE]
        puntos_procesados = procesar_lote(lote)
        
        if puntos_procesados:
            qdrant_client.upsert(
                collection_name="ofertas_trabajo2",
                points=puntos_procesados
            )
        
        ofertas_cargadas += len(puntos_procesados)
        tiempo_transcurrido = time.time() - tiempo_inicio
        velocidad = ofertas_cargadas / tiempo_transcurrido if tiempo_transcurrido > 0 else 0
        
        print(f"Progreso: {ofertas_cargadas}/{total_ofertas} ofertas cargadas. "
              f"Velocidad: {velocidad:.2f} ofertas/segundo")

    tiempo_total = time.time() - tiempo_inicio
    print(f"Carga completada. Se cargaron {ofertas_cargadas} ofertas en {tiempo_total:.2f} segundos.")

def main():
    tiempo_inicio_total = time.time()
    
    with open('data.json', 'r', encoding='utf-8') as f:
        ofertas = json.load(f)
    
    print(f"Se han leído {len(ofertas)} ofertas del archivo JSON.")
    cargar_en_qdrant(ofertas)
    
    tiempo_total = time.time() - tiempo_inicio_total
    print(f"Tiempo total de ejecución: {tiempo_total:.2f} segundos")

if __name__ == "__main__":
    main()
import requests
import json
import re
import html

base_url = "https://www.bne.cl/data/ofertas/buscarListas?mostrar=empleo&idRegion=378&idRegion=384&fechaIniPublicacion=&numPaginaRecuperar={}&numResultadosPorPagina=100&clasificarYPaginar=true"

def limpiar_descripcion(texto):
    texto_decodificado = html.unescape(texto)
    texto_limpio = re.sub(r'[\r\n]+', ' ', texto_decodificado.strip())
    texto_limpio = texto_limpio.lower()
    texto_limpio = re.sub(r'[^a-záéíóúñü\s]', '', texto_limpio)
    texto_limpio = re.sub(r'\s+', ' ', texto_limpio)
    return texto_limpio

def obtener_ofertas_pagina(num_pagina):
    url = base_url.format(num_pagina)
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error al obtener los datos de la página {num_pagina}: {response.status_code}")
        return None

todas_las_ofertas = []
datos = obtener_ofertas_pagina(1)

if datos:
    total_paginas = datos.get("paginaOfertas", {}).get("numPaginasTotal", 1)
    
    for pagina in range(1, total_paginas + 1):
        print(f"Obteniendo datos de la página {pagina} de {total_paginas}...")
        datos_pagina = obtener_ofertas_pagina(pagina)
        
        if datos_pagina:
            resultados = datos_pagina.get("paginaOfertas", {}).get("resultados", [])
            
            for oferta in resultados:
                descripcion_limpia = limpiar_descripcion(oferta.get("descripcion", ""))
                titulo_limpia = limpiar_descripcion(oferta.get("titulo", ""))
                todas_las_ofertas.append({
                    "id": oferta.get("id"),
                    "codigo": oferta.get("codigo"),
                    "fecha": oferta.get("fecha"),
                    "titulo": titulo_limpia,
                    "descripcion": descripcion_limpia,
                    "empresa": oferta.get("empresa"),
                    "region": oferta.get("region"),
                    "comuna": oferta.get("comuna")
                })
else:
    print("No se pudieron obtener los datos iniciales.")
    
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(todas_las_ofertas, f, ensure_ascii=False, indent=2)

print(f"Se han guardado {len(todas_las_ofertas)} ofertas en el archivo data.json")
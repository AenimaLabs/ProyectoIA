import os
import requests
from dotenv import load_dotenv


import time

import json
import re


load_dotenv()

# MODELO = "gemini-flash-latest"
modelo = "gemini-3.1-flash-lite"
URL_BASE = f"https://generativelanguage.googleapis.com/v1beta/models/"
API_KEY = os.getenv("GEMINI_API_KEY")

SYSTEM_INSTRUCTIONS_PEDAGOGICO = (
    "Eres un asistente pedagógico de programación en Python. "
    "Evalúa funciones entregadas por estudiantes usando preguntas guía "
    "para que detecten casos borde y buenas prácticas por sí mismos. "
    "No entregues el código resuelto y mantén respuestas breves y claras."
)


#función para crear la solicitud
def crear_solicitud(pregunta, modelo, system_instructions, response_schema=None):
    if not pregunta or not pregunta.strip():
        raise ValueError("La pregunta no puede estar vacía.")

    if not API_KEY:
        raise ValueError("La clave de API no está configurada. Por favor, establece la variable de entorno GEMINI_API_KEY.")
    

    url = f"{URL_BASE}{modelo}:generateContent?key={API_KEY}"
    body = {
        "systemInstruction": {
            "parts": [
                {
                    "text": system_instructions
                }
            ]
        },
        "contents": [
            {
                "parts": [
                    {
                        "text": pregunta
                    }
                ]
            }
        ],
       
    }

    if response_schema is not None:
        body["generationConfig"] = {
            "responseMimeType": "application/json",
            "responseSchema": response_schema
        }

    return url, body

#función envía la petición
#añadir manejo de errores para la petición

def enviar_peticion(url, body):
    """Envía una solicitud POST a la API de Gemini y devuelve la respuesta en formato JSON."""

    try:
        respuesta = requests.post(url, json=body, timeout=30)  # Añadido un tiempo de espera de 30 segundos
    except requests.exceptions.ConnectionError as err:
        raise RuntimeError("Error de conexión al enviar la petición.") from err
    except requests.exceptions.Timeout as err:
        raise RuntimeError("La petición ha superado el tiempo de espera.") from err

    if respuesta.status_code != 200:
        raise RuntimeError(f"Error en la petición: {respuesta.status_code} - {respuesta.text}")
    
    try:
        return respuesta.json()
    except requests.exceptions.JSONDecodeError as err:
        raise RuntimeError("Error al decodificar la respuesta JSON.") from err



#función procesa y extrae la respuesta
#añadir manejo de errores para la respuesta
def procesar_respuesta(datos): #Gemini
    """Procesa la respuesta de la API de Gemini y extrae el texto generado."""

    try:
        return datos["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError) as err:
        """revisa si la respuesta fue bloqueada por filtros de seguridad"""
        motivo_bloqueo = datos.get("candidates", [{}])[0].get("finishReason", "Desconocido")
        raise RuntimeError(f"La respuesta fue bloqueada por filtros de seguridad: {motivo_bloqueo}") from err

    

#función principal que obtiene el dato de prueba
#añadir manejo de errores para la respuesta
def obtener_dato_de_prueba(pregunta):
    """Ejecuta una petición de prueba, mide su latencia y costo, y devuelve la respuesta."""

    response_schema = {
        "type": "OBJECT",
        "properties": {
            "categoria": {"type": "STRING"},
            "confianza": {"type": "NUMBER"},
        },
        "required": ["categoria", "confianza"]
    }


    system_instructions = SYSTEM_INSTRUCTIONS_PEDAGOGICO
    
    url, body = crear_solicitud(pregunta, modelo, system_instructions, response_schema)

    #contador de tiempo para medir la duración de la solicitud
    inicio = time.perf_counter()
    datos = enviar_peticion(url, body)
    fin = time.perf_counter()

    latencia = fin - inicio
    print(f"Modelo utilizado: {modelo}")
    print(f"Tiempo de respuesta (latencia): {latencia:.2f} segundos")

    costo = calcular_costos(datos, 0.00000075, 0.00000375)  # Ejemplo de precios por token
    print(f"Costo estimado de la solicitud: ${costo:.6f} USD")

    texto = procesar_respuesta(datos)
    datos_formateados = parsear_respuesta_json(texto,  claves_requeridas=["categoria", "confianza"])
    
    return datos_formateados

#funcion calcular costos
#def calcular_costos(datps:dict, precio_entrada:float, precio_salida:float)
def calcular_costos(datos, precio_entrada, precio_salida):
    """Calcula el costo monetario total según los metadatos de tokens utilizados"""
    uso = datos.get("usageMetadata", {})

    # uso = {
    #     "promptTokenCount": 35,
    #     "candidatesTokenCount": 310,
    #     "totalTokenCount": 1041,
    #     "promptTokensDetails": [
    #         {
    #             "modality": "TEXT",
    #             "tokenCount": 35
    #         }
    #     ],
    #     "thoughtsTokenCount": 696,
    #     "serviceTier": "standard"
    # },
    tokens_entrada = uso.get("promptTokenCount", 0)
    tokens_salida = uso.get("candidatesTokenCount", 0)
    tokens_razonamiento = uso.get("thoughtsTokenCount", 0)  # Algunos modelos pueden no tener este campo
    costo = (tokens_entrada * precio_entrada) + (tokens_salida * precio_salida) + (tokens_razonamiento * precio_salida)
    print(f"Tokens de entrada: {tokens_entrada}")
    print(f"Tokens de salida: {tokens_salida}")
    print(f"Tokens de razonamiento: {tokens_razonamiento}")
    return costo

def parsear_respuesta_json(texto_respuesta, claves_requeridas=None):
    """Limpia un texto con JSON (incluso si viene en bloque Markdown),
    lo convierte a diccionario y valida que existan las claves requeridas.
    claves_requeridas: lista de claves que deben estar presentes en el JSON.
    """

    texto_limpio = texto_respuesta.strip()
    texto_limpio = re.sub(r"^```(?:json)?\s*", "", texto_limpio)
    texto_limpio = re.sub(r"\s*```$", "", texto_limpio)
    texto_limpio = texto_limpio.strip()

    try:
        datos = json.loads(texto_limpio)
    except json.JSONDecodeError as e:
        raise ValueError(f"La respuesta del modelo no es un JSON válido: {e}") from e

    if not isinstance(datos, dict):
        raise ValueError("La respuesta JSON debe ser un objeto/diccionario.")

    if claves_requeridas:
        faltantes = [clave for clave in claves_requeridas if clave not in datos]
        if faltantes:
            raise ValueError(f"Faltan claves requeridas en la respuesta JSON: {', '.join(faltantes)}")
        

    return datos

try:
   
    print(obtener_dato_de_prueba("Dame una frase motivacional para empezar el día"))
except (ValueError, RuntimeError) as e:
    print(f"Error: {e}")



# def obtener_dato_de_prueba(pregunta):
#     api_key = os.getenv("GEMINI_API_KEY")

#     modelo = "gemini-flash-latest"

#     url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent?key={api_key}"
#     body = {
#     "contents": [
#       {
#         "parts": [
#           {
#             "text": pregunta
#           }
#             ]
#         }
#         ]
#     }
#     respuesta = requests.post(url, json=body)
#     datos = respuesta.json()
#     return datos["candidates"][0]["content"]["parts"][0]["text"]


'''
ejecuta 4 veces la misma petición con 1 modelo
y ante cada petición se calcule e imprima: latencia, costo, respuesta

vuelvo a hacer lo mismo con un modelo distinto
3 modelos a comparar

objetivo: elijas el mejor modelo para tu proyecto

Promp que sea algo relacionado con tu proyecto.
'''

 
import os
import requests
from dotenv import load_dotenv


load_dotenv()

MODELO = "gemini-flash-latest"
URL_BASE = f"https://generativelanguage.googleapis.com/v1beta/models/"
API_KEY = os.getenv("GEMINI_API_KEY")


#función para crear la solicitud
def crear_solicitud(pregunta):
    
    url = f"{URL_BASE}{MODELO}:generateContent?key={API_KEY}"
    body = {
        "contents": [
            {
                "parts": [
                    {
                        "text": pregunta
                    }
                ]
            }
        ]
    }
    return url, body

#función envía la petición
def enviar_peticion(url, body):
    respuesta = requests.post(url, json=body)
    return respuesta.json()

#función procesa y extrae la respuesta
def procesar_respuesta(datos): #Gemini
    return datos["candidates"][0]["content"]["parts"][0]["text"]

#función principal que obtiene el dato de prueba
def obtener_dato_de_prueba(pregunta):
    url, body = crear_solicitud(pregunta)
    datos = enviar_peticion(url, body)
    return procesar_respuesta(datos)


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

print(obtener_dato_de_prueba("Dame una frase motivacional para empezar el día"))

import os
import requests
from dotenv import load_dotenv


load_dotenv()

MODELO = "gemini-flash-latest"
URL_BASE = f"https://generativelanguage.googleapis.com/v1beta/models/"
API_KEY = os.getenv("GEMINI_API_KEY")


#función para crear la solicitud
def crear_solicitud(pregunta):
    if not pregunta:
        raise ValueError("La pregunta no puede estar vacía.")

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
#añadir manejo de errores para la petición
def enviar_peticion(url, body):
    try:
        respuesta = requests.post(url, json=body, timeout=30)  # Añadido un tiempo de espera de 30 segundos
    except requests.exceptions.ConnectionError:
        raise RuntimeError("Error de conexión al enviar la petición.")
    except requests.exceptions.Timeout:
        raise RuntimeError("La petición ha superado el tiempo de espera.")

    if respuesta.status_code != 200:
        raise RuntimeError(f"Error en la petición: {respuesta.status_code} - {respuesta.text}")
    
    try:
        return respuesta.json()
    except requests.exceptions.JSONDecodeError:
        raise RuntimeError("Error al decodificar la respuesta JSON.")



#función procesa y extrae la respuesta
#añadir manejo de errores para la respuesta
def procesar_respuesta(datos): #Gemini
    try:
        return datos["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        raise RuntimeError("La respuesta no recibe el texto generado en el lugar definido.")

    

#función principal que obtiene el dato de prueba
#añadir manejo de errores para la respuesta
def obtener_dato_de_prueba(pregunta):
    url, body = crear_solicitud(pregunta)
    datos = enviar_peticion(url, body)
    return procesar_respuesta(datos)

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

try:
    print(obtener_dato_de_prueba("Dame una frase motivacional para empezar el día"))
except (ValueError, RuntimeError) as e:
    print(f"Error: {e}")

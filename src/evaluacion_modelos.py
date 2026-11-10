import consumir_gemini
import time

def evaluar_modelo(nombre_modelo, pregunta, precio_entrada, precio_salida, repeticiones=4):

    """
    ejecuta 'repeticiones' veces la misma petición para un modelo específico.
    calcula e imprime la latencia, el costo y la respuesta para cada petición.
    además del promedio de latencia al final.
    """

    print("="*70)
    print(f"Evaluando modelo: {nombre_modelo}")
    print("="*70)

    latencias = []
    costos = []

    for i in range(1, repeticiones + 1):
        print(f"\n---Intento {i} de {repeticiones} ({nombre_modelo}):---")

        # 1. armar petición (puedes pasar el modelo si tu función lo requiere)
        url, body = consumir_gemini.crear_solicitud(pregunta, nombre_modelo)


        # 2. medir latencia
        inicio = time.perf_counter()
        datos = consumir_gemini.enviar_peticion(url, body)
        fin = time.perf_counter()

        latencia = fin - inicio
        latencias.append(latencia)

        # 3. calcular costo
        costo = consumir_gemini.calcular_costos(datos, precio_entrada, precio_salida)
        costos.append(costo)

        # 4. imprimir resultados
        respuesta = datos["candidates"][0]["content"]["parts"][0]["text"]
        
        ''' imprime tokens de entrada y salida, latencia, costo y respuesta '''

        print(f"Tokens de entrada: {datos.get('usageMetadata', {}).get('promptTokenCount', 0)}")
        print(f"Tokens de salida: {datos.get('usageMetadata', {}).get('candidatesTokenCount', 0)}")


        print(f"Latencia: {latencia:.4f} segundos")
        print(f"Costo: ${costo:.10f}")
        print(f"Respuesta: {respuesta.strip()}")

        time.sleep(1)  # Pausa de 1 segundo entre peticiones para evitar sobrecarga

        # resumen acumulado del modelo
    if latencias:
        latencia_promedio = sum(latencias) / len(latencias)
        costo_total = sum(costos)

        print("\n" + "="*70)
        print(f"\nResumen acumulado para {nombre_modelo}:")
        print(f"Latencia promedio: {latencia_promedio:.2f} segundos")
        print(f"Costo acumulado: ({repeticiones} peticiones): ${costo_total:.6f} USD")

pregunta_prueba = """Actúa como asistente pedagógico de programación.
Evalúa la siguiente función Python entregada por un estudiante:

def calcular_promedio(lista):
    suma = 0
    for x in lista:
        suma = suma + x
    return suma / len(lista)

Rúbrica:
1. Manejo de listas vacías o tipos no numéricos.
2. Uso de buenas prácticas y funciones nativas.

Instrucción:
Entrega una retroalimentación formativa de máximo 3 líneas. No entregues el código resuelto; formula preguntas guía que ayuden al estudiante a detectar el caso borde por sí mismo."""
modelos = [
    {
        "nombre": "gemini-3.6-flash",
        "precio_entrada": 0.00000010,
        "precio_salida": 0.0000030
    },
    {
        "nombre": "gemini-3.1-flash-lite",
        "precio_entrada": 0.00000075,
        "precio_salida": 0.00000375
    },
    {
        "nombre": "gemini-3.8-flash",
        "precio_entrada": 0.00000250,
        "precio_salida": 0.000001000
    }
]

# procesar los 3 modelos consecutivamente
for config in modelos:
    try:
        evaluar_modelo(
            nombre_modelo=config["nombre"],
            pregunta=pregunta_prueba,
            precio_entrada=config["precio_entrada"],
            precio_salida=config["precio_salida"],
            repeticiones=4
        )
    except Exception as e:
        print(f"Error al evaluar el modelo {config['nombre']}: {e}")

        




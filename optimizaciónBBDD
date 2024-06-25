import requests
import json
import time
import urllib.parse

# Configuración de la conexión con el servidor InfluxDB
host = server_IP # PC LAB
puerto = server_port
base_datos = BBDD_name
medida = 'intensidad'
canales = ['0', '1', '2', '3', '4', '5', '6', '7'] # Canales a filtrar

# Parámetros de configuración
tolerancia = 0.1 # Tolerancia para identificar valores repetidos
num_valores = 3000000 # Número máximo de valores a analizar en cada ejecución

# URL para la eliminación de puntos de datos
url = "http://{0}:{1}/write?db={2}".format(host, puerto, base_datos)

def codigo():
 for canal in canales:
 # Realizar solicitud para obtener los últimos valores
 consulta = "SELECT * FROM {0} WHERE canal='{1}' ORDER BY time DESC LIMIT {2}".format(base_datos, canal, num_valores)
 consulta = urllib.parse.quote(consulta)
 get = requests.get("http://{0}:{1}/query?db={2}&q={3}".format(host, puerto, base_datos, consulta))
 # Procesar la respuesta JSON
 data = json.loads(get.content)
 puntos = data['results'][0]['series'][0]['values']
 # Lista para almacenar los puntos de datos a eliminar
 puntos_a_eliminar = []
 # Variables auxiliares para el filtrado
 valor_anterior = None
 repeticiones = 0
 # Iterar sobre los puntos de datos y determinar los puntos a eliminar
 for punto in puntos:
 valor_actual = punto[1]
 if valor_anterior is None:
 # Primer valor
 valor_anterior = valor_actual
 else:
 if abs(valor_actual - valor_anterior) <= tolerancia:
 # Valor repetido dentro de la tolerancia
 repeticiones += 1
 puntos_a_eliminar.append(punto)
 else:
 # Nuevo valor, no repetido
 valor_anterior = valor_actual
 # Eliminar los puntos de datos repetidos
 for punto in puntos_a_eliminar:
 tiempo = punto[0]
 consulta = "DELETE FROM {0} WHERE time = '{1}'".format(base_datos, tiempo)
 consulta = urllib.parse.quote(consulta)
 borrar = requests.get("http://{0}:{1}/query?db={2}&q={3}".format(host, puerto, base_datos, consulta))
 print(borrar.content)
 
codigo()

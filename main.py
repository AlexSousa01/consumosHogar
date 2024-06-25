from m5stack import *
from m5ui import *
from uiflow import *
import urequests
import json
import time
import machine
setScreenColor(0x111111)

#Inicializar valores
ejecutando=False # Booleano que si esta en true se ejecuta el programa
sensibilidad=0.185 # Voltios/Amperio en el sensor

#Inicializamos contadores y lista
contador_periodo=0
contador_medidas=0
lista_medidas=[]
canales_activos=0

#Inicializar ADC (convertidor analogico-digital)
adc = machine.ADC(36) #Puerto G36
adc.width(machine.ADC.WIDTH_10BIT) #10 bits
adc.atten(machine.ADC.ATTN_11DB) #Atenuacion 11 decibelios

#Inicializar selectores de canal a cero
cs_0 = machine.Pin(17, machine.Pin.OUT) #selector de canal A0
cs_1 = machine.Pin(2, machine.Pin.OUT) #selector de canal A1
cs_2 = machine.Pin(5, machine.Pin.OUT) #selector de canal A2
cs_0.value(0)
cs_1.value(0)
cs_2.value(0)

#Escribir en la pantalla
triangle0 = M5Triangle(249, 230, 219, 200, 278, 200, 0x222222, 0xFFFFFF)
triangle1 = M5Triangle(69, 201, 39, 231, 99, 231, 0x222222, 0xFFFFFF)
label0 = M5TextBox(53, 160, "Canales activos:", lcd.FONT_Default, 0xFFFFFF, rotate=0)
label_RUN = M5TextBox(138, 210, "RUN", lcd.FONT_Default, 0xFFFFFF, rotate=0)
label_ch_act = M5TextBox(189, 160, "0", lcd.FONT_Default, 0xFFFFFF, rotate=0)
label3 = M5TextBox(10, 25, "canal 0", lcd.FONT_Default, 0xFFFFFF, rotate=0)
label4 = M5TextBox(10, 50, "canal 1", lcd.FONT_Default, 0xFFFFFF, rotate=0)
label5 = M5TextBox(10, 76, "canal 2", lcd.FONT_Default, 0xFFFFFF, rotate=0)
label6 = M5TextBox(10, 101, "canal 3", lcd.FONT_Default, 0xFFFFFF, rotate=0)
label7 = M5TextBox(150, 25, "canal 4", lcd.FONT_Default, 0xFFFFFF, rotate=0)
label8 = M5TextBox(150, 50, "canal 5", lcd.FONT_Default, 0xFFFFFF, rotate=0)
label9 = M5TextBox(150, 76, "canal 6", lcd.FONT_Default, 0xFFFFFF, rotate=0)
label10 = M5TextBox(150, 101, "canal 7", lcd.FONT_Default, 0xFFFFFF, rotate=0)
label_ch0 = M5TextBox(100, 24, "0", lcd.FONT_Default, 0xFFFFFF, rotate=0)
label_ch1 = M5TextBox(100, 50, "0", lcd.FONT_Default, 0xFFFFFF, rotate=0)
label_ch2 = M5TextBox(100, 76, "0", lcd.FONT_Default, 0xFFFFFF, rotate=0)
label_ch3 = M5TextBox(100, 101, "0", lcd.FONT_Default, 0xFFFFFF, rotate=0)
label_ch4 = M5TextBox(240, 24, "0", lcd.FONT_Default, 0xFFFFFF, rotate=0)
label_ch5 = M5TextBox(240, 50, "0", lcd.FONT_Default, 0xFFFFFF, rotate=0)
label_ch6 = M5TextBox(240, 76, "0", lcd.FONT_Default, 0xFFFFFF, rotate=0)
label_ch7 = M5TextBox(240, 101, "0", lcd.FONT_Default, 0xFFFFFF, rotate=0)
labels = [label_ch0,label_ch1,label_ch2,label_ch3,label_ch4,label_ch5,label_ch6,label_ch7]

#Introducir la IPv4 (en cmd escribir ipconfig) y el puerto (por defecto 8086)
INFLUXDB_URL = 'http://server_IP:server_port/write?db=BBDD_name' # URL de la base de datos de InfluxDB
#Funcion para enviar datos a InfluxDB
def enviar_influxdb(valor, canal): 
 payload = "basedatos,canal={0} intensidad={1}".format(str(canal), valor)
 response = urequests.post(INFLUXDB_URL, data=payload)

def leer_canal_MUX(canal):
 cs_0.value(canal & 0x01) # A0 = primer valor binario de canal
 cs_1.value((canal >> 1) & 0x01) # A1 = segundo valor binario de canal
 cs_2.value((canal >> 2) & 0x01) # A2 = tercer valor binario de canal
 return adc.read() #Devuelve la lectura del CAD

#Codigo que se ejecuta cuando ejecutando=True
def codigo_a_ejecutar():
 global canales_activos
 if canales_activos>0:
 for i in range(canales_activos):
 binario = leer_canal_MUX(i)
 canal = str(i)
 imprimir = labels[i]
 
 imax, imin = 0.0, 0.0
 contador_periodo = 0
 corriente = 0.0
 voltaje = 0.0
 contador_medidas = 0
 lista_medidas=[]
 while contador_medidas<10:
 while contador_periodo<20:
 if binario > 487: #el ACS712 proporciona tension mayor que 1.575V
 voltaje = binario * 3.3 /1023 #regla de 3: 0-1023bin y 0-3.3V
 corriente = (voltaje - 2.5) / sensibilidad 
 if corriente > imax:
 imax = corriente
 if corriente < imin:
 imin = corriente
 else:
 imax, imin = 0, 0
 contador_periodo += 1

 wait_ms(1)
 
 #Al finalizar el ciclo:
 irms = (((imax-imin)/2) / 1.414)-0.11 # Irms = ( (Ipp/2) / raiz(2) )- 0.11
 lista_medidas.append(irms) # Añadir a la lista para al llegar a 10 hacer media
 contador_medidas += 1
 #Calcular media de 10 ciclos, obtener corriente y enviar
 media_irms = (sum([medida for medida in lista_medidas]) / len(lista_medidas))
 
 enviar_influxdb(media_irms, canal) #Enviar valor de corriente eficaz
 
 imprimir.setText(str(round(media_irms,3))) #Mostrar en pantalla
 wait_ms(500) # 0.5 segundos entre cada canal que mide
 wait(1) # 1 segundo cada vez que recorre todos los canales

# Funciones para controlar el M5Stack

def botonApulsado():
 global canales_activos
 if canales_activos < 8:
 canales_activos += 1
 label_ch_act.setText(str(canales_activos))
 
def botonBpulsado():
 global ejecutando
 if ejecutando:
 ejecutando = False
 label_RUN.setText("RUN")
 else:
 ejecutando = True
 label_RUN.setText("STOP")
 
def botonCpulsado():
 global canales_activos
if canales_activos >1:
 canales_activos -= 1
 label_ch_act.setText(str(canales_activos))
while True:
 btnA.wasPressed(botonApulsado)
 btnB.wasPressed(botonBpulsado)
 btnC.wasPressed(botonCpulsado)
 if ejecutando:
 codigo_a_ejecutar()

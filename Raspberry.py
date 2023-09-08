from tkinter import *
import smbus2
import struct
import json
from azure.iot.device import IoTHubDeviceClient
# Cadena de Conexion del Dispositivo (RaspberryPi4B)
CONNECTION_STRING = "HostName=UDC-IotHub.azure-
devices.net;DeviceId=RaspberryPI;SharedAccessKey=3FaWeaGZl6Lcpb+2o6KcOAsb3fZUKx1BeggcEmi2+LE=

estado = False # Variable global para el estado de la comunicación
set_point = 0

def escalar(valor):
  return (valor/1023.0) * 100.0

# Funcion encargada de enviar un mensaje D2C por telemetria.
def iothub_send_message(nivel, set_point):
  print("Enviando mensaje...")
  # Crea un diccionario con los datos a enviar
  data = {"nivel": escalar(nivel), "error": escalar(nivel)-set_point, "set_point": set_point}
  # Convierte el diccionario en una cadena de caracteres JSON y codifica esa cadena en un formato de bytes UTF-8 para poder ser enviada a traves del objeto client.
  message = json.dumps(data).encode("utf-8")
  # Envia los datos de telemetria contenidos en la variable "message" a traves del objeto client para ser transmitidos al servicio de IoT Hub en Azure.
  client.send_message(message)
  print("Mensaje enviado al Hub")
  
def iniciar_comunicacion():
  global estado # Declarar la variable global
  global direccion
  global bus
  global client
  client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)
  bus = smbus2.SMBus(1)
  direccion = 0x20
  print("Comunicación I2C Iniciada")
  estado = True
  start_execution_loop() # Iniciar el bucle de ejecución si el estado es 1

def finalizar_comunicacion():
  global client
  global estado # Declarar la variable global
  print("Comunicación I2C finalizada")
  estado = False
  # cerrar la conexión
  client.shutdown()
  
def message_listener(message):
  global set_point
  message_bytes = message.data
  # Decodificar el contenido del mensaje a una cadena
  message_str = message_bytes.decode("utf-8")
  
  try:
    # Intentar convertir el mensaje a un numero
    set_point = int(message_str)
    print("Mensaje recibido desde la nube (setpoint):", set_point)
    except ValueError:
    print("Mensaje recibido desde la nube no es un número válido:", message_str)
  
def start_execution_loop():
  if estado:
    client.on_message_received = message_listener
    #Enviar SP de Arduino (Esclavo)
    msg = smbus2.i2c_msg.write(direccion, [set_point])
    bus.i2c_rdwr(msg)
    # Leer 2 Int de Arduino (Esclavo)
    msg = smbus2.i2c_msg.read(direccion, 4)
    bus.i2c_rdwr(msg)
    
    # Desempaquetar los datos
    (nivel, error) = struct.unpack('hh', bytes(msg))
    # Imprimir los valores de los datos
    print('Nivel:', nivel)
    print('Error:', error)
    print('SP:', set_point)
    
    # Enviar SetPoint, Error, Nivel por telemetria a Azure
    iothub_send_message(nivel,set_point)
    
    #Espera constante de 1s
    master.after(1000, start_execution_loop)
    
master = Tk()
master.title("Planta de Nivel")

# Configurar el color de fondo de la ventana
master.configure(bg="white")
# Centrar verticalmente y horizontalmente los elementos usando la grilla
frame = Frame(master, bg="white")
frame.pack(expand=True)
# Crear el boton para iniciar la comunicación
communication_button = Button(master, text="Iniciar Comunicación",
command=iniciar_comunicacion)
communication_button.pack()
# Crear el boton para finalizar la comunicación
communication_end_button = Button(master, text="finalizar Comunicación",
command=finalizar_comunicacion)
communication_end_button.pack()
# Personalizar la fuente
custom_font = ("Helvetica", 10)
communication_button.config(font=custom_font)
communication_end_button.config(font=custom_font)
mainloop()

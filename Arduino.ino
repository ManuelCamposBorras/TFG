#include "Wire.h" //Biblioteca para la comunicación I2C.
#include <PID_v1.h> //Biblioteca para implementar un controlador PID.

//dirección I2C del dispositivo esclavo
const byte I2C_SLAVE_ADDR = 0x20;

int data = 0; //Almacena datos recibidos a través de I2C.

double setPoint, input, output; //valores de referencia, entrada, y salida de la planta.
/*Se crea una instancia de la clase PID llamada myPID utilizando las variables input,
output, y setPoint.
13 Los valores 2, 5, y 1 son los valores iniciales de los parámetros del controlador PID (Kp,
Ki, Kd).
14 DIRECT indica que el controlador se ejecutará en modo directo.*/
PID myPID(&input, &output, &setPoint, 2, 5, 1, DIRECT);

/*( se define una estructura de datos llamada "Datos" que tiene dos campos enteros: "nivel"
y "control".
19 Luego, se define una variable global de tipo "Datos" llamada "Arduino" utilizando esta
estructura.*/
struct Datos {
int nivel;
int control;
};
Datos Arduino;

void setup() {
    
//Se inicia la comunicación serial a 115200 baudios para la depuración.
Serial.begin(115200);

//Se inicia la comunicación I2C y se establece la dirección del dispositivo esclavo.
34 Wire.begin(I2C_SLAVE_ADDR);

/*Las siguientes dos líneas de código, se utilizan para configurar dos manejadores de
eventos que se
37 activarán cuando se reciban datos y cuando se soliciten datos, respectivamente.*/
38 Wire.onReceive(receiveEvent);
39 Wire.onRequest(requestEvent);

/*Se establece el valor de referencia inicial de la planta (Hasta que lleguen datos de
Azure)*/
setPoint = 50;
    
//Se configura el controlador PID en modo AUTOMÁTICO.
myPID.SetMode(AUTOMATIC);
}
/*Función que se ejecuta cuando se recibe una solicitud de lectura de datos a través del bus
I2C*/
void receiveEvent(int bytes) {
/*Antes de comenzar el bucle, la variable "data" se establece en cero para
53 asegurarse de que no haya ningún dato previo almacenado en ella.*/
data = 0;
/*se declara una variable llamada "index" de tipo byte, que es un tipo de datos de 8 bits
sin signo.
57 Se utiliza para rastrear la posición actual de la variable "data" a medida que se van
leyendo
58 los datos recibidos (index=2 -> 2 Bytes leídos)*/
byte index = 0;

while (Wire.available()) {
// Declara un puntero llamado "pointer" que apunta a la dirección de memoria de la
variable "data"
byte* pointer = (byte*)&data;

/* Se hace un casting de tipo byte a los datos recibidos en Wire.read, y posteriormente
se introduce en
67 el contenido de la dirección de memoria de (data + index)*/
*(pointer + index) = (byte)Wire.read();

//Se aumenta en una unidad el índice.
index++;
}
    }

void requestEvent() {
//Envía los datos almacenados en la estructura Arduino a través de la comunicación I2C
Wire.write((byte*)&Arduino, sizeof(Arduino));

/* &Arduino: Esto obtiene la dirección de memoria de la estructura Arduino.
sizeof(Arduino): Esto devuelve el tamaño en bytes de la estructura Arduino, lo que garantiza
que se envíen todos los datos contenidos en la estructura.*/
}

void loop() {
//Se lee el valor analógico del nivel y se almacena en input. (0-1023)
input = analogRead(A0);

//Se asigna el valor de input al campo nivel de la estructura Arduino.
Arduino.nivel = int(input);

//Se escala el valor del setPoint para convertirlo a porcentaje (0-1023 -> 0-100)
setPoint = (data * 1023.0) / 100.0;

//Se calcula la salida del controlador PID y se envía a la planta (a través de la Shield)
myPID.Compute();
analogWrite(3, output);
Arduino.control = int(output);
delay(1000);
}

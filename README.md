# Cálculo de consumo en un hogar
En este proyecto se realiza una estimación de los consumos de un hogar utilizando un M5Stack Core (basado en ESP32, con pantalla y tres botones), un medidor de corriente ACS 712 y un multiplexor analógico (ampliable a dos).

Se pueden medir los diferentes consumos de cada interruptor magnetotérmico del cuadro eléctrico de un hogar, introduciendo un medidor de corriente en cada uno. Este transmite el valor al ESP32 por cable a uno de los dos pines ADC (conversor analógico-digital), ya que su salida es un valor de tensión determinado por la corriente que está midiendo (2,5V + I*0,185).

El ESP32 contiene solamente 2 pines ADC, así que se ha utilizado un multiplexor analógico de 8 entradas y una salida DG408DJ. La salida se controla con los otros pines del ESP32. Se puede ampliar utilizando otro multiplexor conectado al otro pin ADC.

Estos datos son enviados a una base de datos temporal InfluxDB para posteriormente elaborar gráficas con Grafana.

Los botones se utilizarán para aumentar o disminuir el número de canales que se miden, y para finalizar o comenzar la medición.

Además se incluye un código básico de optimización de almacenamiento de la base de datos.

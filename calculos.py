import csv
import numpy as np
import matplotlib.pyplot as plt

# Estructura para abrir y leer archivo CSV
with open('OCV(z).csv', mode = 'r' ) as read_file:

    content = csv.reader(read_file)
    cond_first = True
    soc = np.array([])
    ocv = np.array([])

    for row in content:

        if cond_first: title = row; cond_first = False; continue

        soc = np.append(soc, float(row[0]))
        ocv = np.append(ocv, float(row[1]))

    # Se almacenan ambas columnas de datos en un array multidimensional
    data = np.array([soc, ocv])

# Algoritmo implementado para interpolar datos de manera optimizada
def interpolar(z):
    if z in soc:
        return ocv[ np.where( soc == z )[0][0] ]
    else:
        # Implementación de optimización para la búsqueda de x_0 y x_1
        if len(soc) >= 2:
            i = int(len(soc) / 2) - 1
        while(True):
            if soc[i] < z and soc[i + 1] > z or soc[i - 1] < z and soc[i] > z:
                # Se almacenan x_0, x_1, y_0, y_1 en orden correcto
                if soc[i] < z:
                    x_0 = soc[i]
                    y_0 = ocv[i]
                    x_1 = soc[i + 1]
                    y_1 = ocv[i + 1]
                else:
                    x_0 = soc[i - 1]
                    y_0 = ocv[i - 1]
                    x_1 = soc[i]
                    y_1 = ocv[i]
                break
            elif soc[i] > z and soc[i - 1] > z:
                i = int(i / 2)
                continue
            else:
                if i * 1.5 < len( soc ):
                    if soc[ int(i * 1.5) ] < z and int(i * 1.05) != i:
                        i = int (i * 1.5)
                    elif soc[ int( i * 1.25 ) ] < z and int(i * 1.05) != i:
                        i = int (i * 1.25)
                    elif soc[ int( i * 1.05 ) ] < z and int(i * 1.05) != i:
                        i = int (i * 1.05)
                    else:
                        i += 1
                else:
                    i += 1
                continue
        # Retornar valor interpolado
        return ( y_0 + (z - x_0) * (y_1 - y_0) / (x_1 - x_0) )

# Se definen las celdas como objetos debido a la versatilidad del paradigma orientado a objetos para
# manipular múltiples elementos con una misma funcionalidad, como lo podrían ser múltiples celdas
class Celdas:
    
    # Inicializar varibles
    cap_nominal = 0
    voltaje = 0
    corriente = 0
    ocv_de_z = 0
    z_soc = 0
    d_k = 0
    resistor = 0
    nc = 0
    nd = 0
    k_total = 0
    k = 0

    # Variables de tipo array
    voltajes = np.array([])
    tiempos = np.array([])
    socs = np.array([])
    corrientes = np.array([])
    capacidades = np.array([])
    puntos_soc = np.array([])

    # Constructor define datos constantes
    def __init__(self):
        self.cap_nominal = 3250
        self.resistor = 0.0001
        self.z_soc = 0.2
        self.d_k = 1
        self.nc = 0.99
        self.nd = 1
        self.k = 1
        self.puntos_soc = np.append(self.puntos_soc, self.z_soc)

    # Método para calcular voltaje en carga o descarga, fact -1 representa corriente negativa
    def volt(self, fact):
        return(self.ocv_de_z - self.resistor * self.corriente * fact)

    # Método corr permite calcular el valor actual de la corriente
    def corr(self, limite):
        a = self.voltaje - self.ocv_de_z
        b = a / self.resistor
        b = float('%.4f'%(b))
        return(b)

    # Método de carga utilizado para iniciar cada proceso con límite de ya sea en CC o CV
    def cargar(self, limite, const, tasa_c):
        fact = -1
        # Caso CC
        if const == "CC":
            self.corriente = self.cap_nominal * tasa_c
            while (self.voltaje < limite):
                self.z_soc = soc[int(self.k)]
                if interpolar(self.z_soc) != self.ocv_de_z:
                    self.ocv_de_z = interpolar(self.z_soc)
                self.voltaje = self.volt(fact)

                # Almacenar los datos de cada iteración
                self.voltajes = np.append(self.voltajes, self.voltaje)
                self.tiempos = np.append(self.tiempos, self.k_total  * 0.5/60)
                self.corrientes = np.append(self.corrientes, self.corriente)
                self.socs = np.append(self.socs, self.z_soc)

                self.k += self.d_k
                self.k_total += 1
            self.k -= self.d_k
        # En caso de ser CV
        else:
            while (self.corriente > limite):
                corriente = self.corr(limite)
                self.z_soc = soc[int(self.k)]
                if interpolar(self.z_soc) != self.ocv_de_z:
                    self.ocv_de_z = interpolar(self.z_soc)
                self.k += self.d_k
                self.k_total += 1
                
                # Almacenar los datos de cada iteración
                self.voltajes = np.append(self.voltajes, self.voltaje)
                self.tiempos = np.append(self.tiempos, self.k_total * 0.5/60 )
                self.corrientes = np.append(self.corrientes, self.corriente)
                self.socs = np.append(self.socs, self.z_soc)

                if corriente < limite: break
                else: self.corriente = corriente
            self.k -= self.d_k

    # Método de descarga utilizado para iniciar cada proceso con límite en CC, no se requirió implementar para CV
    def descargar(self, limite, const, tasa_c):
        fact = 1
        if const == "CC":
            self.corriente = self.cap_nominal * tasa_c
            # Se detiene con v(t) == 3.2 porque ocv no llega más abajo
            while (True):
                self.z_soc = soc[int(self.k)]
                if interpolar(self.z_soc) != self.ocv_de_z:
                    self.ocv_de_z = interpolar(self.z_soc)
                self.voltaje = self.volt(fact)
                
                # Almacenar los datos de cada iteración
                self.voltajes = np.append(self.voltajes, self.voltaje)
                self.tiempos = np.append(self.tiempos, self.k_total * 0.5/60 )
                self.corrientes = np.append(self.corrientes, self.corriente)
                self.socs = np.append(self.socs, self.z_soc)

                self.k -= self.d_k
                self.k_total += 1
                if self.voltaje <= limite: break
            self.k = int(self.k + self.d_k)

    # Método updt_points permite solicitar el almacinamiento de las capacidades y el delta de capacidad en un momento dado
    def updt_points(self):
        self.capacidades = np.append(self.capacidades, (self.cap_nominal * (self.z_soc - self.puntos_soc[len(self.puntos_soc) - 2])))
        self.puntos_soc = np.append(self.puntos_soc, self.z_soc)

    # Método get retorna un array multidimensional con los valores de voltaje, tiempo, corriente, soc para realizar cálculos o gráficas
    def get_resultados(self):
        return np.array([self.voltajes, self.tiempos, self.corrientes, self.socs])

    # Método get retorna array con los soc previamente solicitados para almacenamiento
    def get_puntos(self):
        return self.puntos_soc

    # Método get retorna array con los delta capacidad previamente solicitados para almacenamiento
    def get_caps(self):
        return self.capacidades

# Instrucciones para llamar el proceso de carga - descarga indicado por el enunciado
celda1 = Celdas()
celda1.cargar(4.2, "CC", 0.5)
celda1.cargar(500, "CV", 0)
celda1.updt_points()
celda1.descargar(3.2, "CC", 1)
celda1.updt_points()

# Menú simple para una mejor visualización del funcionamiento
while(True):
    print("\n<<--------------- Menú bonito --------------->>")
    x = input("0. Finalizar programa\n1. Interpolar dato ingresado\n2. Gráfica v/t\n3. Gráfica i/t\n4. Gráfica z/t\n5. Valores durante el proceso\n>>-------------------------------------------<<\n\nIngresar un número:\n>> ")
    
    if x == "0":
        print("Programa finalizado")
        break
    elif x == "1":
        # Manejo de excepciones para prevenir errores por datos no casteables a float
        while(True):
            try:
                num = float( input("Ingresar valor de z entre 0.2 y 1:\n>> ") )
                num =  float( '%.4f'%(num) )
                if num >= 0.2 and num <= 1:
                    print(interpolar(num))
                    break
                else:
                    print("Por favor ingresar un número dentro del rango especificado")
                continue
            except ValueError:
                print("Por favor sólo ingresar números")
    elif x=="2":
        # Grafica V/t
        # Retorna voltajes, tiempos, corrientes, socs
        datos = celda1.get_resultados()
        x = datos[1]
        y = datos[0]
        plt.ylabel('Voltaje (V)')
        plt.xlabel('Tiempo (min)')
        plt.step(x, y)
        plt.grid(axis='x', color='0.95')
        plt.title('Gráfica de Voltaje en función del tiempo')
        plt.show()
        continue
    elif x=="3":
        # Grafica i/t
        # Retorna voltajes, tiempos, corrientes, socs
        datos = celda1.get_resultados()
        x = datos[1]
        y = datos[2]
        plt.ylabel('Corriente (mA)')
        plt.xlabel('Tiempo (min)')
        plt.step(x, y)
        plt.grid(axis='x', color='0.95')
        plt.title('Gráfica de Corriente en función del tiempo')
        plt.show()
        continue
    elif x=="4":
        # Grafica z/t
        # Retorna voltajes, tiempos, corrientes, socs
        datos = celda1.get_resultados()
        x = datos[1]
        y = datos[3]
        plt.ylabel('SOC')
        plt.xlabel('Tiempo (min)')
        plt.step(x, y)
        plt.grid(axis='x', color='0.95')
        plt.title('Gráfica del SOC en función al tiempo')
        plt.show()
        continue
    elif x == "5":
        # Utiliza los gets del objeto para obtener la información
        p_socs = celda1.get_puntos()
        caps = celda1.get_caps()
        print("SOC inicial: %.4f \nSOC fin de carga: %.4f \nSOC fin descarga: %.4f" % (p_socs[0], p_socs[1], p_socs[2]))
        print("Capacidad cargada: %.2f \nCapacidad descargada: %.2f" % (caps[0], caps[1]))

import csv
import numpy as np

title = np.array(['','',''])

hour = np.array([])
norm = np.array([])
atip = np.array([])

with open( "casa.csv", mode = "r" ) as file:
    
    row_amount = 0
    data = csv.reader(file)

    for row in data:
        if row_amount == 0:
            title = row
            row_amount += 1
        else:
            hour = np.append(hour, float(row[0]))
            norm = np.append(norm, float(row[1]))
            atip = np.append(atip, float(row[2]))

# se genera un array multidimensional para iterar eficientemente los datos de cada usuario
users_data = np.array([norm,atip])

# mes de 30 días
days = 30

# función que agrega el IVA al costo final
# 13% > 280kWh/mes
def func_iva(cost,usage):
    if usage < 280:
        return cost
    else:
        cost *= 1.13
        return cost

# residencial ICE (excedente luego de 200kWh se cobra incrementado)

# consumo <= 200 kWh costo 82,3
# consumo > 200 kWh costo 147,75

def residencial_ice():

    # define costos en un array multidimensional [[consumo_usuario1, costo_usuario1],
    #                                             [consumo_usuario2, costo_usuario2]]
    costs = np.array([[0.0, 0.0]])

    # se almacena en la variable user el array que contiene la potencia usada cada hora
    for user in users_data:
        values = np.array([])
        total_usage = 0.0
        # el ciclo suma todos los valores de consumo en el día para el user actual
        for i in range(0, user.size):
            total_usage += user[i]
        # el uso de potencia diario se multiplica por 30 asumiendo un mes de 30 días
        total_usage *= days
        # lógica comparativa para ajustarse a la tarifa
        if total_usage <= 200:
            total_cost = total_usage * 82.3
        else:
            total_cost = 200 * 82.3
            total_cost += (total_usage - 200) * 147.75
        
        # almacenar consumo y costo en un array dentro del array de usuarios
        costs = np.concatenate((costs, np.array([[total_cost, total_usage]])), axis = 0)       

    # se elimina el subarray original pues ya no es necesario
    costs = np.delete(costs, 0, axis = 0)
    
    return costs

# residencial CNFL

# consumo <= 30 kWh cargo fijo 2279,1
# 30 < consumo >= 200 cobra 75,97/kWh
# 200 < consumo >= 300 cobra 116.58/kWh
# consumo > 300 cobra 120,52/kWh aplica el de 200 a 300 y el excedente tiene la nueva tarifa

def residencial_cnfl():

    costs = np.array([[0.0, 0.0]])

    for user in users_data:
        total_usage = 0.0

        # suma los kWh consumidos por el usuario actual y los pasa a consumo mensual
        for i in range(0, user.size):
            total_usage += user[i]
        # asumiendo tarifa cobro por mes
        total_usage *= days
        total_cost = 0
        if total_usage <= 30:
            total_cost = 2279.1
        elif total_usage > 30 and total_usage <= 200:
            total_cost = total_usage * 75.97
        elif total_usage > 200 and total_usage <= 300:
            total_cost = total_usage * 116.58
        # primero se aplica el costo de 300 kWh bajo el costo de 200 a 300 y posteriormente el excedente se aplica a la tarifa final
        elif total_usage > 300:
            total_cost = 300 * 116.58
            total_cost += (total_usage - 300) * 120.52
        
        # almacenar consumo y costo en un array dentro del array de usuarios
        costs = np.concatenate((costs, np.array([[total_cost, total_usage]])), axis = 0)       

    # se elimina el subarray original pues ya no es necesario
    costs = np.delete(costs, 0, axis = 0)

    return costs

# residencial horaria CNFL

# punta 10:00 a 12:30 - 17:30 a 20:00
# consumo <= 500 175,86/kW
# valle 6:01 a 10:00 - 12:30 a 17:30
# <= 500 72,08/kW
# nocturno 20:00 a 6:00
# <= 500 30,17/kW

# punta 10:00 a 12:30 - 17:30 a 20:00
# > 501 (500) 217.45/kW
# valle 6:01 a 10:00 - 12:30 a 17:30
# > 501 87.77/kW
# nocturno 20:00 a 6:00
# > 501 40.62/kW

def horaria_cnfl():

    costs = np.array([[0.0, 0.0]])

    for user in users_data:
        values = np.array([])
        total_usage = 0.0
        total_cost = 0.0
        for i in range(0, user.size):
            total_usage += user[i]
        # de 6:01 a 10
        usage = 0.0
        # sumar los kWh consumidos en el periodo específico
        for i in range(6, 9):
            usage += user[i]
        # aplicar el costo correcto según el periodo y consumo
        if usage <= 500:
            total_cost += usage * 72.08
        else:
            total_cost += usage * 87.77
        

        # de 10 a 12:30
        usage = 0.0
        for i in range(10, 12):
            usage += user[i]
            # agregar un caso especial por los 30 min extra, se resta la mitad de las 12
            if i == 12:
                usage -= user[i]/2
        if usage <= 500:
            total_cost += usage * 175.86
        else:
            total_cost += usage * 217.45
        

        # de 12:30 a 17:30
        usage = 0.0
        for i in range(12, 17):
            usage += user[i]
            # se resta la mitad de las 12 o las 17 debido a los 30 min extra
            if i == 12 or i == 17:
                usage -= user[i]/2
        if usage <= 500:
            total_cost += usage * 72.08
        else:
            total_cost += usage * 87.77
        
            
        # de 17:30 a 20
        usage = 0.0
        for i in range(17, 20):
            usage += user[i]
            if i == 17:
                usage -= user[i]/2
        if usage <= 500:
            total_cost += usage * 175.86
        else:
            total_cost += usage * 217.45
        

        # de 20 a 6
        usage = 0.0
        for i in range(20, 6, -1):
            usage += user[i]
        if usage <= 500:
            total_cost += usage * 30.17
        else:
            total_cost += usage * 40.62
        
        
        # calcular el consumo mensual
        total_usage *= days
        total_cost *= days
    
        # almacenar consumo y costo en un array dentro del array de usuarios
        costs = np.concatenate((costs, np.array([[total_cost, total_usage]])), axis = 0)       
        
    # se elimina el subarray original pues ya no es necesario
    costs = np.delete(costs, 0, axis = 0)
    
    # retorna el array con los gastos de cada usuario
    return costs
    
def horaria_cnfl_BEV():
    
    user_values = horaria_cnfl()
    print("Tarifa residencial horaria del CNFL con BEV (I.V.I):")

    # costo antes del BEV
    cost_pre_BEV = user_values[0][0]

    # consumo previo al BEV
    usage_pre_BEV = user_values[0][1]
    daily_usage = usage_pre_BEV / days
    
    # de 20 a 6
    # al ser la hora mas barata, se distribuyen a diario las 48 horas mensuales necesarias para cargar al BEV
    # en este horario, y se multiplica por su consumo por hora en kW
    BEV_consumo = ((240*24*12)/(7*1000))* days
    usage_plus_BEV = usage_pre_BEV + BEV_consumo
    uso_per = 0.0
    # de 20 a 6
    usage = BEV_consumo / days
    cost_plus_BEV = 0.0
    usage_pre_BEV -= usage - BEV_consumo / days
    
    for i in range(20, 6, -1):
        uso_per += users_data[0][i]
        
    usage += uso_per
    if usage <= 500:
        cost_pre_BEV -= uso_per * 30.17
        cost_plus_BEV += usage * 30.17
    else:
        cost_pre_BEV -= uso_per * 40.62
        cost_plus_BEV += usage * 40.62
       
    # mensuales
    cost_plus_BEV *= days
    cost_plus_BEV += cost_pre_BEV
    
    

    # llamar función encargada de aplicar el IVA
    cost_plus_BEV = func_iva(cost_plus_BEV, usage_plus_BEV)
    cost_pre_BEV = func_iva(cost_pre_BEV, usage_pre_BEV)

    # imprimir datos en comparación
    print("Costo con gasolina: %.2f colones || Costo con BEV: %.2f colones" % (cost_pre_BEV+42000, cost_plus_BEV))
    print("El ahorro utilizando el BEV es de: %.2f colones " % (cost_pre_BEV+42000-cost_plus_BEV))
    print("Consumo previo: %.2f kWh           || Consumo con BEV: %.2f kWh" % (usage_pre_BEV, usage_plus_BEV))

def residencial_cnfl_BEV():
    user_values = residencial_cnfl()
    print()
    print("Tarifa residencial del CNFL con BEV (I.V.I):")
    
    # consumo mensual previo al BEV
    usage_pre_BEV = user_values[0][1]
    

    # costo mensual previo al BEV
    cost_pre_BEV = user_values[0][0]
    costo_cg = func_iva(cost_pre_BEV,usage_pre_BEV) + 42000
    #se divide el consumo semanal (240 V * 24 A * 12 horas) entre 7 dias y se transforma a kW
    BEV_consumo = ((240*24*12)/(7*1000))
    total_usage = usage_pre_BEV + BEV_consumo * days
    
    # asumiendo tarifa cobro por mes
    total_cost = 0
    if total_usage <= 30:
        total_cost = 2279.1
    elif total_usage > 30 and total_usage <= 200:
        total_cost = total_usage * 75.97
    elif total_usage > 200 and total_usage <= 300:
        total_cost = total_usage * 116.58
    # primero se aplica el costo de 300 kWh bajo el costo de 200 a 300 y posteriormente el excedente se aplica a la tarifa final
    elif total_usage > 300:
        total_cost = 300 * 116.58
        total_cost += (total_usage - 300) * 120.52

    total_cost = func_iva(total_cost, total_usage)
    cost_pre_BEV = func_iva(cost_pre_BEV, usage_pre_BEV)

    # imprimir datos en comparación
    print("Costo con gasolina: %.2f colones || Costo con BEV: %.2f colones" % (cost_pre_BEV+42000, total_cost))
    print("El ahorro utilizando el BEV es de: %.2f colones " % (cost_pre_BEV+42000-total_cost))
    print("Consumo previo: %.2f kWh            || Consumo con BEV: %.2f kWh \n" % (usage_pre_BEV, total_usage))
    
# calculos para el BEV
residencial_cnfl_BEV()
horaria_cnfl_BEV()

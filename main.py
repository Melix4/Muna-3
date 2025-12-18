import constants
import math
import pandas as pd
import openpyxl


# Функция рассчета коэффициента расхода топлива
def fuel_consumption():
    return constants.Fuel_Mass / constants.t

# Функция, рассчитывающая массу ракеты в заданный момент времени t
def current_rocket_mass(t):
    return constants.Rocket_Mass - fuel_consumption() * t


# Функция рассчета гравитационного воздействия на ракету
def gravity_force(d):
    if d == 0:
        return constants.g0 * constants.Rocket_Mass
    R = constants.Kerbin_Radius
    return constants.Rocket_Mass * constants.g0 * (R ** 2 / (R + d) ** 2)


# Функция, возвращающая реактивную тягу ракеты
def reactive_thrust():
    # Т.к. Isp = Ve / g0, то
    return constants.Isp * constants.g0 * fuel_consumption()


# Функция, рассчитывающая характеристическую скорость ракеты по формуле Циолковского
def deltaV(t):
    return constants.Isp * constants.g0 * math.log(constants.Rocket_Mass / current_rocket_mass(t))


# Функция рассчета ускорения ракеты в заданный момент времени t
def acceleration(heightArray, t):
    height = heightArray[-1]
    return (reactive_thrust() - gravity_force(height)) / current_rocket_mass(t)


# Функция, проводящая моделирование процесса полета и запись значений в списки
def calc():
    timeArray = [i for i in range(constants.t + 1)] # Список временных значений
    massArray = [current_rocket_mass(time) for time in timeArray] # Список масс ракеты для каждого времени
    speedArray = [deltaV(time) for time in timeArray] # Список значений скорости ракеты для каждого времени

    # Заполнение значениями списка высот ракеты относительно Кербина для каждого времени
    heightArray = [0]
    accelerationArray = [acceleration(heightArray, 0)]
    for time in timeArray[1:]:
        v = speedArray[time]
        a = acceleration(heightArray, time)
        currentHeight = heightArray[-1] + v + 0.5 * a
        heightArray.append(currentHeight)
        accelerationArray.append(a)

    gravityForceArray = [gravity_force(d) for d in heightArray] # Список значений силы гравитации для каждого времени
    # Возврат списков значений
    return massArray, accelerationArray, heightArray, speedArray, gravityForceArray, timeArray

# Функция записи данных в Excel-файл
def write_to_xls():
    # Получение списков данных и создание словаря dataDict, содержащего заголовки
    massArray, accelerationArray, heightArray, speedArray, gravityForceArray, timeArray = calc()
    dataDict = {
        'Время': timeArray,
        'Масса': massArray,
        'Ускорение': accelerationArray,
        'Скорость': speedArray,
        'Высота': heightArray
    }
    # создание объекта DataFrame модуля Pandas
    df = pd.DataFrame(dataDict)
    df.to_excel('data.xlsx', sheet_name='Data', index=False)

if __name__ == '__main__':
    calc()
    #write_to_xls()

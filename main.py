import constants
import math
import pandas as pd
import openpyxl


# Возвращает номер ступени в зависимости от времени
def stage(t):
    if 0 <= t <= 25:
        return 1
    return 2


# Функция рассчета коэффициента расхода топлива
def fuel_consumption(t):
    s = stage(t)
    if s == 1:
        return constants.Mf1 / constants.time_of_stages[0]
    return constants.Mf2 / constants.time_of_stages[1]


# Функция, рассчитывающая массу ракеты в заданный момент времени t
def current_rocket_mass(t):
    s = stage(t)
    if s == 1:
        return constants.Rocket_Mass - fuel_consumption(t) * t
    return constants.Rocket_Mass - constants.M1 - fuel_consumption(t) * (t - constants.time_of_stages[0])


# Функция рассчета гравитационного воздействия на ракету
def gravity_force(d):
    R = constants.Kerbin_Radius
    return constants.Rocket_Mass * constants.g0 * (R ** 2 / (R + d) ** 2)


# Функция, возвращающая реактивную тягу ракеты
def reactive_thrust(t):
    # Т.к. Isp = Ve / g0, то
    s = stage(t)
    return constants.Isp[s - 1] * constants.g0 * fuel_consumption(t)


# Функция, рассчитывающая характеристическую скорость ракеты по формуле Циолковского
def deltaV(t):
    s = stage(t)
    return constants.Isp[s - 1] * constants.g0 * math.log(constants.Rocket_Mass / current_rocket_mass(t))


# Функция рассчета ускорения ракеты в заданный момент времени t
def acceleration(heightArray, t):
    height = heightArray[-1]
    return (reactive_thrust(t) - gravity_force(height)) / current_rocket_mass(t)


# Функция, проводящая моделирование процесса полета и запись значений в списки
def calc():
    timeArray = [i for i in range(constants.t + 1)]  # Список временных значений
    massArray = [current_rocket_mass(time) for time in timeArray]  # Список масс ракеты для каждого времени
    # speedArray = [deltaV(time) for time in timeArray]  # Список значений скорости ракеты для каждого времени
    speedArray = [0]
    # Заполнение значениями списка высот ракеты относительно Кербина для каждого времени
    heightArray = [0]

    accelerationArray = [acceleration(heightArray, 0)]
    for time in timeArray[1:]:
        v = speedArray[-1]
        a = acceleration(heightArray, time)
        v += a
        currentHeight = heightArray[-1] + v
        heightArray.append(currentHeight)
        accelerationArray.append(a)
        speedArray.append(v)

    gravityForceArray = [gravity_force(d) for d in heightArray]  # Список значений силы гравитации для каждого времени
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


# Забираем данные, полученные автопилотом
def data_from_ksp():
    # чтение данных из файла
    with open('ascent_data.csv', 'r', encoding='utf-8') as f:
        data = f.readlines()
    massArray = [0] * (constants.t + 1)
    altitudeArray = [0] * (constants.t + 1)
    data = data[1:]
    for x in data:
        # разбиваем каждую строку по запятой, выбираем необходимые элементы
        x = x.split(',')
        time = int(float(x[0]))
        mass = float(x[1])
        altitude = float(x[2])

        # записываем выбранные данные в списки
        if time <= constants.t:
            massArray[time] = mass
            altitudeArray[time] = altitude
    massArray[-1] = massArray[-2]
    altitudeArray[-1] = altitudeArray[-2]
    return massArray, altitudeArray


if __name__ == '__main__':
    calc()

import constants
import math
import pandas as pd
import openpyxl


def vector_length(vec):
    return (vec[0] ** 2 + vec[1] ** 2) ** 0.5


# Возвращает номер ступени в зависимости от времени
def stage(t):
    if 0 <= t <= 25:
        return 1
    return 2


def angle(h):
    h = h - constants.Kerbin_Radius
    if h <= 20000:
        return 90
    elif h >= 25000:
        return 45
    return 90 - ((h - 20000) / (25000 - 20000) * 45)


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
def gravity_force(d, m0):
    d += constants.Kerbin_Radius
    return constants.Kerbin_Mass * m0 * constants.Gravity_Parametr / (d ** 2)


# Функция, возвращающая реактивную тягу ракеты
def reactive_thrust(t):
    # Т.к. Isp = Ve / g0, то
    s = stage(t)
    return constants.Isp[s - 1] * constants.g0 * fuel_consumption(t)


# сила сопротивления среды (воздуха) в Ньютонах
def drag_force(velocity, Ro):
    # return (constants.Cf * Ro * velocity ** 2 * constants.S) / 2
    return 0


# атмосферное давление от высоты
def pressure(h):
    return constants.Pressure * math.exp(-(constants.Molar_Mass * constants.g0 * h) / (constants.R * constants.T))


# ускорение, м/с^2
def acceleration(ForceOfThrust, ForceOfGravity, ForceOfAirResistance, Angle, mass):
    return ((abs(ForceOfThrust * math.cos(math.radians(Angle)) + ForceOfGravity[0] + ForceOfAirResistance[0])) / mass,
            abs((ForceOfThrust * math.sin(math.radians(Angle)) + ForceOfGravity[1] + ForceOfAirResistance[1]) / mass))


def zero_state():
    return State(current_rocket_mass(0), 0, constants.Kerbin_Radius, 0, 0, 0, 0, angle(0))


class State:
    def __init__(self, m, x_pos, y_pos, vx, vy, ax, ay, angle):
        self.m = m
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.vx = vx
        self.vy = vy
        self.ax = ax
        self.ay = ay
        self.angle = angle

    def get_next_state(self, time):
        dt = 0.01
        m0 = self.m
        h = self.y_pos
        Ro = pressure(h)
        v = vector_length((self.vx, self.vy))

        if v != 0:
            vx_direction = self.vx / v
            vy_direction = self.vy / v
        else:
            vx_direction = math.cos(math.radians(self.angle))
            vy_direction = math.sin(math.radians(self.angle))

        F_thrust = reactive_thrust(time) * dt
        F_gravity = gravity_force(h, m0)
        F_drag = drag_force(v, Ro)
        phi = math.radians(angle(h))

        F_thrust_x = F_thrust * math.cos(phi)
        F_thrust_y = F_thrust * math.sin(phi)

        F_drag_x = -F_drag * vx_direction
        F_drag_y = -F_drag * vy_direction

        F_gravity_x = 0
        F_gravity_y = -F_gravity

        F_total_x = (F_thrust_x + F_drag_x + F_gravity_x) * dt
        F_total_y = (F_thrust_y + F_drag_y + F_gravity_y) * dt

        # ускорения(второй закон Ньютона)
        ax = F_total_x / m0
        ay = F_total_y / m0

        self.vx += ax
        self.vy += ay
        state_arr = [current_rocket_mass(time), self.x_pos + self.vx, self.y_pos + self.vy,
                     self.vx, self.vy, ax, ay, angle(self.y_pos)]
        return State(*state_arr)

    def get_array_state(self):
        return [self.m, self.x_pos, self.y_pos, self.vx, self.vy, self.ax, self.ay, self.angle]


# Функция, проводящая моделирование процесса полета и запись значений в списки
def calc():
    time = 0
    dt = 0.01
    state = zero_state()
    timeArray, massArray, velocityArray, heightArray, thrustArray, gravityArray, dragArray, RoArray = (
        [], [], [], [], [], [], [], [])
    while time <= constants.t:
        state = State(*state.get_array_state())
        state = state.get_next_state(time)
        print(*state.get_array_state())
        timeArray.append(time)
        massArray.append(state.get_array_state()[0])
        velocityArray.append(state.get_array_state()[4])
        heightArray.append(state.get_array_state()[2] - constants.Kerbin_Radius)
        time += dt
    thrustArray = [reactive_thrust(t) for t in timeArray]
    gravityArray = [gravity_force(heightArray[t], massArray[t]) for t in range(len(timeArray))]
    RoArray = [pressure(h) for h in heightArray]
    dragArray = [drag_force(velocityArray[t], RoArray[t]) for t in range(len(velocityArray))]
    return timeArray, massArray, velocityArray, heightArray, thrustArray, gravityArray, dragArray, RoArray


# Функция записи данных в Excel-файл
def write_to_xls():
    # Получение списков данных и создание словаря dataDict, содержащего заголовки
    timeArray, massArray, velocityArray, heightArray, thrustArray, gravityArray, dragArray, RoArray = calc()
    dataDict = {
        'Время': timeArray,
        'Масса': massArray,
        'Скорость': velocityArray,
        'Высота': heightArray,
        'Тяга': thrustArray,
        'Сопротивление среды': dragArray,
        'Плотность среды': RoArray,
        'Гравитация': gravityArray
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
        time = int(float(x[0]) * 10)
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

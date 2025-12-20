import matplotlib.pyplot as plt
import main
import os

if not os.path.isdir("Graphics"):  # папка для хранения графиков
    os.mkdir("Graphics")

# Построение графиков функции
# Получение всех необходимых массивов
timeArray, massArray, velocityArray, heightArray, thrustArray, gravityArray, dragArray, RoArray = main.calc()

#massArrayKSP, altitudeArrayKSP = main.data_from_ksp()

# График №1: Зависимость массы ракеты от времени
massGraph = plt.figure("Масса", figsize=(10, 5), dpi=150)
plt.plot(timeArray, massArray, 'g')
plt.title("Масса от времени")
plt.xlabel('Время, с')
plt.ylabel('Масса, кг')
massGraph.savefig("Graphics/massGraph.png")

# График №2: Зависимость высоты ракеты от времени
heightGraph = plt.figure("Высота", figsize=(10, 5), dpi=150)
plt.plot(timeArray, heightArray, 'r')
plt.title("Высота от времени")
plt.xlabel('Время, с')
plt.ylabel('Высота, м')
heightGraph.savefig("Graphics/heightGraph.png")

# График №3: Зависимость скорости ракеты от времени
speedGraph = plt.figure("Скорость", figsize=(10, 5), dpi=150)
plt.plot(timeArray, velocityArray, 'b')
plt.title("Скорость от времени")
plt.xlabel('Время, с')
plt.ylabel('Скорость, м/с')
speedGraph.savefig("Graphics/speedGraph.png")

# График №4: Зависимость силы гравитации от высоты
gravityForceGraph = plt.figure("Гравитация", figsize=(10, 5), dpi=150)
plt.plot(heightArray, gravityArray, 'g')
plt.title("Сила гравитации от высоты")
plt.xlabel('Высота, м')
plt.ylabel('Сила гравитационного притяжения, Н')
gravityForceGraph.savefig("Graphics/gravityForceGraph.png")

# График №5: Зависимость силы сопротивления от времени
dragGraph = plt.figure("Сопротивление", figsize=(10, 5), dpi=150)
plt.plot(timeArray, dragArray, 'r')
plt.title("Сила сопротивления среды от времени")
plt.xlabel('Время, с')
plt.ylabel('Сила сопротивления воздуха, Н')
dragGraph.savefig("Graphics/dragGraph.png")

# График №6: Зависимость плотности от высоты
RoGraph = plt.figure("Плотность", figsize=(10, 5), dpi=150)
plt.plot(heightArray, RoArray, 'b')
plt.title("Плотность среды от высоты")
plt.xlabel('Высота, м')
plt.ylabel('Плотность среды, Па')
RoGraph.savefig("Graphics/RoGraph.png")

# График №7: Зависимость силы тяги от времени
thrustGraph = plt.figure("Тяга", figsize=(10, 5), dpi=150)
plt.plot(timeArray, thrustArray, 'g')
plt.title("Тяга от времени")
plt.xlabel('Время, с')
plt.ylabel('Сила тяги среды, H')
thrustGraph.savefig("Graphics/thrustGraph.png")

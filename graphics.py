import matplotlib.pyplot as plt
import main
import os

if not os.path.isdir("Graphics"):  # папка для хранения графиков
    os.mkdir("Graphics")

# Построение графиков функции
# Получение всех необходимых массивов
massArray, accelerationArray, heightArray, speedArray, gravityForceArray, time = main.calc()

massArrayKSP, altitudeArrayKSP = main.data_from_ksp()

# График №1: Зависимость массы ракеты от времени
massGraph = plt.figure("Масса", figsize=(10, 5), dpi=150)
plt.plot(time, massArray, 'g')
plt.title("Масса от времени")
plt.xlabel('Время, с')
plt.ylabel('Масса, кг')
massGraph.savefig("Graphics/massGraph.png")

# График №2: Зависимость ускорения ракеты от времени
accelerationGraph = plt.figure("Ускорение", figsize=(10, 5), dpi=150)
plt.plot(time, accelerationArray, 'Orange')
plt.title("Ускорение от времени")
plt.xlabel('Время, с')
plt.ylabel('Ускорение, м/с^2')
accelerationGraph.savefig("Graphics/accelerationGraph.png")

# График №3: Зависимость высоты ракеты от времени
heightGraph = plt.figure("Высота", figsize=(10, 5), dpi=150)
plt.plot(time, heightArray, 'r')
plt.title("Высота от времени")
plt.xlabel('Время, с')
plt.ylabel('Высота, м')
heightGraph.savefig("Graphics/heightGraph.png")

# График №4: Зависимость скорости ракеты от времени
speedGraph = plt.figure("Скорость", figsize=(10, 5), dpi=150)
plt.plot(time, speedArray, 'r')
plt.title("Скорость от времени")
plt.xlabel('Время, с')
plt.ylabel('Скорость, м/с')
speedGraph.savefig("Graphics/speedGraph.png")

# График №5: Зависимость силы гравитации от высоты
gravityForceGraph = plt.figure("Гравитация", figsize=(10, 5), dpi=150)
plt.plot(heightArray[2:], gravityForceArray[2:], 'r')
plt.title("Сила гравитации от высоты")
plt.xlabel('Высота, м')
plt.ylabel('Сила гравитационного притяжения, Н')
gravityForceGraph.savefig("Graphics/gravityForceGraph.png")

# Сравнение графиков масс
compMass = plt.figure("Сравнение масс", figsize=(10, 5), dpi=150)
plt.plot(time, massArray, label='Данные с физ.модели')
plt.plot(time, massArrayKSP, label='Данные c ksp')
plt.xlabel('Время, с')
plt.ylabel('Масса, кг')
plt.title('Сравнение масс')
compMass.savefig("Graphics/comparisonMass.png")

# Сравнение графиков высот
compHeight = plt.figure("Сравнение высот", figsize=(10, 5), dpi=150)
plt.plot(time, heightArray, label='Данные с физ.модели')
plt.plot(time, altitudeArrayKSP, label='Данные с ksp')
plt.xlabel('Время, с')
plt.ylabel('Высота, м')
plt.title('Сравнение высот')
compHeight.savefig("Graphics/comparisonHeight.png")
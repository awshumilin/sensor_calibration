# Import libraries

import PySimpleGUI as sg
from functions import make_plot, draw_figure, get_coefficients, get_accuracy
import seaborn as sns
import numpy as np
from datetime import datetime

sns.set(rc={'figure.figsize': (7, 7)})

# Setting theme and layouts
#_____________________________________
sg.theme('DarkGrey13')

layout0 = [[sg.Text('Выберите режим')],
           [sg.Combo(['Калибровка', 'Проверка погрешности'],
                     size=(30, 5), key='mode', enable_events=True)],
           [sg.Text('Обнуляемый?')],
           [sg.Combo(['Нет', 'Да'],
                     size=(30, 5), key='zero', enable_events=True)],
           [sg.Text('Обратный прогон')],
           [sg.Combo(['Нет', 'Да'],
                     size=(30, 5), key='back', enable_events=True)],
           [sg.Text('Выберите модель датчика')],
           [sg.Combo(['ACE 1220', 'ACE 1215'],
                     size=(30, 5), key='typesensor', enable_events=True)],
           [sg.Text('Введите серийный номер')],
           [sg.InputText(key='serial')],
           [sg.Text('Введите количество калибровочных точек')],
           [sg.InputText()],
           [sg.Text('Введите диапазон датчика')],
           [sg.InputText()],
           [sg.Text('Введите степень уравнения')],
           [sg.InputText()],
           [sg.Submit()]]

layout01 = [[sg.Text('Введите коэффициенты калибровочного уравнения')]]

layout02 = [[sg.Text('Термокомпенсация?')],
            [sg.Combo(['Нет', 'Да'],
                      size=(30, 5), key='thermocomp', enable_events=True)],
            [sg.Submit()]]

layout03 = [[sg.Text('Введите коэффициент термокомпенсации')],
            [sg.InputText()],
            [sg.Text('Тип датчика')],
            [sg.Combo(['Струнный', 'Оптоволоконный'],
                      size=(30, 5), key='therm_type', enable_events=True)],
            [sg.Submit()]]

layout1 = [[sg.Text('Калибровка датчика')]]

layout2 = [[sg.Text('Калибровка датчика')],
           [sg.Text('Калибровочное уравнение')]]

#__________________________________________

# Window0
#__________________________________________
window0 = sg.Window('Calibration', layout0)

while True:             # Event Loop
    event0, values0 = window0.read()
    print(event0, values0)
    if event0 == sg.WIN_CLOSED or event0 == 'Exit' or event0 == 'Submit':
        break
    if event0 == '-C-KEY DOWN':
        window0['-C-'].Widget.event_generate('<Down>')
window0.close()
#___________________________________________

# After closing Window0
#___________________________________________
sensor_type = values0['typesensor']
serial = values0['serial']
mode = values0['mode']
back = values0['back']
zero = values0['zero']
num_points = int(values0[0])
sensor_range = int(values0[1])
degree = int(values0[2])
thermocomp = 'Нет'
therm_type = ''
t_coef = 0

if mode == 'Проверка погрешности':
    for i in range(degree):
        layout01.append([sg.InputText(size=(20,5)), sg.Text(f' * x^{degree - i}')])
    layout01.append([sg.InputText(size=(20, 5)), sg.Text('Свободный член')])
    layout01.append([sg.InputText(size=(20, 5), key='convert'), sg.Text('Коэффициент перевода')])
    layout01.append([sg.Submit()])

layout1[0].append(sg.Text(sensor_type))
layout1[0].append(sg.Text(serial))
layout2[0].append(sg.Text(sensor_type))
layout2[0].append(sg.Text(serial))
layout1.append([sg.Text('№', size=(3,)),
                sg.Text(' ', size=(5,)),
                sg.Text('Показания контрольного прибора', size=(20,2)),
                sg.Text('Показания датчика', size=(15,))])
if back == 'Да':
    layout1[-1].append(sg.Text('Показания контрольного прибора обр.', size=(20,2)))
    layout1[-1].append(sg.Text('Показания датчика обр.', size=(15, 2)))
for i in range(num_points+1):
    layout1.append([sg.Text(str(i+1) + ')', size=(3,)),
                    sg.Text(str(round(i * sensor_range / num_points, 2)), size=(5,)),
                    sg.InputText(round(i * sensor_range / num_points, 2), size=(20,5)),
                    sg.InputText(size=(20,5))])
    if back == 'Да':
        layout1[-1].append(sg.InputText(round(i * sensor_range / num_points, 2), size=(20, 5)))
        layout1[-1].append(sg.InputText(size=(20,5)))
layout1.append([sg.Submit()])
#___________________________________________

if mode == 'Проверка погрешности':
    # Window01
    # __________________________________________
    window01 = sg.Window('Calibration', layout01)

    while True:  # Event Loop
        event01, values01 = window01.read()
        print(event01, values01)
        if event01 == sg.WIN_CLOSED or event01 == 'Exit' or event01 == 'Submit':
            break
    window01.close()
    # ___________________________________________


    # After closing Window01
    # ___________________________________________
    calibration_coefs = [float(values01[x].replace(',','.')) for x in values01.keys() if x != 'convert']
    if zero == 'Да':
        calibration_coefs[-1] = 0
    convert = values01['convert']
    if convert != '':
        convert = float(convert.replace(',','.'))
        calibration_coefs = [coef * convert for coef in calibration_coefs]
    # ___________________________________________

    # Window02
    # __________________________________________
    window02 = sg.Window('Calibration', layout02)

    while True:  # Event Loop
        event02, values02 = window02.read()
        print(event02, values02)
        if event02 == sg.WIN_CLOSED or event02 == 'Exit' or event02 == 'Submit':
                break
        if event0 == '-C-KEY DOWN':
            window0['thermocomp'].Widget.event_generate('<Down>')
    window02.close()
    # ___________________________________________

    # After closing Window02
    # ___________________________________________
    thermocomp = values02['thermocomp']
    if thermocomp == 'Да':
        if back != 'Да':
            layout1[1].append(sg.Text('Для термокомп.', size=(15, )))
            for i in range(num_points + 1):
                layout1[2+i].append(sg.InputText(size=(20,5)))
        if back == 'Да':
            layout1[1].insert(4, sg.Text('Для термокомп.', size=(15,)))
            layout1[1].append(sg.Text('Для термокомп.', size=(15,)))
            for i in range(num_points + 1):
                layout1[2 + i].insert(4, sg.InputText(size=(20, 5)))
                layout1[2 + i].append(sg.InputText(size=(20, 5)))
    # ___________________________________________

    if thermocomp == 'Да':
        # Window03
        # __________________________________________
        window03 = sg.Window('Calibration', layout03)

        while True:  # Event Loop
            event03, values03 = window03.read()
            print(event03, values03)
            if event03 == sg.WIN_CLOSED or event03 == 'Exit' or event03 == 'Submit':
                break
        window03.close()
        # ___________________________________________

        # After closing Window03
        # ___________________________________________
        t_coef = float(values03[0].replace(',','.'))
        therm_type = values03['therm_type']
        # ___________________________________________


# Window1
#__________________________________________
window1 = sg.Window('Calibration', layout1)

while True:             # Event Loop
    event1, values1 = window1.read()
    print(event1, values1)
    if event1 == sg.WIN_CLOSED or event1 == 'Exit' or event1 == 'Submit':
        break
window1.close()
#___________________________________________

# After closing Window1
#___________________________________________

if back == 'Да':
    if thermocomp != 'Да':
        contr_sensor = [float(values1[x].replace(',','.')) for x in values1.keys() if x % 4 == 0]
        sensor = [float(values1[x].replace(',','.')) for x in values1.keys() if x % 4 == 1]
        contr_sensor_b = [float(values1[x].replace(',','.')) for x in values1.keys() if x % 4 == 2]
        sensor_b = [float(values1[x].replace(',','.')) for x in values1.keys() if x % 4 == 3]
    else:
        contr_sensor = [float(values1[x].replace(',','.')) for x in values1.keys() if x % 6 == 0]
        sensor = [float(values1[x].replace(',','.')) for x in values1.keys() if x % 6 == 1]
        thermo = [float(values1[x].replace(',','.')) for x in values1.keys() if x % 6 == 2]
        contr_sensor_b = [float(values1[x].replace(',','.')) for x in values1.keys() if x % 6 == 3]
        sensor_b = [float(values1[x].replace(',','.')) for x in values1.keys() if x % 6 == 4]
        thermo_b = [float(values1[x].replace(',','.')) for x in values1.keys() if x % 6 == 5]
    if zero == 'Да':
        sensor_zero = sensor[0]
        sensor = np.array(sensor) - sensor_zero
        sensor_b = np.array(sensor_b) - sensor_zero
else:
    if thermocomp != 'Да':
        contr_sensor = [float(values1[x].replace(',','.')) for x in values1.keys() if x % 2 == 0]
        sensor = [float(values1[x].replace(',','.')) for x in values1.keys() if x % 2 != 0]
    else:
        contr_sensor = [float(values1[x].replace(',','.')) for x in values1.keys() if x % 3 == 0]
        sensor = [float(values1[x].replace(',','.')) for x in values1.keys() if x % 3 == 1]
        thermo = [float(values1[x].replace(',','.')) for x in values1.keys() if x % 3 == 2]
    if zero == 'Да':
        sensor = np.array(sensor) - sensor[0]


if mode == 'Калибровка':
    coefs = get_coefficients(contr_sensor, sensor, degree, zero)
elif mode == 'Проверка погрешности':
    coefs = np.array(calibration_coefs)

print(coefs)
for i in range(degree):
    layout2.append([sg.Text('{:.8f}'.format(coefs[i])), sg.Text('* x ^' + str(degree - i) + ' +')])
layout2.append([sg.Text('{:.8f}'.format(coefs[degree]))])

if back == 'Да':
    if thermocomp != 'Да':
        fig = make_plot(contr_sensor, sensor, coefs, sensor_range,
                        contr_sensor_b, sensor_b)
        acc, df = get_accuracy(contr_sensor, sensor, coefs, sensor_range,
                               contr_sensor_b, sensor_b, t_coef, therm_type)
    else:
        fig = make_plot(contr_sensor, sensor, coefs, sensor_range,
                        contr_sensor_b, sensor_b, thermo, thermo_b)
        acc, df = get_accuracy(contr_sensor, sensor, coefs, sensor_range,
                               contr_sensor_b, sensor_b, thermo, thermo_b, t_coef, therm_type)
else:
    if thermocomp != 'Да':
        fig = make_plot(contr_sensor, sensor, coefs, sensor_range)
        acc, df = get_accuracy(contr_sensor, sensor, coefs, sensor_range)
    else:
        fig = make_plot(contr_sensor, sensor, coefs, sensor_range,
                        thermo)
        acc, df = get_accuracy(contr_sensor, sensor, coefs, sensor_range,
                               thermo, t_coef, therm_type)

print(df)
print(acc)
layout2.append([sg.Text('Относительная погрешность = '), sg.Text('{:.3f}%'.format(acc))])
layout2.append([sg.Text(df)])
layout2.append([sg.Canvas(key='-CANVAS1-')])
#___________________________________________

# Window2
#__________________________________________
window2 = sg.Window('Calibration', layout2, finalize=True)
fig_canvas_agg = draw_figure(window2['-CANVAS1-'].TKCanvas, fig)

while True:             # Event Loop
    event2, values2 = window2.read()
    print(event2, values2)
    if event2 == sg.WIN_CLOSED or event2 == 'Exit' or event2 == 'Submit':
        break
window2.close()
#___________________________________________

# Output file
#___________________________________________
filename = sensor_type + '  ' + serial + '.txt'
with open(filename, "w") as f:
    f.write('Датчик: ' + sensor_type + ', s/n ' + serial)
    f.write('\n')
    f.write('Калибровочное уравнение:')
    f.write('\n')
    for i in range(degree):
        f.write(str('{:.8f}'.format(coefs[i])) + ' * x^' + str(degree - i) + ' + ')
    f.write(str('{:.8f}'.format(coefs[degree])))
    f.write('\n \n')
    dfAsString = df.to_string(header=True, index=True)
    f.write(dfAsString)
    f.write('\n \n')
    f.write('Относительная погрешность = ' + str('{:.3f}%'.format(acc)))
    f.write('\n \n')
    f.write(datetime.today().strftime('%Y-%m-%d'))
#___________________________________________
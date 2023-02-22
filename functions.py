import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from math import log
# from scipy.optimize import curve_fit
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
matplotlib.use('TkAgg')

# def fit_func0(x, coefs):
#     # Curve fitting function
#     n = len(coefs)
#     eq = 0
#     for i in range(n):
#         eq = eq + coefs[i] * x ** (n - i)
#     return eq

def temperature(x):
    a = 1.4051*10**(-3)
    b = 2.369*10**(-4)
    c = 1.1019*10**(-7)
    return (a + b * log(x) + c * (log(x))**3)**(-1) - 273.2

def get_coefficients(contr_sensor, sensor, degree, zero):
    w = np.ones(len(sensor))
    if zero == 'Да':
        w[0] = 1000
    coefs = np.polyfit(x=np.array(sensor), y=np.array(contr_sensor), deg=degree, w=w)
    if zero == 'Да':
        coefs[-1] = 0
    return coefs

def make_plot(contr_sensor, sensor, coefs, sensor_range, *args):
    if len(args) == 1:
        thermo = args[0]
        df = pd.concat([pd.Series(contr_sensor), pd.Series(sensor), pd.Series(thermo)],
                       axis=1)
        ax = sns.scatterplot(data=df, x=df[1], y=df[0])
    if len(args) == 2:
        contr_sensor_b = args[0]
        sensor_b = args[1]
        df = pd.concat([pd.Series(contr_sensor), pd.Series(sensor), pd.Series(contr_sensor_b), pd.Series(sensor_b)], axis=1)
        ax = sns.scatterplot(data=df, x=df[1], y=df[0])
        sns.scatterplot(data=df, x=df[3], y=df[2])
    if len(args) == 4:
        contr_sensor_b = args[0]
        sensor_b = args[1]
        thermo = args[2]
        thermo_b = args[3]
        df = pd.concat([pd.Series(contr_sensor), pd.Series(sensor), pd.Series(contr_sensor_b), pd.Series(sensor_b),
                        pd.Series(thermo), pd.Series(thermo_b)],
                       axis=1)
        ax = sns.scatterplot(data=df, x=df[1], y=df[0])
        sns.scatterplot(data=df, x=df[3], y=df[2])
    else:
        df = pd.concat([pd.Series(contr_sensor), pd.Series(sensor)], axis=1)
        ax = sns.scatterplot(data=df, x=df[1], y=df[0])
    p = np.poly1d(coefs)
    xp = np.linspace(pd.Series(sensor).min(), pd.Series(sensor).max(), 100)
    appr_plot = plt.plot(xp, p(xp))
    fig = ax.get_figure()
    return fig

def get_accuracy(contr_sensor, sensor, coefs, sensor_range, *args):
    p = np.poly1d(coefs)
    if len(args) == 3:
        t_coef = args[1]
        therm_type = args[2]
        if therm_type == 'Оптоволоконный':
            thermo = [x for x in args[0]]
        else:
            thermo = [temperature(x) for x in args[0]]
        # print(t_coef)
        df = pd.concat([pd.Series(contr_sensor), pd.Series(sensor), pd.Series(thermo)],
                       axis=1)
        df.columns = ['Контр.дат.', 'Дат.', 'Темп.']
        df['Темп.разн.'] = df['Темп.'] - thermo[0]
        df['По_ур.'] = p(df['Дат.']) - t_coef * df['Темп.разн.']
        df['Разн.%'] = np.abs(df['По_ур.'] - df['Контр.дат.']) * 100 / sensor_range
        accuracy = np.max(df['Разн.%'])
    elif len(args) == 4:
        contr_sensor_b = args[0]
        sensor_b = args[1]
        t_coef = args[2]
        therm_type = args[3]
        df = pd.concat([pd.Series(contr_sensor), pd.Series(sensor), pd.Series(contr_sensor_b), pd.Series(sensor_b)], axis=1)
        df.columns = ['Контр.дат.', 'Дат.', 'Контр.дат.обр.', 'Дат.обр.']
        df['По_ур.'] = p(df['Дат.'])
        df['По_ур.обр.'] = p(df['Дат.обр.'])
        df['Разн.%'] = np.abs(df['По_ур.'] - df['Контр.дат.']) * 100 / sensor_range
        df['Разн.обр.%'] = np.abs(df['По_ур.обр.'] - df['Контр.дат.обр.']) * 100 / sensor_range
        accuracy = max([df['Разн.%'].max(), df['Разн.обр.%'].max()])
    elif len(args) == 6:
        contr_sensor_b = args[0]
        sensor_b = args[1]
        t_coef = args[4]
        therm_type = args[5]
        if therm_type == 'Оптоволоконный':
            thermo = [x for x in args[2]]
            thermo_b = [x for x in args[3]]
        else:
            thermo = [temperature(x) for x in args[2]]
            thermo_b = [temperature(x) for x in args[3]]
        df = pd.concat([pd.Series(contr_sensor), pd.Series(sensor), pd.Series(contr_sensor_b), pd.Series(sensor_b),
                        pd.Series(thermo), pd.Series(thermo_b)],
                       axis=1)
        df.columns = ['Контр.дат.', 'Дат.', 'Контр.дат.обр.', 'Дат.обр.', 'Темп.', 'Темп.обр.']
        df['Темп.разн.'] = df['Темп.'] - thermo[0]
        df['Темп.разн.обр.'] = df['Темп.обр.'] - thermo[0]
        df['По_ур.'] = p(df['Дат.']) - t_coef * df['Темп.разн.']
        df['По_ур.обр.'] = p(df['Дат.обр.']) - t_coef * df['Темп.разн.обр.']
        df['Разн.%'] = np.abs(df['По_ур.'] - df['Контр.дат.']) * 100 / sensor_range
        df['Разн.обр.%'] = np.abs(df['По_ур.обр.'] - df['Контр.дат.обр.']) * 100 / sensor_range
        accuracy = max([df['Разн.%'].max(), df['Разн.обр.%'].max()])
    else:
        df = pd.concat([pd.Series(contr_sensor), pd.Series(sensor)], axis=1)
        df.columns = ['Контр.дат.', 'Дат.']
        df['По_ур.'] = p(df['Дат.'])
        df['Разн.%'] = np.abs(df['По_ур.'] - df['Контр.дат.']) * 100 / sensor_range
        accuracy = np.max(df['Разн.%'])

    return accuracy, df

def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.get_tk_widget().forget()
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg
#!/usr/bin/env python
# coding: utf-8
import sys
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

while True:
    try:
        mean = input('Введите среднее для нормального распределения:') 
        mean = float(mean)
        break
    except:
        print('Это не число!')

while True:
    try:
        deviation = input('Введите стандартное отклонение для нормального распределения:') 
        deviation = float(deviation)
        break
    except:
        print('Это не число!')

distribution_n1 = np.random.normal(0,1,1000)            
distribution_n2 = np.random.normal(mean,deviation,1000)*2       

sns_plot  = sns.distplot(distribution_n1, kde=True, rug=False)
sns_plot  = sns.distplot(distribution_n2, kde=True, rug=False)
plt.savefig('./output/plot.png')

print('Файл успешно сохранен')
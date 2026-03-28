#!/usr/bin/env python3
import os
import numpy as np
import matplotlib.pyplot as plt
from taxi3_wrapper import TaxiMDPWrapper  # из репозитория + корректировка
from value_iteration import ValueIterationSolver
from visualization import visualize_policy_execution, plot_convergence, plot_value_distribution

import warnings
warnings.filterwarnings("ignore") # скинем упоминание об устаривании

if __name__ == "__main__":
    # 1. Инициализация среды
    mdp = TaxiMDPWrapper('Taxi-v3')
    
    # 2. Обучение стратегии
    solver = ValueIterationSolver(mdp, gamma=0.99)
    policy, V = solver.solve(max_iterations=100)
    
    # 3. Визуализация сходимости
    plot_convergence(solver.get_convergence_history())
    plot_value_distribution(V)
    
    # 4. Демонстрация работы стратегии
    print("\n" + "="*50)
    print("ДЕМОНСТРАЦИЯ ОПТИМАЛЬНОЙ СТРАТЕГИИ")
    print("="*50)
    path, total_reward = visualize_policy_execution(mdp, policy)
    
    # 5. Статистика
    print("\n" + "="*50)
    print(f"Статистика выполнения:")
    print(f"- Пройдено шагов: {len(path)-1}")
    print(f"- Общее вознаграждение: {total_reward:.1f}")
    print(f"- Среднее вознаграждение за шаг: {total_reward/(len(path)-1):.2f}")
    print("="*50)
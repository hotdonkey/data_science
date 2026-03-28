#!/usr/bin/env python3
import os
import numpy as np
import matplotlib.pyplot as plt

def visualize_policy_execution(mdp, policy, max_steps=50):
    """Визуализация маршрута агента"""
    state = mdp.env.reset()
    path = [state]
    total_reward = 0
    
    print("Начальное состояние такси:")
    mdp.env.render()
    
    for step in range(max_steps):
        if mdp.is_terminal(state):
            print(f"\nПассажир доставлен. Общее вознаграждение: {total_reward}")
            break
            
        action = policy.get(state)
        if action is None:
            print("Терминальное состояние достигнуто")
            break
            
        # Выполняем действие
        next_state, reward, done, _ = mdp.env.step(action)
        total_reward += reward
        path.append(next_state)
        state = next_state
        
        if step % 5 == 0:  # Показываем промежуточные шаги
            print(f"\nШаг {step}, Действие: {action}, Вознаграждение: {reward:.1f}")
            mdp.env.render()
    
    return path, total_reward

def plot_convergence(history):
    """График сходимости алгоритма"""
    plt.figure(figsize=(10, 4))
    plt.plot(history, marker='o', markersize=3, linewidth=1.5)
    plt.yscale('log')
    plt.xlabel('Итерация')
    plt.ylabel('Макс. изменение V(s) (лог. шкала)')
    plt.title('Сходимость Value Iteration')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    os.makedirs("./graphs", exist_ok=True)
    plt.savefig('./graphs/convergence.png', dpi=150)

def plot_value_distribution(V, iteration=None):
    """Визуализация распределения value function"""
    values = [v for s, v in V.items() if not np.isinf(v) and not np.isnan(v)]
    
    plt.figure(figsize=(8, 4))
    plt.hist(values, bins=50, color='skyblue', edgecolor='black')
    plt.xlabel('V(s)')
    plt.ylabel('Частота')
    title = 'Распределение Value Function' 
    if iteration is not None:
        title += f' (итерация {iteration})'
    plt.title(title)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    os.makedirs("./graphs", exist_ok=True)
    plt.savefig(f'./graphs/value_dist_{iteration or "final"}.png', dpi=150)
    
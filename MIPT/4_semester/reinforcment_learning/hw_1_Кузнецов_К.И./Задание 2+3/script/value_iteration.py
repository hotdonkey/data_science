#!/usr/bin/env python3
import os
import numpy as np
import matplotlib.pyplot as plt
from taxi3_wrapper import TaxiMDPWrapper  # из репозитория + корректировка
from visualization import visualize_policy_execution, plot_convergence, plot_value_distribution

import warnings
warnings.filterwarnings("ignore") # скинем упоминание об устаривании

class ValueIterationSolver:
    def __init__(self, mdp, gamma=0.99, theta=1e-6):
        self.mdp = mdp
        self.gamma = gamma
        self.theta = theta
        self.V = {s: 0.0 for s in mdp.get_all_states()}
        self.policy = {s: None for s in mdp.get_all_states()}
        self.history = []  # для визуализации сходимости
        
    def solve(self, max_iterations=1000):
        for iteration in range(max_iterations):
            delta = 0
            # Policy Evaluation (одна итерация)
            for s in self.mdp.get_all_states():
                if self.mdp.is_terminal(s):
                    continue
                    
                v_old = self.V[s]
                action_values = []
                
                for a in self.mdp.get_possible_actions(s):
                    q_value = 0
                    for s_next in self.mdp.get_next_states(s, a):
                        p = self.mdp.get_transition_prob(s, a, s_next)
                        r = self.mdp.get_reward(s, a, s_next)
                        q_value += p * (r + self.gamma * self.V[s_next])
                    action_values.append((a, q_value))
                
                if action_values:
                    self.V[s] = max(q for _, q in action_values)
                    delta = max(delta, abs(v_old - self.V[s]))
            
            self.history.append(delta)
            
            if delta < self.theta:
                print(f"Сходимость достигнута на итерации {iteration}")
                break
        
        # Policy Extraction
        for s in self.mdp.get_all_states():
            if self.mdp.is_terminal(s):
                self.policy[s] = None
                continue
                
            best_action, best_value = None, -np.inf
            for a in self.mdp.get_possible_actions(s):
                q_value = 0
                for s_next in self.mdp.get_next_states(s, a):
                    p = self.mdp.get_transition_prob(s, a, s_next)
                    r = self.mdp.get_reward(s, a, s_next)
                    q_value += p * (r + self.gamma * self.V[s_next])
                
                if q_value > best_value:
                    best_value = q_value
                    best_action = a
            
            self.policy[s] = best_action
        
        return self.policy, self.V

    def get_convergence_history(self):
        return self.history

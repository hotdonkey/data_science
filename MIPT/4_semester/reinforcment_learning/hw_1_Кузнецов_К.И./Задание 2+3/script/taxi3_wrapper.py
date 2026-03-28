import gym
import numpy as np

class TaxiMDPWrapper:
    def __init__(self, env_name='Taxi-v3'):
        # Важно: для новых версий Gym используйте gymnasium
        try:
            import gymnasium as gym
            self.env = gym.make(env_name, render_mode=None)
        except ImportError:
            import gym
            self.env = gym.make(env_name)
        
        self.env.reset(seed=42)
        self.states = list(range(self.env.observation_space.n))
        self.actions = list(range(self.env.action_space.n))  # 6 действий!

    def get_all_states(self):
        return self.states

    def get_possible_actions(self, state):
        """
        В Taxi-v3 ВСЕ действия доступны в любом состоянии.
        Среда сама обрабатывает "неправильные" действия (возвращает штраф -10).
        """
        if self.is_terminal(state):
            return []
        return self.actions  # [0, 1, 2, 3, 4, 5]

    def get_next_states(self, state, action):
        """
        Возвращает {следующее_состояние: вероятность}
        Среда детерминированная → вероятность = 1.0
        """
        # Структура env.P[state][action]: список [(prob, next_state, reward, terminated)]
        transitions = self.env.P[state][action]
        next_states = {}
        for prob, next_state, reward, terminated in transitions:
            next_states[next_state] = prob
        return next_states

    def get_reward(self, state, action, state_next):
        """Возвращает вознаграждение за переход"""
        transitions = self.env.P[state][action]
        for prob, next_state, reward, terminated in transitions:
            if next_state == state_next:
                return reward
        return 0  # fallback

    def get_transition_prob(self, state, action, state_next):
        """Возвращает вероятность перехода (детерминированная среда)"""
        transitions = self.env.P[state][action]
        for prob, next_state, reward, terminated in transitions:
            if next_state == state_next:
                return prob
        return 0.0

    def is_terminal(self, state):
        """Проверяет, является ли состояние терминальным"""
        # В Taxi-v3 терминальные состояния имеют только действие "ничего не делать"
        # Проще проверить через переходы: если все действия ведут к себе же с done=True
        for action in self.actions:
            transitions = self.env.P[state][action]
            if transitions:
                _, _, _, terminated = transitions[0]
                if not terminated:
                    return False
        return True
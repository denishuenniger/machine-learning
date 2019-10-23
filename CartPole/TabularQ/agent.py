import gym
import os
import pickle
import numpy as np
import matplotlib.pyplot as plt

from collections import defaultdict


class Agent:

    def __init__(self, env, gamma, alpha, epsilon, epsilon_min, epsilon_decay):
        self.env = env
        self.num_states = self.env.observation_space.shape[0]
        self.num_actions = self.env.action_space.n
        self.q = defaultdict(lambda : [0.0 for _ in range(self.num_actions)])
        self.gamma = gamma
        self.alpha = alpha
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay

        # File paths
        dirname = os.path.dirname(__file__)
        self.path_model = os.path.join(dirname, "models/q.pickle")
        self.path_plot = os.path.join(dirname, "plots/q.png")


    def convert_state(self, state):
        return '_'.join([str(np.round(x, 2)) for x in state])

    
    def get_action(self, state):
        state = self.convert_state(state)
        action = np.argmax(self.q[state])

        return action


    def get_value(self, state):
        value = np.max(self.q[state])

        return value


    def get_random_action(self):
        action = self.env.action_space.sample()
        return action


    def update_q_values(self, state, action, reward, next_state):
        state = self.convert_state(state)
        next_state = self.convert_state(next_state)
        
        q_update = reward + self.gamma * self.get_value(next_state)
        q = self.q[state][action]
        q = (1 - self.alpha) * q + self.alpha * q_update

        self.q[state][action] = q


    def save_q_values(self):
        with open(self.path_model, "wb") as file:
            pickle.dumps(dict(self.q))

    
    def load_q_values(self):
        try:
            with open(self.path_model, "rb") as file:
                self.q = defaultdict(pickle.load(file))
        except:
            print("Model does not exist! Create new model...")


    def reduce_epsilon(self):
        epsilon = self.epsilon * self.epsilon_decay

        if epsilon >= self.epsilon_min:
            self.epsilon = epsilon
        else:
            self.epsilon = self.epsilon_min


    def train(self, num_episodes):
        total_rewards = []
        self.load_q_values()  
        
        for episode in range(num_episodes):
            state = self.env.reset()
            total_reward = 0.0

            while True:
                if np.random.random() <= self.epsilon:
                    action = self.get_random_action()
                    self.reduce_epsilon()
                else:
                    action = self.get_action(state)

                next_state, reward, done, _ = self.env.step(action)
                
                if done and reward != 500.0: reward = -100.0
                
                self.update_q_values(state, action, reward, next_state)
                total_reward += reward
                state = next_state

                if done:
                    total_reward += 100
                    total_rewards.append(total_reward)
                    mean_total_rewards = np.mean(total_rewards[-10:])

                    print(f"Episode: {episode + 1}/{num_episodes} \tTotal Reward: {total_reward} \tMean Total Rewards: {mean_total_rewards}")

                    if mean_total_rewards >= 495.0:
                        self.save_q_values()
                        return total_rewards
                    else:
                        break

        self.save_q_values()
        return total_rewards


    def play(self, num_episodes):
        self.load_q_values()
        
        for episode in range(num_episodes):
            state = self.env.reset()
            total_reward = 0.0

            while True:
                self.env.render()
                action = self.get_action(state)
                state, reward, done, _ = self.env.step(action)
                total_reward += reward

                if done:
                    print(f"Episode: {episode + 1} \tTotal Reward: {total_reward}")
                    break


    def plot_rewards(self, total_rewards):
        plt.plot(range(len(total_rewards)), total_rewards, linewidth=0.8)
        plt.xlabel("Episode")
        plt.ylabel("Reward")
        plt.title("Total Rewards")
        plt.savefig(self.path_plot)


if __name__ == "__main__":

    # Hyperparameters
    GAMMA = 0.9
    ALPHA = 0.8
    EPSILON = 0.9
    EPSILON_MIN = 0.1
    EPSILON_DECAY = 0.95

    PLAY = False
    EPISODES_TRAIN = 100000
    EPISODES_PLAY = 5
    
    env = gym.make("CartPole-v1")
    agent = Agent(env, gamma=GAMMA, alpha=ALPHA, epsilon=EPSILON, epsilon_min=EPSILON_MIN, epsilon_decay=EPSILON_DECAY)

    if not PLAY:
        total_rewards = agent.train(num_episodes=EPISODES_TRAIN)
        agent.plot_rewards(total_rewards)
    else:
        agent.play(num_episodes=EPISODES_PLAY)
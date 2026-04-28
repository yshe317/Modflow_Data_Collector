import numpy as np
import random

class BayesianOptimizer:
    def __init__(self, model, max_iter = 50):
        self.model = model
        self.max_iter = max_iter
    
    def optimize(self, initial_guess, target):
        """
        优化模型参数
        """
        current = initial_guess
        current_output = self.model.forward(current)
        current_likelihood = self._likelihood(current_output, target)
        current_prior = self._prior(current)
        current_posterior = current_likelihood + current_prior
        
        for i in range(self.max_iter):
            # 生成新的参数候选
            candidate = self._generate_candidate(current)
            
            # 计算候选参数的似然函数和先验概率
            candidate_output = self.model.forward(candidate)
            candidate_likelihood = self._likelihood(candidate_output, target)
            candidate_prior = self._prior(candidate)
            candidate_posterior = candidate_likelihood + candidate_prior
            
            # 计算接受概率（考虑似然和先验）
            acceptance_prob = min(1, np.exp(candidate_posterior - current_posterior))
            
            # 根据接受概率更新参数
            if random.random() < acceptance_prob:
                current = candidate
                current_posterior = candidate_posterior
        
        return current
    
    def _generate_candidate(self, current):
        """
        生成新的参数候选
        """
        # 添加高斯噪声生成候选参数
        noise = np.random.normal(0, 0.1, size=current.shape)
        return current + noise
    
    def _prior(self, candidate):
        """
        计算对数先验概率
        假设先验为零均值、单位方差的高斯分布
        """
        # log(P(θ)) = -0.5 * θ^T θ + constant
        # return -0.5 * np.sum(candidate ** 2)
        
        # mock one
        return 0.5
    def _likelihood(self, output, target):
        """
        计算对数似然函数
        """
        # 使用高斯似然模型：log(P(D|θ)) ∝ -0.5 * ||output - target||^2
        return -0.5 * np.mean((output - target) ** 2)
    

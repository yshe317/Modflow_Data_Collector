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
        self.model.forward(current)
        current_output = self.model.get_concentration()
        current_likelihood = self._likelihood(current_output, target)
        current_prior = self._prior(current)
        current_posterior = current_likelihood + current_prior
        best = current
        best_posterior = 0
        for i in range(self.max_iter):
            # 打印进度条
            progress = f"\rProgress: {i+1}/{self.max_iter}"
            print(progress, end="", flush=True)
            
            # 生成新的参数候选
            candidate = self._generate_candidate(current)
            
            # 计算候选参数的似然函数和先验概率
            self.model.forward(candidate)
            candidate_output = self.model.get_concentration()
            candidate_likelihood = self._likelihood(candidate_output, target)
            candidate_prior = self._prior(candidate)
            candidate_posterior = candidate_likelihood + candidate_prior
            if candidate_posterior > best_posterior:
                best = candidate
                best_posterior = candidate_posterior
            # 计算接受概率（考虑似然和先验）
            acceptance_prob = min(1, np.exp(candidate_posterior - current_posterior))
            # 根据接受概率更新参数
            if random.random() < acceptance_prob:
                current = candidate
                current_posterior = candidate_posterior
        
        return current, best
    
    def _generate_candidate(self, current):
        """
        生成新的参数候选
        """
        plt_position = current[0].copy() #(2)
        plt_quantity = current[1].copy() #(2)
        plt_time = current[2].copy() #(2)

        # 定义各参数的搜索步长
        position_step = 1      # 位置变化步长
        amount_step = 5        # 数量变化步长
        conc_step = 1          # 浓度变化步长
        time_step = 1          # 时间变化步长
        # 处理位置参数 [x, y]
        x, y = current[0]
        new_x = x + np.random.randint(-position_step, position_step+1)
        new_y = y + np.random.randint(-position_step, position_step+1)

        # 处理数量和浓度 [amount, concentration]
        amount, conc = current[1]
        new_amount = amount + np.random.randint(-amount_step, amount_step+1)
        new_conc = conc + np.random.randint(-conc_step, conc_step+1)

        # 处理时间参数 [begin_time, end_time]
        begin, end = current[2]
        new_begin = begin + np.random.randint(-time_step, time_step+1)
        new_end = end + np.random.randint(-time_step, time_step+1)
        
        max_col, max_row,max_amount,max_conc, max_begin, max_end = self.model.constraint()
        new_x = np.clip(new_x, 0, max_col)        # 假设x范围0-100
        new_y = np.clip(new_y, 0, max_row)        # 假设y范围0-100
        new_amount = np.clip(new_amount, 1, max_amount)   # 数量范围1-1000
        new_conc = np.clip(new_conc, 1, max_conc)  # 浓度范围1-100
        new_begin = np.clip(new_begin, 0, max_begin)  # 开始时间0-23
        new_end = np.clip(new_end, new_begin+1, max_end)  # 结束时间必须在开始时间后
        return [[int(new_x), int(new_y)], [float(new_amount), float(new_conc)], [int(new_begin), int(new_end)]]
    
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
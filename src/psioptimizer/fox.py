import numpy as np


class GWO:
    def __init__(self, model, max_iter=100, population_size=30):
        self.model = model
        self.max_iter = max_iter
        self.population_size = population_size

    def optimize(self, lb, ub, dim, fobj, *args):
        if len(ub) == 1:
            ub = np.full(dim, ub[0])
            lb = np.full(dim, lb[0])

        Alpha_pos = np.zeros(dim)
        Alpha_score = float('inf')

        Beta_pos = np.zeros(dim)
        Beta_score = float('inf')

        Delta_pos = np.zeros(dim)
        Delta_score = float('inf')

        Convergence_curve = np.zeros(self.max_iter)

        X = np.random.uniform(low=lb, high=ub, size=(self.population_size, dim))

        l = 0
        while l < self.max_iter:
            for i in range(self.population_size):
                Flag4ub = X[i, :] > ub
                Flag4lb = X[i, :] < lb
                X[i, :] = X[i, :] * (~(Flag4ub + Flag4lb)) + ub * Flag4ub + lb * Flag4lb

                fitness = fobj(X[i, :], *args)

                if fitness < Alpha_score:
                    Alpha_score = fitness
                    Alpha_pos = X[i, :].copy()

                if Alpha_score < fitness < Beta_score:
                    Beta_score = fitness
                    Beta_pos = X[i, :].copy()

                if Alpha_score < fitness and Beta_score < fitness < Delta_score:
                    Delta_score = fitness
                    Delta_pos = X[i, :].copy()

            a = 2 - l * (2 / self.max_iter)

            for i in range(self.population_size):
                for j in range(dim):
                    r1 = np.random.rand()
                    r2 = np.random.rand()

                    A1 = 2 * a * r1 - a
                    C1 = 2 * r2

                    D_alpha = np.abs(C1 * Alpha_pos[j] - X[i, j])
                    X1 = Alpha_pos[j] - A1 * D_alpha

                    r1 = np.random.rand()
                    r2 = np.random.rand()

                    A2 = 2 * a * r1 - a
                    C2 = 2 * r2

                    D_beta = np.abs(C2 * Beta_pos[j] - X[i, j])
                    X2 = Beta_pos[j] - A2 * D_beta

                    r1 = np.random.rand()
                    r2 = np.random.rand()

                    A3 = 2 * a * r1 - a
                    C3 = 2 * r2

                    D_delta = np.abs(C3 * Delta_pos[j] - X[i, j])
                    X3 = Delta_pos[j] - A3 * D_delta

                    X[i, j] = (X1 + X2 + X3) / 3

            l = l + 1
            Convergence_curve[l - 1] = Alpha_score

            print(f"GWO: {l} {Alpha_score}")

        return Alpha_score, Alpha_pos, Convergence_curve
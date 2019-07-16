import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colours
import copy
import time

""" A population split into M demes with members having either A or a alleles """
class Population:
    def __init__(self, M, N, m):
        self.M = M
        self.m = m
        self.N = N
        self.demes = [Deme(N) for i in range(M)]
        self.age = 0

    def evolve(self, time):
        for i in range(time):
            # self.migrate()
            for deme in self.demes:
                deme.generation()
        self.age = time

    def migrate(self):
        migrant_pool = {
            "a": 0,
            "A": 0
        }

        # all demes donate to migrant pool
        for i in range(self.M):
            for let in ["a", "A"]:
                migrants = int(self.m * self.demes[i].count[let])
                migrant_pool[let] += migrants
                self.demes[i].count[let] -= migrants

        # calculate divisor and remainder for equal distribution
        div = {
            "a": migrant_pool["a"] // self.M,
            "A": migrant_pool["A"] // self.M,
        }
        rem = {
            "a": migrant_pool["a"] % self.M,
            "A": migrant_pool["A"] % self.M,
        }

        # give all demes an equal distribution of the pool
        for i in range(self.M):
            for let in ["a", "A"]:
                add = div[let]
                if rem[let] > 0:
                    add += 1
                    rem[let] -= 1
                self.demes[i].count[let] += add


    def print_self(self):
        print("Population at time {0}".format(self.age))
        for deme in self.demes:
            deme.print_self()
        print()

    def plot_self(self, sample_freq=100, together=True):
        if together:
            for i in range(self.M):
                plt.plot(range(self.age + 1)[0::sample_freq], np.divide(self.demes[i].history["a"][0::sample_freq], self.N), label=i)
            plt.xlabel("Time", fontsize="small")
            plt.ylabel("Allele Frequency", fontsize="small")
            plt.show()
        else:
            _, axes = plt.subplots(self.M, 1, sharex=True, sharey=True)
            for i in range(self.M):
                axes[i].stackplot(range(self.age + 1)[0::sample_freq], 
                    [np.divide(self.demes[i].history["a"][0::sample_freq], self.N), np.divide(self.demes[i].history["A"][0::sample_freq], self.N)],
                    labels=["a Allele", "A Allele"]
                )
                axes[i].set_xlabel("Time", fontsize="small")
                axes[i].set_xlim((0, GENERATIONS))
                axes[i].set_ylim((0, 1))
                axes[i].set_yticks([])
            plt.show()

class Deme:
    def __init__(self, N):
        self.N = N
        self.count = {
            "a": int(np.floor(N / 2)),
            "A": int(np.ceil(N / 2))
        }
        self.history = {
            "a": [self.count["a"]],
            "A": [self.count["A"]]
        }
        self.environment = 0

    def generation(self):
        if self.count["a"] != 0 and self.count["A"] != 0:
            # calculate new totals
            weighted_total = self.count["a"] * (1 + BENEFIT) + self.count["A"]
            trans_prob = (self.count["a"] * (1 + BENEFIT) * (1 - NU) + self.count["A"] * MU) / weighted_total
            self.count["a"] = np.random.binomial(self.N, trans_prob)
            self.count["A"] = self.N - self.count["a"]

        # switch environments
        if self.environment == 0:
            self.environment = np.random.choice([0, 1], p=[1 - ALPHA, ALPHA])
        else:
            self.environment = np.random.choice([0, 1], p=[BETA, 1 - BETA])

        # a is lethal in environment 1
        if self.environment == 1:
            self.count["a"] = 0

        self.history["a"].append(self.count["a"])
        self.history["A"].append(self.count["A"])

    def print_self(self):
        print("a count {0}, A count {1}, Environment {2}".format(self.count["a"], self.count["A"], self.environment))

GENERATIONS = 100
DEMES = 10
DEME_SIZE = 100
BENEFIT = 0.1
MU = 0.02
NU = 0
ALPHA = 5 / GENERATIONS
BETA = 1 - ALPHA

def main():
    # start = time.time()
    pop = Population(DEMES, DEME_SIZE, 0.1)
    pop.evolve(GENERATIONS)
    pop.plot_self(1)
    # end = time.time()
    # print("Elapsed {0}".format(end - start))

if __name__ == "__main__":
    main()
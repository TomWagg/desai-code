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
        self.dead = False

    def evolve(self, time, benefit, mu, nu, alpha, beta):
        for i in range(time):
            if self.dead:
                self.age = i
                return
            pool = self.migrate()
            dead = True
            for deme in self.demes:
                if not deme.generation(pool, benefit, mu, nu, alpha, beta):
                    dead = False
            self.dead = dead
            # print()
        self.age = time

    def migrate(self):
        migrant_pool = {
            "a": 0,
            "A": 0
        }
        for i in range(self.M):
            for let in ["a", "A"]:
                migrants = int(self.m * self.demes[i].count[let])
                migrant_pool[let] += migrants
                self.demes[i].count[let] -= migrants
        return migrant_pool

    def print_self(self):
        print("Population at time {0}".format(self.age))
        for deme in self.demes:
            deme.print_self()
        print()

    def plot_self(self, sample_freq=100, colour=None, together=True, label=None, faint_lines=False):
        if together:
            lines = []
            for i in range(self.M):
                line = np.divide(self.demes[i].history["a"][0::sample_freq], self.N)
                lines.append(line)
                if faint_lines:
                    plt.plot(range(self.age + 1)[0::sample_freq], line, color=colour, alpha=0.1)
            average = [0 for i in range(len(lines[0]))]
            for i in range(len(lines[0])):
                for j in range(len(lines)):
                    average[i] += lines[j][i]
                average[i] /= len(lines)
            plt.plot(range(self.age + 1)[0::sample_freq], average, label=label, color=colour, linewidth=1.5)
            plt.xlabel("Time", fontsize="small")
            plt.ylabel("Allele Frequency", fontsize="small")
        else:
            _, axes = plt.subplots(self.M, 1, sharex=True, sharey=True)
            for i in range(self.M):
                axes[i].stackplot(range(self.age + 1)[0::sample_freq], 
                    [np.divide(self.demes[i].history["a"][0::sample_freq], self.N), np.divide(self.demes[i].history["A"][0::sample_freq], self.N)],
                    labels=["a Allele", "A Allele"]
                )
                axes[i].set_xlabel("Time", fontsize="small")
                axes[i].set_xlim((0, self.age))
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

    def generation(self, pool, benefit, mu, nu, alpha, beta):
        dead = False

        # calculate new totals
        weighted_total = (self.count["a"] + pool["a"]) * (1 + benefit) + (self.count["A"] + pool["A"])
        if weighted_total > 0:
            trans_prob = ((self.count["a"] + pool["a"]) * (1 + benefit) * (1 - nu) + (self.count["A"] + pool["A"]) * mu) / weighted_total
            self.count["a"] = np.random.binomial(self.N, trans_prob)
            self.count["A"] = self.N - self.count["a"]
        else:
            dead = True

        # switch environments
        if self.environment == 0:
            self.environment = np.random.choice([0, 1], p=[1 - alpha, alpha])
        else:
            self.environment = np.random.choice([0, 1], p=[beta, 1 - beta])

        # a is lethal in environment 1
        if self.environment == 1:
            self.count["a"] = 0

        self.history["a"].append(self.count["a"])
        self.history["A"].append(self.count["A"])

        # self.print_self()

        return dead

    def print_self(self):
        print("a count {0}, A count {1}, Environment {2}".format(self.count["a"], self.count["A"], self.environment))

def main():
    # constant parameters
    GENERATIONS = 1000
    DEMES, DEME_SIZE = 5, 1000
    NU = 0
    SELECTION = 0.05
    BETA = 10 / GENERATIONS

    limits = {
        "m>>mu=a": [(1, 1, 1), (1, 1, 10), (1, 1, 100), (1, 1, 1000),(1, 1, 10000)],
        "m>>mu>>a": [(1, 1, 1), (10, 1, 100), (100, 1, 1000), (1000, 1, 10000)],
        "mu>>m=a": [(1, 1, 1), (10, 1, 1), (100, 1, 1), (1000, 1, 1),(10000, 1, 1)],
        "mu>>m>>a": [(1, 1, 1), (100, 1, 10), (1000, 1, 100), (10000, 1, 1000)],
        "a>>mu=m": [(1, 1, 1), (1, 10, 1), (1, 100, 1), (1, 1000, 1), (1, 10000, 1)],
        "a>>mu>>m": [(1, 1, 1), (1, 100, 10), (1, 1000, 100), (1, 10000, 1000)],
        "all_a, all_A": [(1, 2, 1)]
    }
    LIMIT = "all_a, all_A"
    space = np.multiply(np.divide(limits[LIMIT], DEME_SIZE), (1, 1, 1))
    colours = [plt.cm.jet(1.*j / (len(space))) for j in range(len(space))]
    i = 0

    start = time.time()
    for mu, alpha, m in space:
        pop = Population(DEMES, DEME_SIZE, m)
        pop.evolve(GENERATIONS, SELECTION, mu, NU, alpha, BETA)
        pop.plot_self(1, colours[i], faint_lines=True, label=r"$\mu, \alpha, m$ = {0:.0e}, {1:.0e}, {2:.0e}".format(mu, alpha, m))
        i += 1    
    end = time.time()
    print("Time", end - start)

    plt.title("a Allele Frequency in the limit of " + LIMIT)
    plt.legend(loc="center right", fontsize="small")
    plt.show()

if __name__ == "__main__":
    main()
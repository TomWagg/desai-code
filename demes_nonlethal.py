import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colours
import time

""" A population split into M demes with members having either A or a alleles """
class Population:
    def __init__(self, params):
        self.M = params["demes"]
        self.m = params["m"]
        self.N = params["deme_size"]
        self.demes = [Deme(params["deme_size"]) for i in range(params["demes"])]
        self.age = 0
        self.fixed = False
        self.extinct = False

        # add 'a' alleles
        for i in range(100):
            choice = self.demes[np.random.randint(0, len(self.demes))]
            while choice.count["A"] == 0:
                choice = self.demes[np.random.randint(0, len(self.demes))]
            choice.count["a"] += 1
            choice.count["A"] -= 1

    # keep evolving until an allele fixes; migrate and then have each deme reproduce
    def evolve(self, params):
        while not self.fixed and not self.extinct:
            self.migrate()
            fixed, extinct = True, True
            for deme in self.demes:
                fix, ex = deme.generation(params["selection"], params["mu"], params["nu"], params["alpha"], params["beta"])
                if not fix:
                    fixed = False
                if not ex:
                    extinct = False
            self.fixed = fixed
            self.extinct = extinct
            self.age += 1

    # randomly draw m individuals from each deme into a pool and then randomly distribute them
    def migrate(self):
        migrant_pool = {
            "a": 0,
            "A": 0
        }
        for deme in self.demes:
            migrants = np.random.binomial(self.m, deme.count["a"] / (deme.count["a"] + deme.count["A"]))
            migrants = deme.count["a"] if migrants > deme.count["a"] else migrants
            if self.m - migrants > deme.count["A"]:
                migrants = self.m - deme.count["A"]
            migrant_pool["a"] += migrants
            deme.count["a"] -= migrants
            migrant_pool["A"] += (self.m - migrants)
            deme.count["A"] -= (self.m - migrants)
            
        for deme in self.demes:
            returners = min(np.random.randint(0, self.m + 1), migrant_pool["a"])
            returners = migrant_pool["a"] if returners > migrant_pool["a"] else returners
            if self.m - returners > migrant_pool["A"]:
                returners = self.m - migrant_pool["A"]
            migrant_pool["a"] -= returners
            deme.count["a"] += returners
            migrant_pool["A"] -= (self.m - returners)
            deme.count["A"] += (self.m - returners)

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

""" A deme of N individuals which have either the a or A allele and exist in one of two environments """
class Deme:
    def __init__(self, N):
        self.N = N
        self.count = {
            "a": 0,
            "A": N
        }
        self.environment = np.random.randint(0, 2)

    # sample new individuals from distribution then possibly switch environment
    def generation(self, benefit, mu, nu, alpha, beta):
        weighted_total = self.count["a"] * (1 + benefit["a"][self.environment]) + self.count["A"] * (1 + benefit["A"][self.environment])
        trans_prob = (self.count["a"] * (1 + benefit["a"][self.environment]) * (1 - nu) + self.count["A"] * (1 + benefit["A"][self.environment]) * mu) / weighted_total
        
        self.count["a"] = np.random.binomial(self.N, trans_prob)
        self.count["A"] = self.N - self.count["a"]
        
        if self.environment == 0:
            self.environment = np.random.choice([0, 1], p=[1 - alpha, alpha])
        else:
            self.environment = np.random.choice([0, 1], p=[beta, 1 - beta])
        return self.count["a"] == self.N, self.count["A"] == self.N

    def print_self(self):
        print("a count {0}, A count {1}, Environment {2}".format(self.count["a"], self.count["A"], self.environment))

def main():
    REPEATS = 50
    print("Simulation with", REPEATS, "repeats")
#serial requeue

    time_record = [time.time()]
    options = [(1, 10000), (2, 5000), (4, 2500)]
    for i in range(len(options)):
        averages = []
        for j in range(REPEATS):
            averages.append(run_simulation({
                "pop": {
                    "demes": options[i][0],
                    "deme_size": options[i][1],
                    "m": 5
                },
                "evolve": {
                    "selection": {
                        "a": [0.1, 0],
                        "A": [0, 0.01]
                    },
                    "mu": 0,
                    "nu": 0,
                    "alpha": 0.01,
                    "beta": 0.002,
                }
            }))
        fix_prob = 0
        avgtime = 0
        for t, fix in averages:
            fix_prob += int(fix)
            avgtime += t if fix else 0
        avgtime /= fix_prob if fix_prob != 0 else 1
        fix_prob /= len(averages)
        time_record.append(time.time())
        print("Demes: {0}, Deme Size: {1}, Fixation Probability {2}, Avg Fixation Time {3}, (Time at Completion {4})".format(options[i][0], options[i][1], fix_prob, round(avgtime), round(time_record[-1] - time_record[-2], 2)))
    time_record.append(time.time())
    print("Time", str(round(time_record[-1] - time_record[0], 2)) + "s")

def run_simulation(params):
    pop = Population(params["pop"])
    pop.evolve(params["evolve"])
    return pop.age, pop.fixed

if __name__ == "__main__":
    main()
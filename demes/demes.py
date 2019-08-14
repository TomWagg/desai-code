import numpy as np
import sys
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

        # add 'a' alleles to population
        for i in range(100):
            choice = self.demes[np.random.randint(0, len(self.demes))]
            while choice.count["A"] == 0:
                choice = self.demes[np.random.randint(0, len(self.demes))]
            choice.count["a"] += 1
            choice.count["A"] -= 1

    def evolve(self, params):
        # evolve the population until an allele fixes
        while not self.fixed and not self.extinct:
            self.migrate()

            # reproduce each deme and if any are not fixed or not extinct then slip booleans
            fixed, extinct = True, True
            for deme in self.demes:
                fix, ex = deme.reproduce(params["selection"], params["mu"], params["nu"], params["alpha"], params["beta"])
                if not fix:
                    fixed = False
                if not ex:
                    extinct = False
            self.fixed = fixed
            self.extinct = extinct
            self.age += 1

    def migrate(self):
        # calculate the number of migrants
        n_migrant = round(self.m * self.N)

        # randomly choose m individuals from each deme, put them in the pool and adjust deme counts
        migrant_pool = []
        for deme in self.demes:
            migrants = list(np.random.choice(["a"] * deme.count["a"] + ["A"] * deme.count["A"], size=n_migrant, replace=False))
            migrant_pool += migrants
            for allele in ["a", "A"]:
                deme.count[allele] -= migrants.count(allele)
            
        # shuffle the order of the migrant pool
        np.random.shuffle(migrant_pool)
        migrant_pool = list(migrant_pool)

        # remove the first m individuals from the pool and adjust deme counts back up
        for deme in self.demes:
            selection = migrant_pool[:n_migrant]
            del migrant_pool[:n_migrant]
            for allele in ["a", "A"]:
                deme.count[allele] += selection.count(allele)

    def print_self(self):
        print("Population at time {0}".format(self.age))
        for deme in self.demes:
            deme.print_self()
        print()

""" A deme of N individuals which have either the a or A allele and exist in one of two environments """
class Deme:
    def __init__(self, N):
        self.N = N
        self.count = {
            "a": 0,
            "A": N
        }
        self.environment = np.random.randint(0, 2)

    def reproduce(self, benefit, mu, nu, alpha, beta):
        # calculate the transition probability based on the environment, counts and mutation rates
        weighted_total = self.count["a"] * (1 + benefit["a"][self.environment]) + self.count["A"] * (1 + benefit["A"][self.environment])
        trans_prob = (self.count["a"] * (1 + benefit["a"][self.environment]) * (1 - nu) + self.count["A"] * (1 + benefit["A"][self.environment]) * mu) / weighted_total

        # sample new counts from binomial based on transition probability above        
        self.count["a"] = np.random.binomial(self.N, trans_prob)
        self.count["A"] = self.N - self.count["a"]
        
        # possibily change environment
        if self.environment == 0:
            self.environment = np.random.choice([0, 1], p=[1 - alpha, alpha])
        else:
            self.environment = np.random.choice([0, 1], p=[beta, 1 - beta])

        # return booleans of whether fixation or extinction has occured
        return self.count["a"] == self.N, self.count["A"] == self.N

    def print_self(self):
        print("a count {0}, A count {1}, Environment {2}".format(self.count["a"], self.count["A"], self.environment))

def main():
    REPEATS = 100
    s = 0.01
    f = 10

    start = time.time()

    # check if they didn't provide CLAs
    if len(sys.argv) != 3:
        print("USAGE: python demes.py M N")
        return
    M, N = int(sys.argv[1]), int(sys.argv[2])
    averages = []

    # run the same simulation REPEATS times
    for i in range(REPEATS):
        averages.append(run_simulation({
            "pop": {
                "demes": M,
                "deme_size": N,
                "m": 0.01
            },
            "evolve": {
                "selection": {
                    "a": [f * s, 0],
                    "A": [0, s]
                },
                "mu": 0,
                "nu": 0,
                "alpha": s,
                "beta": 2 * s / f,
            }
        }))

    # find the fraction of simulations in which 'a' fixed and the fixation times for those
    fix_prob, avgtime = 0, 0
    for t, fix in averages:
        fix_prob += int(fix)
        avgtime += t if fix else 0
    avgtime /= fix_prob if fix_prob != 0 else 1
    fix_prob /= len(averages)
    print(M, N, fix_prob, round(avgtime), sep=",")
    print(time.time() - start)

# create new population, evolve until an allele fixes and return stats
def run_simulation(params):
    pop = Population(params["pop"])
    pop.evolve(params["evolve"])
    return pop.age, pop.fixed

if __name__ == "__main__":
    main()
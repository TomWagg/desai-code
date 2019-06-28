import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colours
import copy

""" A population of individuals with genomes and mutations """
class Population:
    # create members with the same number of loci
    def __init__(self, size, loci):
        self.N = size
        self.members = [Member(loci) for i in range(self.N)]

    # randomly (with weights) choose a member to clone and increase mutation frequencies
    def reproduce(self, tactic=None):
        if tactic == "weighted-random":
            fitnesses = np.array([member.fitness for member in self.members])
            fitnesses += (1 - min(fitnesses))
            child = np.random.choice(self.members, None, True, np.divide(fitnesses, np.sum(fitnesses)))
        elif tactic == "survial-fittest":
            child = None
            for i in range(self.N):
                if child is None or self.members[i].fitness > child.fitness:
                    child = self.members[i]
        else:
            print("Invalid tactic")
            exit(0)
        
        return copy.deepcopy(child)

    # uniformly randomly select a member to die and decrease mutation frequencies
    def death(self, tactic=None):
        if tactic == "uniform-random":
            dead_member = self.members[np.random.randint(0, self.N)]
        elif tactic == "weakest-link":
            dead_member = None
            for i in range(self.N):
                if dead_member is None or self.members[i].fitness < dead_member.fitness:
                    dead_member = self.members[i]
        else:
            print("Invalid tactic")
            exit(0)
        
        return self.members.pop(self.members.index(dead_member))

    def print_self(self):
        print("Population Information")
        print("======================")
        print("Size: {0}".format(self.N))
        for member in self.members:
            print("Fitness: {0}, Genome {1}".format(member.fitness, member.genome))
        print("======================")

""" An individual in a population with a mean fitness and array of loci with possible mutations """
class Member:
    # create a member with an unmutated genome
    def __init__(self, loci):
        self.loci = loci
        self.genome = [None for i in range(loci)]
        self.fitness = 1.0

    # update the count of every mutation in this member's genome (due to birth/death)
    def change_mutation_counts(self, delta):
        for i in range(self.loci):
            if self.genome[i] is not None:
                mutations[self.genome[i]].update_current(delta)

    def print_self(self, message=None):
        print("{0} Loci: {1}, Fitness: {2}, Genome:{3}".format(message, self.loci, self.fitness, self.genome))

""" 
A mutation for a specific locus in a genome 

@inception  time of creation
@locus      index of locus in the genome
@fitness    fitness of the new mutation
@current    current count in population
@alive      whether any individual has this mutation
@count      array of counts across time
"""
class Mutation:
    def __init__(self, inception, locus, fitness=None, current=0, parent=None):
        if fitness is None:
            self.fitness = 1 + np.random.normal(0, 1)
        else:
            self.fitness = fitness
        self.inception = inception
        self.locus = locus
        self.alive = True
        self.count = []
        self.current = current
        self.parent = parent

    # update the value and mark it as dead if no one has the mutation
    def update_current(self, delta):
        if self.current + delta > POP_SIZE:
            print("ERROR TOO HIGH, current: {0}, change: {1}, history: {2}".format(self.current, delta, self.count[-10:]))
        self.current += delta
        if self.current <= 0:
            self.alive = False

    def time_step(self):
        self.count.append(self.current)

    def print_self(self):
        print("Fitness: {0:+2.2f}, Inception: {1:4.0f}, Alive: {2:1b}, Current: {3:4.0f}, Parent: {4}, Locus: {5}".format(
            self.fitness, self.inception, self.alive, self.current, self.parent, self.locus))

""" Evoluation a population instance through a specific amount of time, record the mutation that develop """
def evolve_population(pop, time):
    for i in range(time):
        child = pop.reproduce("weighted-random")
        total_fitness = 0

        for j in range(child.loci):
            if mutation_occurs(mutation_rate):
                mutation = Mutation(inception=i, locus=j, parent=child.genome[j])
                mutations.append(mutation)
                child.genome[j] = mutations.index(mutation)
                total_fitness += mutation.fitness
            elif child.genome[j] is not None:
                total_fitness += mutations[child.genome[j]].fitness
            else:
                total_fitness += 1
        child.fitness = total_fitness / child.loci
        
        pop.death("uniform-random").change_mutation_counts(-1)
        child.change_mutation_counts(1)
        pop.members.append(child)
        
        for mutation in mutations:
            if mutation.alive:
                mutation.time_step()

""" Randomly decide whether a mutation occurs """
def mutation_occurs(mutation_rate):
    return bool(np.random.choice([0, 1], 1, True, [1 - mutation_rate, mutation_rate]))

""" Create a muller plot of the mutations that had adbunance of at least the cutoff at some time """
def plot_mutation_evolution(mutations, time, colorscale=False, cutoff=0.5, lines=False):
    long_lived_mutations = []
    for mutation in mutations:
        if max(mutation.count) > cutoff * POP_SIZE:
            # mutation.print_self()
            mutation.count = [0 for i in range(mutation.inception)] + mutation.count
            diff = len(time) - len(mutation.count)
            if diff != 0:
                mutation.count = mutation.count + [0 for i in range(diff)]
            long_lived_mutations.append(mutation)
    counts = np.array([np.divide(mutation.count, POP_SIZE) for mutation in long_lived_mutations])
    fitnesses = np.array([round(mutation.fitness, 2) for mutation in long_lived_mutations])
    labels = np.array([r"$s$:{0}, locus:{1}".format(round(mutation.fitness - 1, 2), mutation.locus) for mutation in long_lived_mutations])

    if len(long_lived_mutations) == 0:
        print("No mutations under conditions of given cutoff")
        return

    if lines:
        for i in range(len(counts)):
            plt.plot(time, counts[i], label=labels[i], linewidth=0.5)
    else:
        # plt.ylim((-POP_SIZE / 2, POP_SIZE / 2))
        ax = plt.gca()
        ax.set_facecolor("xkcd:sky blue")
        if colorscale:
            cmap = plt.cm.rainbow
            norm = colours.Normalize(vmin=min(fitnesses), vmax=max(fitnesses))
            sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
            plt.colorbar(sm)
            plt.stackplot(time, counts, baseline="sym", labels=fitnesses, colors=cmap(norm(fitnesses)))
        else:
            plt.stackplot(time, counts, baseline="sym", labels=labels)

    plt.ylabel("Mutation Frequency")
    plt.xlim((0, GENERATIONS))
    plt.xlabel("Time")
    plt.legend(loc="upper left", ncol=2, fontsize='xx-small')

    plt.show()

GENERATIONS = 10000
POP_SIZE = 200
LOCI = 2
mutations = []
mutation_rate = 50 / GENERATIONS

def main():
    pop = Population(POP_SIZE, LOCI)
    evolve_population(pop, GENERATIONS)
    plot_mutation_evolution(mutations, range(GENERATIONS), colorscale=True, cutoff=0.05)

if __name__ == "__main__":
    main()
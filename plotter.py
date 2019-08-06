import matplotlib.pyplot as plt
import numpy as np

def main():
    kinds = ["absfitness", "migration"]
    values = [[0.1, 0.5, 1, 2, 10], [1, 2, 10, 20]]
    for i in range(len(kinds)):
        for j in range(len(values[i])):            
            with open("../results/" + kinds[i] + "_" + str(values[i][j]) + ".txt") as f:
                results = [[float(x) for x in line.replace("\n", "").split(",")] for line in f.readlines()]
            demes, probs = [], []
            for result in sorted(results):
                demes.append(result[0])
                probs.append(result[2])
            plt.plot(demes, probs, label=values[i][j])
        plt.title(kinds[i])
        plt.legend(loc="best")
        plt.show()

if __name__ == "__main__":
    main()
import matplotlib.pyplot as plt
import numpy as np

titles = {
    "absfitness": "Fixation for varying absolute fitnesses",
    "migration": "Fixation for varying numbers of migrants"
}

labels = {
    "absfitness": r"$s$ = ",
    "migration": r"$m$ = "
}

def main():
    for file in ["new_s_0.1.txt", "absfitness_0.1.txt"]:
        with open("../results/" + file) as f:
            results = [[float(x) for x in line.replace("\n", "").split(",")] for line in f.readlines()]
        demes, probs = [], []
        for result in sorted(results):
            demes.append(result[0])
            probs.append(result[2])     
        plt.plot(demes, probs)
    plt.xlabel(r"$M$, Number of Demes")
    plt.grid(b=True, which="both")
    plt.ylabel("Fixation Probability")

    M = [1, 2, 4, 5, 8, 10, 20, 40, 50, 80, 100]
    pfix = [fix_from_M(m) for m in M]
    plt.plot(M, pfix)
    plt.show()
    return
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
            plt.plot(demes, probs, label=labels[kinds[i]] + str(values[i][j]))
        plt.title(titles[kinds[i]])
        plt.legend(loc="best")
        plt.xlabel(r"$M$, Number of Demes")
        plt.grid(b=True, which="both")
        plt.ylim((0, 1))
        plt.ylabel("Fixation Probability")
        plt.show()

def fix_from_M(M, a=0.001, b=0.0002):
    return 1 - (a*(1-b)*(M - 1) / ((1-a)*b))

if __name__ == "__main__":
    main()
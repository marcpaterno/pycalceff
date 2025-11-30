import random

with open("data.txt", "w") as f:
    for _ in range(0, 1000):
        ntrials = random.randint(1, 1000 * 1000)
        k = random.randint(0, ntrials)
        f.write(f"{k} {ntrials}\n")

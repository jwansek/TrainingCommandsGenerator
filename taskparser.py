with open("tasks.csv", "r") as f:
    tasks = f.read().split("\n")

for l in tasks:
    print(len(l.split("\t")))
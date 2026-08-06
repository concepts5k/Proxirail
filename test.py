from pathlib import Path

p = Path(__file__).resolve()
print(p)
for i in range(4):
    print(i, p.parents[i])
    
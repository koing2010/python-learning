from matplotlib import pyplot as plt
import numpy as np

x = np.linspace(1, 100, 20)
y = x * 2 + 3
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
ax.scatter(x, y)
plt.ion()
for i in range(100):
    y = x * i * 0.1 + i
    try:
        ax.lines.remove(lines[0])
    except Exception:
        pass
    lines = ax.plot(x, y)
    plt.pause(0.1)

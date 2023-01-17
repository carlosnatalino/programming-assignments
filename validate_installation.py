# these imports help us validate that the installation was correct
import time
import random
import matplotlib.pyplot as plt

numbers = []
for i in range(100):
    if i < 50:
        numbers.append(random.randint(0, 10))
    else:
        numbers.append(random.randint(10, 20))

plt.figure()
plt.title("If you see this, your installation was successful!")
plt.plot(numbers)
plt.show()
plt.close()

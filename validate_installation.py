# these imports help us validate that the installation was correct
import datetime
import getpass
import os
import platform
import random

import matplotlib.pyplot as plt

numbers = []
for i in range(100):
    if i < 50:
        numbers.append(random.randint(0, 10))
    else:
        numbers.append(random.randint(10, 20))

plt.figure()
plt.title(
    f"""If you see this, your installation was successful!
    Date: {datetime.datetime.now()}
    Folder: {os.getcwd()}
    User: {getpass.getuser()}
    OS: {platform.platform()}"""
)
plt.plot(numbers)
plt.tight_layout()
plt.show()
plt.close()

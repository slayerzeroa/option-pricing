import pandas as pd
import matplotlib.pyplot as plt


data = pd.read_csv('cpp/hedge_path.csv', header=None, names=['Hedge Path'])

print(data)

plt.plot(data)
plt.show()
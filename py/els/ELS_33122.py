import numpy as np
import scipy.stats as stat
import matplotlib.pyplot as plt


# TARGET ELS : 미래에셋증권 33122번 ELS
issue_price = 10000
S0_AMD = 101.86      # 6월 1일 기준
S0_NVD = 186.72      # 6월 1일 기준
sigma_AMD = 0.6717        # AMD 변동성
sigma_NVD = 0.6877        # NVD 변동성
cor = 0.825             # AMD NVD 상관계수
mu = 0.01759     # 6월 1일 KOFR 기준
T = 3           # 기간
L = 1200        # 자르기
dt = T/L
Pair_Price = 8274.15        # 공정가치

N1 = 10
N2 = 100
N3 = 500
N4 = 1000
N5 = 5000
N6 = 10000
N7 = 30000          # 반복횟수


def biasset_path(S0_1, S0_2, mu, sigma_1, sigma_2, T, L, cor):
    Spath_1 = np.zeros(L+1)
    Spath_2 = np.zeros(L+1)
    Spath_1[0] = S0_1
    Spath_2[0] = S0_2
    for i in range(1, L+1):
        z_1 = np.random.standard_normal()
        z_2 = np.random.standard_normal()
        z_2 = z_1*cor+z_2*np.sqrt(1-cor**2)
        Spath_1[i] = Spath_1[i-1] * np.exp((mu-0.5*sigma_1**2)*dt + sigma_1*np.sqrt(dt)*z_1)
        Spath_2[i] = Spath_2[i-1] * np.exp((mu-0.5*sigma_2**2)*dt + sigma_2*np.sqrt(dt)*z_2)
    return Spath_1, Spath_2

def option_pricing(asset1_sheet, asset2_sheet, S0_1, S0_2, issue_price, N):     # 옵션 프라이싱 함수
    NPV = []
    for i in range(N):
        if asset1_sheet[i, 200] >= S0_1 * 0.85 and asset2_sheet[i, 200] >= S0_2 * 0.85:  # 만약 1차 조기상환이 된다면
            NPV.append(1.1115 * issue_price * np.exp(-1/2*mu))
        elif asset1_sheet[i, 400] >= S0_1 * 0.85 and asset2_sheet[i, 400] >= S0_2 * 0.85:  # 만약 2차 조기상환이 된다면
            NPV.append(1.2230* issue_price * np.exp(-1*mu))
        elif asset1_sheet[i, 600] >= S0_1 * 0.85 and asset2_sheet[i, 600] >= S0_2 * 0.85:  # 만약 3차 조기상환이 된다면
            NPV.append(1.3345* issue_price * np.exp(-3/2*mu))
        elif asset1_sheet[i, 800] >= S0_1 * 0.85 and asset2_sheet[i, 800] >= S0_2 * 0.85:  # 만약 4차 조기상환이 된다면
            NPV.append(1.4460* issue_price * np.exp(-2*mu))
        elif asset1_sheet[i, 1000] >= S0_1 * 0.80 and asset2_sheet[i, 1000] >= S0_2 * 0.80:  # 만약 5차 조기상환이 된다면
            NPV.append(1.5575* issue_price * np.exp(-5/2*mu))
        elif asset1_sheet[i, 1200] >= S0_1 * 0.75 and asset2_sheet[i, 1200] >= S0_2 * 0.75:  # 만약 만기상환(1)이 된다면
            NPV.append(1.6690* issue_price * np.exp(-3*mu))
        elif np.any(asset1_sheet[i, :] < S0_1 * 0.45) == False and np.any(asset2_sheet[i, :] < S0_2 * 0.45) == False:  # 만약 만기상환(2)가 된다면
            NPV.append(1.6690* issue_price * np.exp(-3*mu))
        else:       # 다 안 되면
            NPV.append(min(asset1_sheet[i, 1200]/S0_1, asset2_sheet[i, 1200]/S0_2) * issue_price * np.exp(-3*mu))
    result = np.mean(NPV)
    return result

AMD_asset_sheet = None
NVD_asset_sheet = None

Iteration = [N1, N2, N3, N4, N5, N6, N7]
Predicted_Price = []

for j in Iteration:         # Iteration List
    for i in range(j):
        if i == 0:
            AMD_asset_sheet, NVD_asset_sheet = biasset_path(S0_AMD, S0_NVD, mu, sigma_AMD, sigma_NVD, T, L, cor)
        else:
            AMD_asset_path, NVD_asset_path = biasset_path(S0_AMD, S0_NVD, mu, sigma_AMD, sigma_NVD, T, L, cor)
            AMD_asset_sheet = np.vstack([AMD_asset_sheet, AMD_asset_path])
            NVD_asset_sheet = np.vstack([NVD_asset_sheet, NVD_asset_path])
    Predicted_Price.append(option_pricing(AMD_asset_sheet, NVD_asset_sheet, S0_AMD, S0_NVD, issue_price, j))


print("predicted prices are", Predicted_Price)

error_list = []
error_rate = []
for i in Predicted_Price:
    error_list.append(abs(i-Pair_Price))
    error_rate.append(abs(i-Pair_Price)/Pair_Price*100)
x = np.arange(len(Iteration))
plt.bar(x, error_list)
plt.xticks(x, Iteration)
plt.show()

print("errors are ", error_list)
print("error rates are", error_rate)

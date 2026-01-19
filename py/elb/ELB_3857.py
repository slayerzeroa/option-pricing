import numpy as np
import scipy.stats as stat
import matplotlib.pyplot as plt


# TARGET ELB : 미래에셋증권 3857번 ELB
issue_price = 10000
S0_KOSPI = 711.58      # 2026년 1월 19일 기준

sigma_KOSPI = 0.2987   # KOSPI200 변동성

mu = 0.02557     # 2026년 1월 19일 KOFR 기준
T = 1           # 기간
L = 250        # 자르기(영업일수)
dt = T/L
Pair_Price = 9857.55        # 공정가치

N1 = 10
N2 = 100
N3 = 500
N4 = 1000
N5 = 5000
N6 = 10000
N7 = 30000          # 반복횟수


def asset_path(S0_1, mu, sigma_1, T, L):
    Spath_1 = np.zeros(L+1)
    Spath_1[0] = S0_1
    for i in range(1, L+1):
        z_1 = np.random.standard_normal()
        Spath_1[i] = Spath_1[i-1] * np.exp((mu-0.5*sigma_1**2)*dt + sigma_1*np.sqrt(dt)*z_1)
    return Spath_1

def option_pricing(asset1_sheet, S0_1, issue_price, N):     # 옵션 프라이싱 함수
    NPV = []
    for i in range(N):
        # 1차 조건
        if asset1_sheet[i,:].any() > S0_1 * 1.15:
            NPV.append(1.015 * issue_price * np.exp(-1*mu))
        # 2차 조건
        elif asset1_sheet[i,-1] > S0_1 * 1.00 and asset1_sheet[i,-1] <= S0_1 * 1.15:
            NPV.append(asset1_sheet[i,-1]/S0_1 * issue_price * np.exp(-1*mu))
        # 3차 조건
        else:
            NPV.append(1.015 * issue_price * np.exp(-1*mu))

    result = np.mean(NPV)
    return result

KOSPI_asset_sheet = None

Iteration = [N1, N2, N3, N4, N5, N6, N7]
Predicted_Price = []

for j in Iteration:         # Iteration List
    for i in range(j):
        if i == 0:
            KOSPI_asset_sheet = asset_path(S0_KOSPI, mu, sigma_KOSPI, T, L)
        else:
            KOSPI_asset_path = asset_path(S0_KOSPI, mu, sigma_KOSPI, T, L)
            KOSPI_asset_sheet = np.vstack([KOSPI_asset_sheet, KOSPI_asset_path])
    Predicted_Price.append(option_pricing(KOSPI_asset_sheet,  S0_KOSPI, issue_price, j))


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

# import numpy as np
# import scipy.stats as stat
# import matplotlib.pyplot as plt


# seed = 12345
# np.random.seed(seed)

# # TARGET ELS : 미래에셋증권 35682 ELS
# # Three Asset ELS
# issue_price = 10000
# S0_SNP = 5995.54       # 2024년 11월 11일 기준
# S0_NVD = 147.63        # 2024년 11월 11일 기준
# S0_AMD = 147.95        # 2024년 11월 11일 기준
# sigma_SNP = 0.252         # SNP 변동성
# sigma_NVD = 0.6092        # NVD 변동성
# sigma_AMD = 0.7222        # AMD 변동성
# cor_SNP_NVD = 0.6473             # SNP NVD 상관계수
# cor_SNP_AMD = 0.5883             # SNP AMD 상관계수
# cor_NVD_AMD = 0.5804             # AMD NVD 상관계수

# mu = 0.03270    # 2024년 11월 11일 KOFR 기준
# T = 3           # 기간
# L = 252*3       # 자르기
# dt = T/L
# Pair_Price = 8185.04        # 공정가치

# N1 = 10
# N2 = 100
# N3 = 500
# N4 = 1000
# N5 = 5000
# N6 = 10000
# # N7 = 30000          # 반복횟수


# def triple_asset_path(S0_1, S0_2, S0_3, mu, sigma_1, sigma_2, sigma_3, T, L, corr_matrix):
#     Spath_1 = np.zeros(L+1)
#     Spath_2 = np.zeros(L+1)
#     Spath_3 = np.zeros(L+1)
#     Spath_1[0] = S0_1
#     Spath_2[0] = S0_2
#     Spath_3[0] = S0_3
#     for i in range(1, L+1):
#         z_1 = np.random.standard_normal()
#         z_2 = np.random.standard_normal()
#         z_3 = np.random.standard_normal()
#         z_2 = z_1*corr_matrix[1][0]+z_2*corr_matrix[1][1]
#         z_3 = z_1*corr_matrix[2][0]+z_2*corr_matrix[2][1]+z_3*corr_matrix[2][2]
#         Spath_1[i] = Spath_1[i-1] * np.exp((mu-0.5*sigma_1**2)*dt + sigma_1*np.sqrt(dt)*z_1)
#         Spath_2[i] = Spath_2[i-1] * np.exp((mu-0.5*sigma_2**2)*dt + sigma_2*np.sqrt(dt)*z_2)
#         Spath_3[i] = Spath_3[i-1] * np.exp((mu-0.5*sigma_3**2)*dt + sigma_3*np.sqrt(dt)*z_3)
#     return Spath_1, Spath_2, Spath_3


# def option_pricing(asset1_sheet, asset2_sheet, asset3_sheet, S0_1, S0_2, S0_3, issue_price, N):     # 옵션 프라이싱 함수
#     NPV = []
#     for i in range(N):
#         if asset1_sheet[i, 252] >= S0_1 * 0.85 and asset2_sheet[i, 252] >= S0_2 * 0.85 and asset3_sheet[i, 252] >= S0_3 * 0.85:  # 만약 1차 조기상환이 된다면
#             NPV.append(1.1140 * issue_price * np.exp(-1*mu))
#         if asset1_sheet[i, 252*2] >= S0_1 * 0.85 and asset2_sheet[i, 252*2] >= S0_2 * 0.85 and asset3_sheet[i, 252*2] >= S0_3 * 0.85:  # 만약 2차 조기상환이 된다면
#             NPV.append(1.1140 * issue_price * np.exp(-2*mu))
#         if asset1_sheet[i, 252*3] >= S0_1 * 0.75 and asset2_sheet[i, 252*3] >= S0_2 * 0.75 and asset3_sheet[i, 252*3] >= S0_3 * 0.75:  # 만약 만기상환이 된다면
#             NPV.append(1.1140 * issue_price * np.exp(-3*mu))
#         else:       # 다 안 되면
#             NPV.append(min((asset1_sheet[i, 252*3]/asset1_sheet[i, 0]-1) * issue_price * np.exp(-3*mu), (asset2_sheet[i, 252*3]/asset2_sheet[i, 0]-1) * issue_price * np.exp(-3*mu), (asset3_sheet[i, 252*3]/asset3_sheet[i, 0]-1) * issue_price * np.exp(-3*mu)))
#     result = np.mean(NPV)
#     return result



# corr_matrix = np.array([[1, cor_SNP_NVD, cor_SNP_AMD], [cor_SNP_NVD, 1, cor_NVD_AMD], [cor_SNP_AMD, cor_NVD_AMD, 1]])

# def choleski_decomposition(corr_matrix):
#     L = np.linalg.cholesky(corr_matrix)
#     return L


# choleski_matrix = choleski_decomposition(corr_matrix)

# print(choleski_matrix)


# SNP_asset_sheet = None
# NVD_asset_sheet = None
# AMD_asset_sheet = None


# iteration = [N1, N2, N3, N4, N5, N6]
# predicted_price = []

# for j in iteration:         # iteration List
#     for i in range(j):
#         if i == 0:
#             SNP_asset_sheet, AMD_asset_sheet, NVD_asset_sheet = triple_asset_path(S0_SNP, S0_NVD, S0_AMD, mu, sigma_SNP, sigma_NVD, sigma_AMD, T, L, corr_matrix)
#         else:
#             SNP_asset_path, AMD_asset_path, NVD_asset_path = triple_asset_path(S0_SNP, S0_NVD, S0_AMD, mu, sigma_SNP, sigma_NVD, sigma_AMD, T, L, corr_matrix)
#             SNP_asset_sheet = np.vstack([SNP_asset_sheet, SNP_asset_path])
#             NVD_asset_sheet = np.vstack([NVD_asset_sheet, NVD_asset_path])
#             AMD_asset_sheet = np.vstack([AMD_asset_sheet, AMD_asset_path])
#     predicted_price.append(option_pricing(SNP_asset_sheet, NVD_asset_sheet, AMD_asset_sheet, S0_SNP, S0_NVD, S0_AMD, issue_price, j))


# print("predicted prices are", predicted_price)

# error_list = []
# error_rate = []
# for i in predicted_price:
#     error_list.append(abs(i-Pair_Price))
#     error_rate.append(abs(i-Pair_Price)/Pair_Price*100)
# x = np.arange(len(iteration))
# plt.bar(x, error_list)
# plt.xticks(x, iteration)
# plt.show()

# print("errors are ", error_list)
# print("error rates are", error_rate)



import numpy as np
import scipy.stats as stat
import matplotlib.pyplot as plt
from multiprocessing import Pool, cpu_count

# 초기 설정
seed = 12345
np.random.seed(seed)

# TARGET ELS : 미래에셋증권 35682 ELS
issue_price = 10000
S0_SNP = 5995.54
S0_NVD = 147.63
S0_AMD = 147.95
sigma_SNP = 0.252
sigma_NVD = 0.6092
sigma_AMD = 0.7222
cor_SNP_NVD = 0.6473
cor_SNP_AMD = 0.5883
cor_NVD_AMD = 0.5804

mu = 0.03270
T = 3
L = 252 * 3
dt = T / L
Pair_Price = 8185.04

iteration = [10, 100, 500, 1000, 5000, 10000]  # 반복 횟수

# 상관행렬
corr_matrix = np.array([
    [1, cor_SNP_NVD, cor_SNP_AMD],
    [cor_SNP_NVD, 1, cor_NVD_AMD],
    [cor_SNP_AMD, cor_NVD_AMD, 1]
])

def triple_asset_path(S0_1, S0_2, S0_3, mu, sigma_1, sigma_2, sigma_3, T, L, corr_matrix):
    Spath_1 = np.zeros(L+1)
    Spath_2 = np.zeros(L+1)
    Spath_3 = np.zeros(L+1)
    Spath_1[0] = S0_1
    Spath_2[0] = S0_2
    Spath_3[0] = S0_3
    for i in range(1, L+1):
        z = np.random.multivariate_normal([0, 0, 0], corr_matrix)
        Spath_1[i] = Spath_1[i-1] * np.exp((mu - 0.5 * sigma_1**2) * dt + sigma_1 * np.sqrt(dt) * z[0])
        Spath_2[i] = Spath_2[i-1] * np.exp((mu - 0.5 * sigma_2**2) * dt + sigma_2 * np.sqrt(dt) * z[1])
        Spath_3[i] = Spath_3[i-1] * np.exp((mu - 0.5 * sigma_3**2) * dt + sigma_3 * np.sqrt(dt) * z[2])
    return Spath_1, Spath_2, Spath_3

def option_pricing(SNP_sheet, NVD_sheet, AMD_sheet, S0_1, S0_2, S0_3, issue_price):
    NPV = []
    for i in range(SNP_sheet.shape[0]):
        if SNP_sheet[i, 252] >= S0_1 * 0.85 and NVD_sheet[i, 252] >= S0_2 * 0.85 and AMD_sheet[i, 252] >= S0_3 * 0.85:
            NPV.append(1.1140 * issue_price * np.exp(-1 * mu))
        elif SNP_sheet[i, 252*2] >= S0_1 * 0.85 and NVD_sheet[i, 252*2] >= S0_2 * 0.85 and AMD_sheet[i, 252*2] >= S0_3 * 0.85:
            NPV.append(1.1140 * issue_price * np.exp(-2 * mu))
        elif SNP_sheet[i, 252*3] >= S0_1 * 0.75 and NVD_sheet[i, 252*3] >= S0_2 * 0.75 and AMD_sheet[i, 252*3] >= S0_3 * 0.75:
            NPV.append(1.1140 * issue_price * np.exp(-3 * mu))
        else:
            NPV.append(min(
                (SNP_sheet[i, 252*3] / S0_1 - 1) * issue_price * np.exp(-3 * mu),
                (NVD_sheet[i, 252*3] / S0_2 - 1) * issue_price * np.exp(-3 * mu),
                (AMD_sheet[i, 252*3] / S0_3 - 1) * issue_price * np.exp(-3 * mu)
            ))
    return np.mean(NPV)

# 병렬 작업을 위한 단일 프로세스 함수
def monte_carlo_simulation(N):
    SNP_sheets = []
    NVD_sheets = []
    AMD_sheets = []
    for _ in range(N):
        SNP_path, NVD_path, AMD_path = triple_asset_path(S0_SNP, S0_NVD, S0_AMD, mu, sigma_SNP, sigma_NVD, sigma_AMD, T, L, corr_matrix)
        SNP_sheets.append(SNP_path)
        NVD_sheets.append(NVD_path)
        AMD_sheets.append(AMD_path)
    SNP_sheets = np.array(SNP_sheets)
    NVD_sheets = np.array(NVD_sheets)
    AMD_sheets = np.array(AMD_sheets)
    return option_pricing(SNP_sheets, NVD_sheets, AMD_sheets, S0_SNP, S0_NVD, S0_AMD, issue_price)

# 병렬 처리
if __name__ == "__main__":
    predicted_prices = []

    for N in iteration:
        with Pool(processes=cpu_count()) as pool:
            # 각 프로세스에서 Monte Carlo 시뮬레이션 수행
            result = pool.map(monte_carlo_simulation, [N // cpu_count()] * cpu_count())
            # 결과 평균 계산
            predicted_prices.append(np.mean(result))

    # 결과 출력
    print("Predicted Prices:", predicted_prices)

    # 시각화
    error_list = [abs(p - Pair_Price) for p in predicted_prices]
    error_rate = [abs(p - Pair_Price) / Pair_Price * 100 for p in predicted_prices]

    # x = np.arange(len(iteration))
    # plt.bar(x, error_list)
    # plt.xticks(x, iteration)
    # plt.show()

    print("Errors:", error_list)
    print("Error Rates:", error_rate)

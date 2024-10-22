# 라이브러리 설치
# pip install -r requirements.txt

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import scipy.stats as stats
import time

import copy


# Simulation Setting
T = 1.0             # Time
N = 252             # The number of split
dt = T/N            # Delta time
sim = 1000          # The number of simulations

# Initial Value
S0 = 100.0          # Initial Stock Price
v0 = 0.25**2        # Initial Volatility

# Constants of Heston Process
ksi = 0.5           # Volatility of Volatility
kappa = 3           # Kappa; the rate at which νt reverts to θ.
theta = 0.2**2      # Theta;  the long variance, or long-run average variance of the price; as t tends to infinity, the expected value of νt tends to θ.
rho = -0.2          # Rho; the correlation of the two Wiener processes. (Returns <-> Volatility in this simulation)
mu = 0.02           # mu; Expected Returns

# Risk Free Rate
rf = 0.02
rf_daily = np.exp(rf/N) - 1

# Strike Price
K = 110




def heston_process(ksi, kappa, theta, rho, mu, return_vol=False, random_seed=21):
  '''
  ksi           # Ksi;   Volatility of Volatility
  kappa         # Kappa; The rate at which νt reverts to θ.
  theta         # Theta; The long variance, or long-run average variance of the price; as t tends to infinity, the expected value of νt tends to θ.
  rho           # Rho;   The correlation of the two Wiener processes. (Stock Price <-> Volatility in this simulation)
  mu            # Mu;    Expected Returns
  '''
  np.random.seed(random_seed)
  dt = T/N

  mean = np.array([0, 0])
  cov = np.array([[1,rho],
                  [rho, 1]])
  Z = np.random.multivariate_normal(mean, cov, (N, sim))

  S = np.zeros(shape=(N+1, sim))
  V = np.zeros(shape=(N+1, sim))

  S[0, :] = S0
  V[0, :] = v0

  for i in range(1, N+1):
    S[i] = S[i-1] * np.exp((mu-0.5*V[i-1])*dt+np.sqrt(V[i-1]*dt)*Z[i-1, :, 0])
    V[i] = np.maximum(V[i-1] + (kappa*(theta-V[i-1])*dt + ksi*np.sqrt(V[i-1] * dt)*Z[i-1, :, 1]), 0)

  if return_vol:
    return S, V

  return S



S, V = heston_process(ksi, kappa, theta, rho, mu, return_vol = True)


# S[-1]에서 K를 뺀 값이 Call Option의 Payoff
call_p = np.maximum(S[-1] - K, 0)
put_p = np.maximum(K - S[-1], 0)

# call_p가 0보다 작으면 0으로 만들어줌
call_p[call_p < 0] = 0
put_p[put_p < 0] = 0

# Option의 현재 가치
call_option_price = np.mean(call_p) / ((1 + rf_daily)**N)
put_option_price = np.mean(put_p) / ((1 + rf_daily)**N)


# Excel로 내보내기
export_S = copy.deepcopy(S)
export_S = pd.DataFrame(export_S)

export_S['option_price'] = None

export_S.loc[0, 'option_price'] = 'Call Option Price'
export_S.loc[1, 'option_price'] = call_option_price  
export_S.loc[2, 'option_price'] = 'Put Option Price'
export_S.loc[3, 'option_price'] = put_option_price

export_S.to_csv('export_S.csv', index=False)
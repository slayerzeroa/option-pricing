#include <iostream>
#include <random>
#include <vector>

using namespace std;

// Homework 3
// Write C++ code that calculates Call option and Put option using Monte Carlo Approach.
// Compare it with the formula for Black Scholes equation.
// You may use any value for risk-free rate and expiration date.

vector<double> generate_discrete_path(double rf, double sigma, int len);
vector<double> generate_continuous_path(double rf, double sigma, int len);

double calculate_payoff(vector<double> s, double k, int type);
double discount(double s, double rate, int len);
double mean(vector<double> array);


double norm_dist();

int main(){
    vector<double> stock_path;
    double rf, sigma, k;
    int len, m, type;
    double payoff, pv, result;
    cout << "Plese Enter the rf, sigma, and strike price" << endl;
    cin >> rf >> sigma >> k;

    cout << "Please Enter the expiration date, simulation number and option type(put==0, call==1)" << endl;
    cin >> len >> m >> type;

    result = 0;
    for (int i=0; i < m; i++){
        stock_path = generate_continuous_path(rf, sigma, len);
        payoff = calculate_payoff(stock_path, k, type);
        pv = discount(payoff, rf, len);
        result += pv;
    }
    result /= m;

    cout << "Option Price is " << result << endl;
}


vector<double> generate_discrete_path(double rf, double sigma, int len){
    vector<double> s(len);
    double st=100;
    double y;
    for (int i=0; i<len; ++i){
        s[i] = st;
        y = norm_dist();
        st = st + rf * st + sigma * y * st;

        // cout << y << endl;
    }
    return s;
}

vector<double> generate_continuous_path(double rf, double sigma, int len){
    vector<double> s(len);
    double st=100;
    double y;
    for (int i=0; i<len; ++i){
        s[i] = st;
        y = norm_dist();
        st = st * exp((rf - 0.5*pow(sigma, 2)) + sigma * y);

        // cout << y << endl;
    }
    return s;
}



// type: 0==put, 1==call
double calculate_payoff(vector<double> s, double k, int type) {
    if (type == 0) {
        if (s.back() < k) {
            return (k - s.back());
        } else {
            return 0;
        }
    } else if (type == 1) {
        if (s.back() > k) {
            return (s.back() - k);
        } else {
            return 0;
        }
    } else {
        cout << "Please select type 0 or 1 (0==put, 1==call)" << endl;
        return -1;
    }
}


double norm_dist(){
    std::default_random_engine generator(random_device{}());
    std::normal_distribution<double> distribution(0, 1);
    double num = distribution(generator);

    return num;
}

double discount(double s, double rate, int len) {
    return s * exp(-rate * len);
}


double mean(vector<double> array) {
    double sum = accumulate(array.begin(), array.end(), 0.0);
    double avg = sum / array.size();
    return avg;
}
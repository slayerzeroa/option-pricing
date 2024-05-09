#include <iostream>
#include <random>
#include <vector>

using namespace std;

// Homework 2
// Write C++ code that gives the path of the asset given its volatility σ and drift µ.

vector<double> generate_discrete_path(double mu, double sigma, int tau, double st);
vector<double> generate_continuous_path(double mu, double sigma, int tau, double st);
double norm_dist();

int main(){
    vector<double> stock_path;
    double mu, sigma, st;
    int tau;
    cout << "Plese Enter the mu, sigma and tau" << endl;
    cin >> mu >> sigma >> tau;
    cout << "Plese Enter the initial value of Stock" << endl;
    cin >> st;
    stock_path = generate_continuous_path(mu, sigma, tau, st);

    for (const double &value : stock_path) {
        cout << value << " ";
    }
    cout << endl;
}


vector<double> generate_discrete_path(double mu, double sigma, int tau, double st){
    vector<double> s(tau);
    double y;
    for (int i=0; i<tau; ++i){
        s[i] = st;
        y = norm_dist();
        st = st + mu * st + sigma * y * st;

        // cout << y << endl;
    }
    return s;
}

vector<double> generate_continuous_path(double mu, double sigma, int tau, double st){
    vector<double> s(tau);
    double y;
    for (int i=0; i<tau; ++i){
        s[i] = st;
        y = norm_dist();
        st = st * exp((mu - 0.5*pow(sigma, 2)) + sigma * y);

        // cout << y << endl;
    }
    return s;
}


double norm_dist(){
    std::default_random_engine generator(random_device{}());
    std::normal_distribution<double> distribution(0, 1);
    double num = distribution(generator);

    return num;
}



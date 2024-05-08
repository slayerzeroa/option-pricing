#include <iostream>
#include <random>
#include <vector>

using namespace std;

// Homework 2
// Write C++ code that gives the path of the asset given its volatility σ and drift µ.


vector<double> generate_discrete_path(double mu, double sigma, int len);
vector<double> generate_continuous_path(double mu, double sigma, int len);

double norm_dist();

int main(){
    vector<double> stock_path;
    double mu, sigma;
    int len;
    cout << "Plese Enter the mu, sigma and length" << endl;
    cin >> mu >> sigma >> len;
    stock_path = generate_continuous_path(mu, sigma, len);

        // Correct way to print the elements of a vector
    for (const double &value : stock_path) {
        cout << value << " ";
    }
    cout << endl;
}


vector<double> generate_discrete_path(double mu, double sigma, int len){
    vector<double> s(len);
    double st=100;
    double y;
    for (int i=0; i<len; ++i){
        s[i] = st;
        y = norm_dist();
        st = st + mu * st + sigma * y * st;

        // cout << y << endl;
    }
    return s;
}

vector<double> generate_continuous_path(double mu, double sigma, int len){
    vector<double> s(len);
    double st=100;
    double y;
    for (int i=0; i<len; ++i){
        s[i] = st;
        y = norm_dist();
        st = st * exp((mu - pow(0.5*sigma, 2)) + sigma * y);

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



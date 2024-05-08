#include <iostream>
#include <random>
#include <vector>
#include <fstream>

using namespace std;

// Homework 4
// Given asset path, use delta hedging for call option and visualize the result (save as an image file).

vector<double> generate_discrete_path(double mu, double sigma, int len);
vector<double> generate_continuous_path(double mu, double sigma, int len);

double calculate_payoff(vector<double> s, double k, int type);
double discount(double s, double rate, int len);
double mean(vector<double> array);


double normalCDF(double value);
double calD1(double s, double k, double mu, double sigma, int tau);
double norm_dist();

// to csv
void saveToCSV(const vector<double>& data, const string& filename);


vector<double> deltaHedge(double s, double k, double mu, double sigma, int tau);

int main(){
    vector<double> stock_path;
    double mu, sigma, rf, k;
    int len, m, type;
    double payoff, pv, result;
    cout << "Plese Enter the mu, sigma, and strike price" << endl;
    cin >> mu >> sigma >> k;

    cout << "Please Enter the expiration date, simulation number and option type(put==0, call==1)" << endl;
    cin >> len >> m >> type;

    stock_path = deltaHedge(100, k, mu, sigma, len);
    // Correct way to print the elements of a vector
    for (const double &value : stock_path) {
        cout << value << " ";
    }
    cout << endl;
    saveToCSV(stock_path, "C:/Users/slaye/VscodeProjects/Option_Pricing_Practice/cpp/hedge_path.csv");

    // result = 0;
    // for (int i; i < m; i++){
    //     stock_path = generate_continuous_path(mu, sigma, len);
    //     payoff = calculate_payoff(stock_path, k, type);
    //     pv = discount(payoff, mu, len);
    //     result += pv;
    // }
    // result /= m;
    

    // cout << "Option Price is " << result << endl;
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


double normalCDF(double value){
    return 0.5 * erfc(-value * sqrt(0.5));
}

double calD1(double s, double k, double mu, double sigma, int tau){
    return ((log(s/k) + (mu + 0.5*pow(sigma, 2))*tau)/(sigma*sqrt(tau)));
}

vector<double> deltaHedge(double s, double k, double mu, double sigma, int tau){
    double a0, a1, d, phi, y;
    vector<double> hPath(tau);

    a0 = normalCDF(calD1(s, k, mu, sigma, tau));

    d = 1.0;
    phi = a0*s + d;

    for (int i=0; i < tau; i++) {
        cout << "a: " << a0 << endl;
        cout << "phi: " << phi << endl;
        hPath[i] = phi;
        y = norm_dist();
        s = s * exp((mu - pow(0.5*sigma, 2)) + sigma * y);
        phi = a0*s + d;
        a1 = normalCDF(calD1(s, k, mu, sigma, tau));
        d = (1+mu)*d + (a0 - a1)*s;
        a0 = normalCDF(calD1(s, k, mu, sigma, tau));
    }
    return hPath;
}


// to csv

void saveToCSV(const vector<double>& data, const string& filename){
    ofstream outFile(filename);
    for (const auto& value : data){
        outFile << value << endl;
    }
    outFile.close();
}
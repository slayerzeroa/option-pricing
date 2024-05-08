#include <iostream>
#include <random>

// Homework 1
// Write C++ code such that it uses <random> library for uniform distribution
// function and generate normal distribution.

double norm_dist(double mean, double std);
double uni_dist(double lower, double upper);

int main(){
    double mean, std, lower, upper;

    std::cout << "Enter mean and std dev for normal distribution: ";
    std::cin >> mean >> std;
    std::cout << "Enter lower and upper bounds for uniform distribution: ";
    std::cin >> lower >> upper;

    double normal_num = norm_dist(mean, std);
    double uniform_num = uni_dist(lower, upper);

    std::cout << "normal distribution:" << normal_num << std::endl;
    std::cout << "uniform distribution:" << uniform_num << std::endl;
}

double norm_dist(double mean, double std){
    std::default_random_engine generator(std::random_device{}());
    std::normal_distribution<double> distribution(mean, std);
    double num = distribution(generator);

    return num;
}

double uni_dist(double lower, double upper){
    std::default_random_engine generator(std::random_device{}());
    std::uniform_real_distribution<double> distribution(lower, upper);
    double num = distribution(generator);

    return num;
}
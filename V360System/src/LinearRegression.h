// This is adapted from:
// https://www.analyticsvidhya.com/blog/2020/04/machine-learning-using-c-linear-logistic-regression/

/*
 * LinearRegression.h
 *
 *  Created on: Sep 15, 2021
 *      Author: cbothra
 */

#include <utility>
#include <vector>

class LinearRegression {
 public:
  /* this custom sort function is defined to
  sort on basis of min absolute value or error*/

  bool custom_sort(double a, double b) {
    double a1 = abs(a - 0);
    double b1 = abs(b - 0);
    return a1 < b1;
  }

  static constexpr size_t HW = 13;
  static constexpr size_t PW = 25;
  static constexpr float lower_bound = 1e-5;

  size_t hw_{HW};
  size_t pw_{PW};

  float yawInput[HW];
  float pitchInput[HW];
  float timeSampleInput[HW];

  std::vector<float> yawError;  // for storing the yaw error values
  float yawErr;                 // for calculating yaw error on each stage
  float yawB0 = 0;              // initializing yaw b0
  float yawB1 = 0;              // initializing yaw b1
  float yawAlpha = 0.01;        // initializing our learning rate

  std::vector<float> pitchError;  // for storing the pitch error values
  float pitchErr;                 // for calculating pitch error on each stage
  float pitchB0 = 0.0;            // initializing pitch b0
  float pitchB1 = 0.0;            // initializing pitch b1
  float pitchAlpha = 0.01;        // initializing our learning rate

  float e = 2.71828;

  std::vector<std::pair<float, float>> lrPredictions;

  std::vector<std::pair<float, float>> Model(
      std::vector<std::pair<float, float>> input, int length);
};

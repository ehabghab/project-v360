// This is adapted from:
// https://www.analyticsvidhya.com/blog/2020/04/machine-learning-using-c-linear-logistic-regression/

/*
 * LinearRegression.h
 *
 *  Created on: Sep 15, 2021
 *      Author: cbothra
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#include <vector>

class LinearRegression {
private:
  static constexpr size_t kHW = 13;
  static constexpr size_t kPW = 25;
  static constexpr float kLowerBound_ = 1e-5;
  static constexpr float kYawAlpha_ = 0.01;   // initializing our learning rate
  static constexpr float kPitchAlpha_ = 0.01; // initializing our learning rate

  // ToDo initialize with slope function.

  float pitchB0; // initializing pitch b0
  float pitchB1; // initializing pitch b1
  float yawB0;
  float yawB1;
  bool initalized = false;

  size_t hw_{kHW};
  size_t pw_{kPW};

  float yawInput_[kHW];
  float pitchInput_[kHW];
  float timeSampleInput_[kHW];

  void init(std::vector<std::pair<float, float>> &input);

  FILE *predictionLog_;

public:
  std::vector<std::pair<float, float>>
  predict(std::vector<std::pair<float, float>> &input, int length);
};

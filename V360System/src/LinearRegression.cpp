/*
 * LinearRegression.cpp
 *
 *  Created on: Sep 15, 2021
 *      Author: cbothra
 */
#include "LinearRegression.h"

#include<iostream>

std::vector<std::pair<float, float>> LinearRegression::predict(
    std::vector<std::pair<float, float>>& input, int length) {
  std::vector<std::pair<float, float>> lrPredictions;
  std::vector<float> pitchError;  // for storing the pitch error values
  std::vector<float> yawError;    // for storing the yaw error values

  /*Intialization Phase*/
  for (size_t i = 0; i < hw_; i++) {
    // Assuming the ground truth is [1,2,3,4,5,6] with 6 being most recent.
    yawInput_[hw_ - i] = input[length - i].first;
    pitchInput_[hw_ - i] = input[length - i].second;
    timeSampleInput_[i] = i;
  }
  
  /*Training Phase*/
  // Since there are {hw_} values in our dataset and we want to run for 4*HW
  // epochs.
  int idx;
  float pred;
  float yawErr;
  for (int i = 0; i < (4 * hw_); i++) {
    idx = i % 10;  // for accessing index after every epoch
    pred = yawB0 + yawB1 * timeSampleInput_[idx];  // making the prediction
    yawErr = pred - yawInput_[idx];                // calculating the error
    yawB0 = yawB0 - kYawAlpha_ * yawErr;           // updating b0
    yawB1 = yawB1 - kYawAlpha_ * yawErr * timeSampleInput_[idx];  // updating b1
    if (yawB1 < kLowerBound_) yawB1 = 0;
    if (yawB0 < kLowerBound_) yawB0 = 0;
    yawError.push_back(yawErr);
  }

  float pitchErr;       // for calculating pitch error on each stage
  for (int i = 0; i < (4 * hw_); i++) {
    idx = i % 10;  // for accessing index after every epoch
    pred = pitchB0 + pitchB1 * timeSampleInput_[idx];  // making the prediction
    pitchErr = pred - pitchInput_[idx];                // calculating the error
    pitchB0 = pitchB0 - kPitchAlpha_ * pitchErr;       // updating b0
    pitchB1 = pitchB1 -
              kPitchAlpha_ * pitchErr * timeSampleInput_[idx];  // updating b1
    if (pitchB1 < kLowerBound_) pitchB1 = 0;
    if (pitchB0 < kLowerBound_) pitchB0 = 0;
    pitchError.push_back(pitchErr);
  }

  for (size_t i = 1; i <= pw_; i++) {
    float predYaw = yawB0 + yawB1 * i;
    float predPitch = pitchB0 + pitchB1 * i;

    if (predYaw > 360) predYaw -= int(predYaw / 360) * 360;
    if (predPitch > 180) predPitch -= int(predPitch / 180) * 180;

    lrPredictions.push_back(std::make_pair(predYaw, predPitch));
  }

  return lrPredictions;
}

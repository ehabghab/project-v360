/*
 * LinearRegression.cpp
 *
 *  Created on: Sep 15, 2021
 *      Author: cbothra
 */
#include "LinearRegression.h"
#include <iostream>
#include <vector>

using std::cout; using std::cin;
using std::endl; using std::string;
using std::vector; using std::pair;
using std::make_pair;

std::vector<std::pair<float, float>> LinearRegression::Model(std::vector<std::pair<float, float>> input){
	
	size_t length = input.size();
	
	/*Intialization Phase*/
	for (size_t i = 1; i<hw_; i++) {
		
		//Assuming the ground truth is [1,2,3,4,5,6] with 6 being most recent.
		yawInput[hw_-i] = input[length-i].first;
		pitchInput[hw_-i] = input[length-i].second;
		timeSampleInput[i] = i;
	}
			 	  
	/*Training Phase*/
	//Since there are {hw_} values in our dataset and we want to run for 4*HW epochs.
	
	for (int i = 0; i < (4*hw_); i ++) {
		int idx = i % 10;   //for accessing index after every epoch
		float pred = yawB0 + yawB1 * timeSampleInput[idx]; //making the prediction
		yawErr = pred - yawInput[idx];  //calculating the error
		yawB0 = yawB0 - yawAlpha * yawErr;   //updating b0
		yawB1 = yawB1 - yawAlpha * yawErr * timeSampleInput[idx];//updating b1
		if (yawB1 < lower_bound)
			yawB1 = 0;
		if (yawB0 < lower_bound)
			yawB0 = 0;
		yawError.push_back(yawErr);
	}
	
	for (int i = 0; i < (4*hw_); i ++) {
		int idx = i % 10;   //for accessing index after every epoch
		float pred = pitchB0 + pitchB1 * timeSampleInput[idx]; //making the prediction
		pitchErr = pred - pitchInput[idx];  //calculating the error
		pitchB0 = pitchB0 - pitchAlpha * pitchErr;   //updating b0
		pitchB1 = pitchB1 - pitchAlpha * pitchErr * timeSampleInput[idx];//updating b1
		if (pitchB1 < lower_bound)
			pitchB1 = 0;
		if (pitchB0 < lower_bound)
			pitchB0 = 0;
		pitchError.push_back(pitchErr);
	}
	
	for (size_t i=1; i<=pw_; i++) {
		float predYaw = yawB0 + yawB1 * i;
		float predPitch = pitchB0 + pitchB1 *i;
		lrPredictions.push_back(std::make_pair(predYaw, predPitch));
	}
	
	return lrPredictions;
}


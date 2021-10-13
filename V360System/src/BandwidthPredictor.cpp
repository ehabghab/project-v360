/*
 * BandwidthPredictor.cpp
 *
 *  Created on: Jun 2, 2021
 *      Author: eghabash
 */

#include "BandwidthPredictor.h"

#include <cmath>
#include <iostream>


BandwidthPredictor::BandwidthPredictor() {
	bandwidthSum_ = 0.0;
	numOfChunks_ = 0;
	avgBandwidths_ = { };
}

void BandwidthPredictor::addTileBandwidth(float bandwidth) {
	if (std::isinf(bandwidth))
	{
		return;		
	}
	bandwidthMutex_.lock();
	bandwidthSum_+= bandwidth;
	numOfChunks_++;
	bandwidthMutex_.unlock();
}

std::pair<int,float> BandwidthPredictor::getAvgDownloadTime() {

	//get the average of bandwidth for all received so far.
	//then empty the downloadTime_;

	// TODO store sum, num.

	bandwidthMutex_.lock();
	std::pair<int,float> avgParameters = {numOfChunks_,bandwidthSum_};
	bandwidthSum_ = 0.0;
	numOfChunks_ = 0;
	bandwidthMutex_.unlock();
	return avgParameters;
}

float BandwidthPredictor::getMpcBandwidthPrediction() {


	//ToDo return mpc avg.

	avgBandwidths_.push_back(getAvgDownloadTime());
	int timeStartIdx = avgBandwidths_.size() < 50 ? 0 : avgBandwidths_.size() - 50;
	float predictedBandwidthSum = 0;
	int totalNumOfChunks = 0;
	for(timeStartIdx; timeStartIdx < avgBandwidths_.size() ; timeStartIdx++) {

		predictedBandwidthSum += avgBandwidths_[timeStartIdx].second;
		totalNumOfChunks += avgBandwidths_[timeStartIdx].first;
	}
	return predictedBandwidthSum/totalNumOfChunks;
}


BandwidthPredictor::~BandwidthPredictor() {

}

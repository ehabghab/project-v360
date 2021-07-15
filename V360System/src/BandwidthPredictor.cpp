/*
 * BandwidthPredictor.cpp
 *
 *  Created on: Jun 2, 2021
 *      Author: eghabash
 */

#include "BandwidthPredictor.h"

BandwidthPredictor::BandwidthPredictor() {
	bandwidthSum_ = 0.0;
	numOfChunks_ = 0;
	avgBandwidths_ = { };
}

void BandwidthPredictor::addTileBandwidth(float bandwidth) {
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
	int timeEndIdx = avgBandwidths_.size() - 50 < 0 ? 0 : avgBandwidths_.size() - 50;
	float predictedBandwidthSum = 0;
	int totalNumOfChunks = 0;
	for(int timeIdx = avgBandwidths_.size()-1; timeIdx > timeEndIdx - 1; timeIdx++) {
		predictedBandwidthSum += avgBandwidths_[timeIdx].first * avgBandwidths_[timeIdx].second;
		totalNumOfChunks += avgBandwidths_[timeIdx].first;
	}

	//TODO: check?
	return predictedBandwidthSum/totalNumOfChunks;
}


BandwidthPredictor::~BandwidthPredictor() {

}

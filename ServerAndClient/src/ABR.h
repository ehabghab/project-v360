/*
 * ABR.h
 *
 *  Created on: May 5, 2021
 *      Author: eghabash
 */

#ifndef ABR_H_
#define ABR_H_

#include <vector>
#include <map>

#include "ClientNetworkLayer.h"

class ABR {

	std::vector<std::pair<float,float>> vpGroundTruth_;

	std::vector<std::pair<float,float>> vpPredictions_;

	std::vector<std::pair<float,float>> bwGroundTruth_;

	std::vector<std::pair<float,float>> bwPredictions_;

	std::map<std::pair<int,int>,float> tileSizes_;

	static void run(ABR* abr, ClientNetworkLayer* clientNetworkLayer);

public:



	ABR();

	virtual ~ABR();
};

#endif /* ABR_H_ */

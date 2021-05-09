/*
 * ABR.cpp
 *
 *  Created on: May 5, 2021
 *      Author: eghabash
 */

#include "ABR.h"

#include <thread>

void ABR::run(ABR* abr, ClientNetworkLayer* clientNetworkLayer)
{

	long stime;
	long etime;

	float tileSec = 1;

	while(true)
	{

		stime = std::chrono::duration_cast<std::chrono::milliseconds>
		(std::chrono::system_clock::now().time_since_epoch()).count();

		// do prediction using bw, tilesizes, and current location.
		//first find tiles needed


		etime = std::chrono::duration_cast<std::chrono::milliseconds>
		(std::chrono::system_clock::now().time_since_epoch()).count();

		//sleep for 100ms
		std::this_thread::sleep_for(std::chrono::milliseconds((stime + 100) - etime));
		tileSec += .1;


	}


}

ABR::ABR() {


}

ABR::~ABR() {
	// TODO Auto-generated destructor stub
}


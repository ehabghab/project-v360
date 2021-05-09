/*
 * VideoPlayer.cpp
 *
 *  Created on: May 1, 2021
 *      Author: eghabash
 */

#include "VideoPlayer.h"

#include <stdio.h>

#include <chrono>
#include <iostream>
#include <string>
#include <thread>

#include <boost/algorithm/string/regex.hpp>
#include <boost/algorithm/string.hpp>


VideoPlayer::VideoPlayer(Decoder* decoder) {
	// TODO Auto-generated constructor stub

	//read ground truth.
	std::string tracePath = "/Users/eghabash/Desktop/360 Video/Project-V360"
			"/split/tiles_per_frame_user_3.txt";
	std::ifstream infile(tracePath);

	std::string line;
	int pos;
	uint32_t sec;
	std::string tiles;
	std::vector<std::string> tilesVec;

	while (std::getline(infile, line))
	{

		pos = line.find(":");
		sec = static_cast<uint32_t>(std::stoi(line.substr(0,pos)));
		tiles = line.substr(pos+2,line.size()-(pos+3));

		boost::algorithm::split(tilesVec, tiles, boost::is_any_of(","));
		std::vector<uint16_t> t;
		for(auto& tile : tilesVec)
		{
			t.push_back(static_cast<uint16_t>(stoi(tile)));
		}
		groundTruth_.insert(std::pair<uint32_t, std::vector<uint16_t>>(sec,t));

	}
	frameId_ = 1;
	FPS_ = 25;
	decoder_ = decoder;


}

void VideoPlayer::addChunk(uint8_t* chunkPointer, uint32_t chunkSize, std::string tileIndex)
{
	// tileIndex == /<tile index>/<presentation time>.h264

	std::vector<std::string> tileInfo;

	boost::algorithm::split_regex(tileInfo, tileIndex,
			boost::regex("/"));


	//presentation start time of a chunk (chunk deadline)
	//if we don't get chunk by timestamp, it may cause a re-buffering event.
	uint32_t timestamp = static_cast<uint16_t>(stoi(tileInfo[2].substr(0,tileInfo[2].find('.'))));

	//which part of the viewport this tile corresponds to.
	uint16_t tileIdx = static_cast<uint32_t>(stoi(tileInfo[1]));

	//std::cout<<timestamp<<","<<tileIdx<<std::endl;
	//We take 4 bytes to exclude the "\r\n\r\n" out of chunk bytes.
	Chunk chunk = {chunkPointer, chunkSize - 4};

	auto pair = chunks_.find(timestamp);

	if (pair != chunks_.end())
	{
		pair->second.insert(std::pair<uint16_t, struct Chunk>(tileIdx, chunk));
	}
	else
	{
		std::map<uint16_t, struct Chunk> tileIdxChunkMap;
		tileIdxChunkMap.insert(std::pair<uint16_t, struct Chunk>(tileIdx, chunk));
		chunks_.insert(std::pair<uint32_t, std::map<uint16_t, struct Chunk> >(timestamp,tileIdxChunkMap));
	}


}

void VideoPlayer::decode(VideoPlayer* videoPlayer)
{

	//urgent decode
	//decode 1 sec in advance.

	//TODO use chunk length in the system.

	//TODO clear chunks of previous second from map.
	//videoPlayer->frameId_ += videoPlayer->FPS_*50;
	uint32_t startChunk = (videoPlayer->frameId_ / videoPlayer->FPS_) + 1;
	std::vector<std::string> chunksDecoded;
	while(true)
	{
		sleep(2);
		startChunk = (videoPlayer->frameId_ / videoPlayer->FPS_) + 1;
		for(uint32_t idx = startChunk; idx < startChunk+2; idx++)
		{

			//chunks have presentation time first, and map<tile index, encoded tile frames> second.
			auto chunks = videoPlayer->chunks_.find(idx);
			if(chunks != videoPlayer->chunks_.end())
			{
				//tileInfo has tileIndex first, and encoded tile frames second.
				while(chunks->second.size()!=0)//for(auto& tileInfo : chunks->second)
				{
					auto tileInfo = chunks->second.begin();
					std::vector<uint8_t *> rawTileFrames;

					//std::cout<<tileInfo->first<<std::endl;
					//call decoder
					videoPlayer->decoder_->decode(tileInfo->second.chunk,tileInfo->second.chunkSize,
							rawTileFrames);

					//std::cout<<idx<<":"<<tileInfo->first<<":"<<rawTileFrames.size()<<std::endl;
					//					for(auto& frame : rawTileFrames)
					//					{
					//							std::ofstream myfile;
					//							myfile.open (std::to_string(chunks->first)+"_"+std::to_string(tileInfo->first));
					//
					//							for(int idx=0; idx<320*160*4;idx++)
					//							{
					//								myfile << frame->data[0][idx];
					//							}
					//							myfile.close();
					//
					//						free(frame->data[0]);
					//						av_frame_free(&frame);
					//					}
					//insert to decodedTileChunks_
					videoPlayer->decodedTileChunksMutex_.lock();
					if (videoPlayer->decodedTileChunks_.find(chunks->first)
							!= videoPlayer->decodedTileChunks_.end())
					{
						videoPlayer->decodedTileChunks_.find(chunks->first)->second.insert(
								std::pair<uint16_t, std::vector<uint8_t *>>(tileInfo->first
										, rawTileFrames));
						//std::cout<<"Added,"<<chunks->first<<":"<<tileInfo->first<<std::endl;
					}
					else
					{
						std::map<uint16_t,std::vector<uint8_t*>> temp;
						temp.insert(std::pair<uint16_t,std::vector<uint8_t*>>(tileInfo->first
								, rawTileFrames));

						videoPlayer->decodedTileChunks_.insert(std::pair<uint32_t
								, std::map<uint16_t,std::vector<uint8_t*>>>(chunks->first, temp));
						//std::cout<<"Added,"<<chunks->first<<":"<<tileInfo->first<<std::endl;
						//return;
					}
					videoPlayer->decodedTileChunksMutex_.unlock();

					//free chunks.
					auto& encodedFrameStruct = tileInfo->second;
					free(encodedFrameStruct.chunk);
					chunks->second.erase(tileInfo->first);
				}
			}
			//std::cout<<"-----"<<std::endl;


		}
		startChunk += 2;
		//videoPlayer->frameId_ += videoPlayer->FPS_*2;
		//sleep(100);
	}

	//FPS
	//1000 second.




}

void VideoPlayer::start(VideoPlayer* videoPlayer)
{

	sleep(1);
	long stime;
	long etime;

	uint8_t frameGap = 1000 / videoPlayer->FPS_;
	int frm = 1;

	uint32_t playSecond;
	//tileIndex, raw-tile-frame.
	std::map<uint16_t,uint8_t *> viewport;
	while(true)
	{
		stime = std::chrono::duration_cast<std::chrono::milliseconds>
		(std::chrono::system_clock::now().time_since_epoch()).count();

		bool check1 = true;
		bool check2 = true;

		//all tiles to present in the current frame.
		auto tiles =  videoPlayer->groundTruth_.find(videoPlayer->frameId_);
		if(tiles == videoPlayer->groundTruth_.end())
		{
			//no more frames;
			break;
		}

		//		std::cout<<videoPlayer->frameId_<<std::endl;

		//for each tile.
		for(auto tileIdx : tiles->second)
		{

			playSecond = ((videoPlayer->frameId_-1)/videoPlayer->FPS_) + 1;
			while(check1)
			{
				videoPlayer->decodedTileChunksMutex_.lock();
				if(videoPlayer->decodedTileChunks_.find(playSecond)
						!= videoPlayer->decodedTileChunks_.end())
				{
					check1 = false;
				}
				videoPlayer->decodedTileChunksMutex_.unlock();

			}
			check1 = true;
			//decoded chunks with frames belong to current presentation time.
			//this gets all the raw chunks for all tiles at chunk = play-second.

			if(videoPlayer->decodedTileChunks_.find(playSecond)
					!= videoPlayer->decodedTileChunks_.end())
			{
				auto& rawTilesChunks = videoPlayer->decodedTileChunks_.find(playSecond)->second;

				//get all frames of chunk.
				//std::cout<<"stitch:"<<playSecond<<":"<<videoPlayer->frameId_<<","<<tileIdx<<std::endl;
				while(check2)
				{
					videoPlayer->decodedTileChunksMutex_.lock();
					if(rawTilesChunks.find(tileIdx)
							!= rawTilesChunks.end())
					{
						//std::cout<<tileIdx<<":"<<rawTilesChunks.find(tileIdx)->first<<std::endl;

						check2 = false;
					}
					videoPlayer->decodedTileChunksMutex_.unlock();
				}
				check2 = true;

				if (rawTilesChunks.find(tileIdx) != rawTilesChunks.end())
				{
					//std::cout<<rawTilesChunks.find(tileIdx)->first<<" Found!"<<std::endl;
					auto& frame = rawTilesChunks.find(tileIdx)->second[videoPlayer->frameId_ % videoPlayer->FPS_];
					viewport.insert(std::pair<uint16_t,uint8_t *>(tileIdx,frame));
				}
				else
				{

					std::cout<<"MISSSSSSSSSSSSS:"<<rawTilesChunks.find(tileIdx)->first<<std::endl;
					//tile is missing. or not decoded.
				}


			}
			else
			{
				//schedule urgent request.
				//all tiles are needed.

			}

		}
		//std::cout<<videoPlayer->frameId_<<","<<viewport.size()<<std::endl;

		//ToDo
		//stichFrames.

		auto rawViewPort = videoPlayer->stitchTileFrames(viewport);
		free(rawViewPort);

		//free all tile-frames belonging to current frameId
		if(videoPlayer->frameId_ % videoPlayer->FPS_ == 0){

			for(auto& pair:  videoPlayer->decodedTileChunks_.find(playSecond)->second)
			{
				for(auto& pointer : pair.second)
				{
					free(pointer);
				}
			}

		}

		viewport.clear();

		etime = std::chrono::duration_cast<std::chrono::milliseconds>
		(std::chrono::system_clock::now().time_since_epoch()).count();

		std::this_thread::sleep_for(std::chrono::milliseconds((stime + frameGap) - etime));
		videoPlayer->frameId_++;
	}


}
int frm = 1;
uint8_t* VideoPlayer::stitchTileFrames(std::map<uint16_t,uint8_t *>& viewport)
{


	//assume that tile scheme is 12x12.
	uint32_t tileSize = 320 * 160 * 4;
	//assume that frame is in ARGB format.
	uint8_t * rawViewPort = (uint8_t *) malloc(sizeof(uint8_t) * viewport.size() * tileSize);



	// number of tiles in col.
	// number of rows.
	// start index.

	int tileWidth = 360/30;
	int tileHeight = 180/15;

	uint16_t startIdx;
	int row;
	int col;
	int prevRow = -1;
	int prevCol = -1;
	int numOfRows = 1;
	int numOfCols = 1;
	bool colScanned = false;
	std::string _all;
	for(auto& pair : viewport)
	{
		row = ((pair.first - 1) / tileHeight) + 1; //1--> 12 same row.
		col = ((pair.first - 1) % tileWidth) + 1; // 1--> 12
		_all += std::to_string(pair.first)+",";
		if(prevRow == -1 && prevCol == -1)
		{
			startIdx = pair.first;
		}

		if (prevRow != row && prevRow != -1)
		{
			if(prevRow != row - 1)
			{
				startIdx = pair.first;
				colScanned = false;

			}
			else
			{
				colScanned = true;
			}
			numOfRows++;
		}
		else if(prevCol != -1)
		{
			if(prevCol != col - 1 && !colScanned)
			{
				startIdx = pair.first;
			}
			numOfCols = colScanned? numOfCols : numOfCols+1;
		}
		prevRow = row;
		prevCol = col;
	}

//	std::cout<<frm<<"["<<_all<<"]"<<std::endl;
//	std::cout<< startIdx<<std::endl;
//	std::cout<<numOfCols<<","<<numOfRows<<std::endl<<std::endl;

	std::string _order = "";
	int t1= std::chrono::duration_cast<std::chrono::milliseconds>
			(std::chrono::system_clock::now().time_since_epoch()).count();
	int tileIdx;
	int currRow;
	//row is 160 * 4.
	//loop from 0 to 320
	//row * 320 * 160 * 4. is my base.
	int baseBytes;
	int colBytes;
	int count = 0;
	int stepSize = 320 * 4;
	for(int row = 0; row < numOfRows; row++)
	{
		baseBytes = tileSize * count;
		if(startIdx + tileWidth * row > tileWidth * tileHeight)
		{
			startIdx = ((startIdx -1) % tileWidth) + 1;
			numOfRows -= row;
			row = 0;
		}
		tileIdx =  startIdx + tileWidth * row ;

		for(int col = 0; col < numOfCols; col++)
		{
			colBytes = baseBytes + stepSize * col;
			int tempRow = ((tileIdx + col - 1) / tileHeight) + 1;
			if(col != 0 && tempRow != currRow)
			{
				_order+=std::to_string(tileIdx + col - tileWidth)+" ,";
				for(int ij = 0 ; ij < 160; ij++)
				{
					memcpy(rawViewPort + (colBytes + ij * numOfCols * stepSize) ,
							viewport.find(tileIdx + col - tileWidth)->second + (ij * stepSize),stepSize);
				}

			}
			else
			{
				for(int ij = 0 ; ij < 160; ij++)
				{
					memcpy(rawViewPort + (colBytes + ij * numOfCols * stepSize) ,
							viewport.find(tileIdx + col)->second + (ij * stepSize),stepSize);
				}
				_order+=std::to_string(tileIdx + col)+" ,";
				currRow = tempRow;

			}

			count++;
		}
		//check if I went outside.
	}

	int t2= std::chrono::duration_cast<std::chrono::milliseconds>
			(std::chrono::system_clock::now().time_since_epoch()).count();

	std::cout<<frm<<":"<<t2-t1<<std::endl;
	FILE * myfile;

	std::string filename = std::to_string(frm++);

	myfile = fopen(filename.c_str(),"wb");

	fwrite (rawViewPort , sizeof(uint8_t), viewport.size() * tileSize, myfile);

	fclose(myfile);

	return rawViewPort;

}


VideoPlayer::~VideoPlayer() {
	// TODO Auto-generated destructor stub
}


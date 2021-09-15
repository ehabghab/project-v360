/*
 * VideoPlayer.h
 *
 *  Created on: May 1, 2021
 *      Author: eghabash
 */

#ifndef VIDEOPLAYER_H_
#define VIDEOPLAYER_H_

#include <cstdint>
#include <map>
#include <mutex>

#include "Decoder.h"
#include "TilePredictor.h"

class VideoPlayer {
  struct Chunk {
    // pointer to received chunk bytes in memory;
    uint8_t *chunk;

    // chunk size in bytes
    uint32_t chunkSize;
  };

  // linked list to order the tiles in stitched frame.
  struct Node {
    AVFrame *tile;
    Node *nextTile;
  };

  std::mutex decodedTileChunksMutex_;

  uint8_t FPS_;

  uint32_t frameId_;

  std::map<uint32_t, std::map<uint16_t, struct Chunk>> chunks_;

  // Per frame, what are the tiles in the viewport.
  std::map<uint32_t, std::vector<uint16_t>> groundTruth_;

  std::vector<std::pair<float, float>> groundTruthCoordinates_;

  // per presentation time "chunk", per tile-index, the decode tile-frames.
  std::map<uint32_t, std::map<uint16_t, std::vector<uint8_t *>>>
      decodedTileChunks_;

  uint8_t *stitchTileFrames(std::map<uint16_t, uint8_t *> &viewport);

  void stitchTileFramesYUV(std::map<uint16_t, AVFrame *> &viewport);

  // This function will take viewport map as input which contains
  // the tiles to construct the viewport frame. And,
  // returns vector of linkedlist. The nodes in the vector
  // correspond to the first tiles in each row.
  void orderTilesToLinkedList(std::map<uint16_t, AVFrame *> &viewport,
                              std::vector<Node *> &viewportLinkedList);

 public:
  static void start(VideoPlayer *videoPlayer, TilePredictor *tilePredictor);

  static void decode(VideoPlayer *videoPlayer, Decoder *decoder);

  VideoPlayer();

  void addChunk(uint8_t *chunkPointer, uint32_t chunkSize,
                uint32_t tileChunkIdx, uint16_t tileIdx);

  virtual ~VideoPlayer();
};

#endif /* VIDEOPLAYER_H_ */

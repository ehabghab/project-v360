/*
 * Util.h
 *
 *  Created on: Jun 6, 2021
 *      Author: eghabash
 */

#include <string>

class Util {
  static long videoPlayTime;
  static std::string logTimestamp;

public:
  static const std::string getCurrentDateTime();
  static long getTime();
  static void sleep(long currentTime, long millisecondsToSleep);
  static long getTimePassedSinceLastFrame();
  static void setFramePlayTime(long FramePlayTimeInMs);
  static std::string getLogTimestamp();
};
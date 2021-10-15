/*
 * Util.h
 *
 *  Created on: Jun 6, 2021
 *      Author: eghabash
 */

#include <string>

class Util {
public:
  static const std::string getCurrentDateTime();
  static long getTime();
  static void sleep(long currentTime, long millisecondsToSleep);
};
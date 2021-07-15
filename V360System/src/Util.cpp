#include "Util.h"

#include <chrono>

long Util::getTime() {
  return std::chrono::duration_cast<std::chrono::milliseconds>(
             std::chrono::system_clock::now().time_since_epoch())
      .count();
}

void Util::sleep(long currentTime, long millisecondsToSleep) {
  while (getTime() - currentTime < millisecondsToSleep)
    ;
}

/*
 * Time.h
 *
 *  Created on: Mar 11, 2015
 *      Author: fermitron2048
 */

#ifndef BASE_TIMER_H_
#define BASE_TIMER_H_

#include <Arduino.h>

class Timer {
private:
	unsigned long startTime;
	unsigned long elapsedTime;
	unsigned long timer;
	unsigned long preRollElapsed; // Number of ms or us elapsed before the rollover
	unsigned long lastCheck; // Result of millis() or micros() at last check
	bool rolledOver; // The millis() or micros() output rolled over during this timer session
	bool running;
	bool micro;

public:
	Timer();
	Timer(bool micro);
	virtual ~Timer();

	void startTimer();
	void stopTimer();
	void restartTimer();
	void resetTimer();
	unsigned long getElapsedTime();
	bool isTimerRunning();
	void setTimer(unsigned long time);
	unsigned long getStartTime();
};

#endif /* BASE_TIMER_H_ */

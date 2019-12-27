/*
 * Time.cpp
 *
 *  Created on: Mar 11, 2015
 *      Author: fermitron2048
 */

#include "Timer.h"
#include <stdio.h>
#include <limits.h>

Timer::Timer() {
	startTime=0;
	elapsedTime=0;
	running=false;
	micro=false;
	timer=0;
	rolledOver=false;
	preRollElapsed=0;
	lastCheck=0;
}

/*
 * Instantiate a timer, specifying whether the timer
 * measures microseconds (true) or milliseconds (false)
 */
Timer::Timer(bool micro) {
	this->micro = micro;
	startTime=0;
	elapsedTime=0;
	running=false;
	timer=0;
	rolledOver=false;
	preRollElapsed=0;
	lastCheck=0;
}

Timer::~Timer() {
}

void Timer::startTimer() {
	if(running) return;
	resetTimer();
	if(micro) startTime = micros();
	else startTime = millis();
	running = true;
}

void Timer::stopTimer() {
	if(!running) return;
	getElapsedTime(); // Sets elapsedTime and compensates for rollover
	running = false;
}

void Timer::resetTimer() {
	// This stops and clears the timer
	stopTimer();
	startTime = elapsedTime = 0;
	rolledOver = false;
	preRollElapsed=0;
	lastCheck=0;
}

unsigned long Timer::getElapsedTime() {
	unsigned long currentValue;
	if (running) {
		if (micro) currentValue = micros();
		else currentValue = millis();
		// Handle rollover
		if (!rolledOver) {
			if (lastCheck != 0 && currentValue < lastCheck) {
				// We just rolled over
				rolledOver = true;
				preRollElapsed = ULONG_MAX - startTime;
				elapsedTime = currentValue + preRollElapsed;
			} else {
				// Haven't rolled over yet
				elapsedTime = currentValue - startTime;
			}
		} else {
			// We rolled over some time ago
			elapsedTime = currentValue + preRollElapsed;
			// If elapsedTime itself rolls over, result is not guaranteed.
		}
		lastCheck = currentValue;
	}
	return elapsedTime;
}

void Timer::restartTimer() {
	resetTimer();
	startTimer();
}

bool Timer::isTimerRunning() {
	return running;
}

void Timer::setTimer(unsigned long time) {
	timer = time;
}

unsigned long Timer::getStartTime() {
	return startTime;
}

/*
 * RollingAverage.cpp
 *
 *  Created on: May 16, 2015
 *      Author: fermitron2048
 */

#include "RollingAverage.h"
#include <Arduino.h>
#include <stdlib.h>

RollingAverage::RollingAverage(long numValues) {
	usingRingBuf = false;
	bufsize = numValues;
	head=0;
	tail=0;
	count=0;
	avg=0;
	sum=0;
	total=0;
	ringbuf = 0;
	debug=false;
}

RollingAverage::RollingAverage(long numValues, bool highPrecision) {
	bufsize = numValues + 1;
	if(highPrecision) {
		usingRingBuf = true;
		ringbuf = (double*)malloc(bufsize * sizeof(double));
	} else {
		usingRingBuf = false;

	}
	head=0;
	tail=0;
	count=0;
	avg=0;
	sum=0;
	total=0;
	debug=false;
}

RollingAverage::RollingAverage() {
	usingRingBuf=0;
	bufsize = 20;
	head=0;
	tail=0;
	count=0;
	avg=0;
	sum=0;
	total=0;
	ringbuf=0;
	debug=false;
}

RollingAverage::~RollingAverage() {
	if(usingRingBuf) free(ringbuf);
}

void RollingAverage::addValue(double value) {
	/*
	 * The buffer is empty when head == tail
	 * When a value is added, the value is written to head, and head is advanced
	 */
	if(usingRingBuf) {
		// Rolling average with ring buffer
		ringbuf[head] = value;

		// The buffer is empty
		if(head == tail) {
			avg = value;
			count++,head++;
			if(debug) Serial.print(value);
			if(debug) Serial.print(",");
			if(debug) Serial.print(avg);
			if(debug) Serial.print(",");
			if(debug) Serial.print(String(getStdev(),3));
			if(debug) Serial.print(",");
			if(debug) Serial.print(count);
			if(debug) Serial.print("\n");
			return;
		}

		double oldavg = avg;
		if(((head+1) % bufsize) != tail ) {
			// If the buffer isn't full yet
		    avg += (value - avg)/++count*1.0;
		    sum += (value - oldavg) * (value - avg);
			head = (head+1) % bufsize;
		} else {
			// Add to head and drop from tail
			avg += (value - ringbuf[tail]) / (count * 1.0);
			sum += (value - avg + ringbuf[tail] - oldavg) * (value - ringbuf[tail]);
			head = (head+1) % bufsize;
			tail = (tail+1) % bufsize;
		}
		if(debug) Serial.print(value);
		if(debug) Serial.print(",");
		if(debug) Serial.print(avg);
		if(debug) Serial.print(",");
		if(debug) Serial.print(String(getStdev(),3));
		if(debug) Serial.print(",");
		if(debug) Serial.print(count);
		if(debug) Serial.print("\n");

	} else {
		// Just do the weighted moving average and standard deviation
		double oldavg = avg;
		if(count >= bufsize) {
			avg -= avg/count*1.0;   // Remove one average number
		    avg += value/count*1.0; // Add the new number to the average
		} else {
			avg += (value - avg) / ++count * 1.0;
		}
	}
}

double RollingAverage::getAverage() {
	return avg;
}

double RollingAverage::getStdev() {
	return (count>1) ? sqrt(sum / (count-1)) : 0.0;
}

long RollingAverage::getCount() {
	return count;
}

// Returns true when the ring buffer is full (only applicable with high precision)
bool RollingAverage::isFull() {
	if(count+1 == bufsize) return true;
	else return false;
}

double RollingAverage::getMin() {
	if(!usingRingBuf) return -9999;
	double min = ringbuf[tail];
	for(long i=0; i<count; i++) {
		long j = (tail + i) % bufsize;
		if(ringbuf[j] < min) min = ringbuf[j];
	}
	return min;
}

double RollingAverage::getMax() {
	if(!usingRingBuf) return -9999;
	double max = ringbuf[tail];
	for(long i=0; i<count; i++) {
		long j = (tail + i) % bufsize;
		if(ringbuf[j] > max) max = ringbuf[j];
	}
	return max;
}

void RollingAverage::reset() {
	head=0;
	tail=0;
	count=0;
	avg=0;
	sum=0;
	total=0;
}

void RollingAverage::printArray() {
	if(!usingRingBuf) return;
	Serial.print(tail);
	Serial.print(",");
	Serial.print(head);
	Serial.print(",");
	Serial.println(count);
	for(long i=0; i<count; i++) {
		long j = (i + tail) % bufsize;
		Serial.print(String(ringbuf[j],2));
		Serial.print(",");
	}
	Serial.println();
}

double RollingAverage::getLatestValue() {
	if(usingRingBuf == false) return -9999;
	return ringbuf[(head+bufsize-1) % (bufsize)];
}

double RollingAverage::getEarliestValue() {
	if(usingRingBuf == false) return -9999;
	return ringbuf[tail];
}

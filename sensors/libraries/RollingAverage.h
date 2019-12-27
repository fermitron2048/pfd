/*
 * RollingAverage.h
 *
 *  Created on: May 16, 2015
 *      Author: fermitron2048
 */

#ifndef LIBRARIES_BASE_ROLLINGAVERAGE_H_
#define LIBRARIES_BASE_ROLLINGAVERAGE_H_

class RollingAverage {
private:
	double* ringbuf;
	long head,tail,count;
	double avg,sum,total;
	long bufsize;
	bool usingRingBuf;
	bool debug;

public:
	RollingAverage();
	RollingAverage(long numValues);
	RollingAverage(long numValues, bool highPrecision);
	virtual ~RollingAverage();

	void addValue(double value);
	double getAverage();
	double getStdev();
	double getMin();
	double getMax();
	double getLatestValue();
	double getEarliestValue();
	long getCount();
	bool isFull();
	void reset();
	void printArray();
};

#endif /* LIBRARIES_BASE_ROLLINGAVERAGE_H_ */

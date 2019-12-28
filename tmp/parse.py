#!/usr/bin/env python

import json
import codecs
import statistics
from numpy import std

def get_macs(data):
    """
    returns a dict of all macs and its occurrences
    """

    macs = []
    values = {}

    for p in data['fingerprint']:
        for v in p['signalSample']:
            macs.append(v['macAddress'])

    for mac in list(set(macs)):
        values[mac] = macs.count(mac)

    return values


def get_average_strength(data, mac):
    """
    returns the average of a mac address
    """

    strength = []

    for p in data['fingerprint']:
        for v in p['signalSample']:
            if v['macAddress'] == mac:
                strength.append(int(v['strength']))

    return statistics.mean(strength)


def get_standard_deviation(data, mac):
    """
    returns the standard deviation for a specific mac
    """

    strength = []

    for p in data['fingerprint']:
        for v in p['signalSample']:
            if v['macAddress'] == mac:
                strength.append(-1 * int(v['strength']))

    # print(strength)
    return std(strength, ddof=1)



if __name__ == "__main__":
    with codecs.open('fp.json', 'r', 'utf-8-sig') as json_file:
        data = json.load(json_file)

    unique_macs = get_macs(data)
    print("Measurements: %d\tMinimum occurrences: %d " % (len(data['fingerprint']), int(1/3 * len(data['fingerprint']))))
    for k, v in unique_macs.items():
        print("MAC: %s\tCounts: %s\tAverage: %f\tStd.Abweichung: %f" % (
            k,
            v,
            get_average_strength(data, k),
            get_standard_deviation(data, k)
        ))
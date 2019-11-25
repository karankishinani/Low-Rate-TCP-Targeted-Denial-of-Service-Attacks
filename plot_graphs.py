# Average data points and get rid of error messages
# Makes 2 plots in the graphs/ directory
# One plot uses the average throughput, and the other uses the min throughput

import sys
import glob
import plot_normalized_throughput
from helper import *


def plot_graphs(algo):
    path = 'outputs/*'
    graphDir = "graphs"
    outDir = "cleanOutput"
    files = glob.glob(path)

    for file in files:
        dict = {}
        for line in open(file, 'r'):
            splitLine = line.split()
            key = splitLine[0]
            value = splitLine[1]
            if "error" in value:
                continue

            if dict.has_key(key):
                dict[key].append(float(value))
            else:
                dict[key] = [float(value)]

        queueSize = re.search('[0-9]+', file).group(0)
        outfileName = outDir + "/" + algo + "_" + queueSize + ".txt"
        minOutfileName = outDir + "/" + algo + "_min" + queueSize + ".txt"

        with open(outfileName, 'w') as outfile, open(minOutfileName, 'w') as minOutfile:
            baseline_avg = 1.0
            baseline_min = 1.0
            for key in dict:
                values = dict[key]
                if key != '0.0':
                    outfile.write(key + " " + str(avg(values)) + "\n")
                    minOutfile.write(key + " " + str(min(values)) + "\n")
                else:
                    baseline_avg = avg(values)
                    baseline_min = min(values)

        plot_normalized_throughput.plot(outfileName, baseline_avg, graphDir + "/" + algo + "_" + queueSize)
        plot_normalized_throughput.plot(minOutfileName, baseline_min, graphDir + "/" + algo + "_min" + queueSize)


if __name__ == "__main__":
    algo = sys.argv[1] if len(sys.argv) == 2 else "reno"
    plot_graphs(algo)

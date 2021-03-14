#!/bin/bash

# Note: Mininet must be run as root.  So invoke this shell script
# using sudo.

time=200
bwnet=1.5
# TODO: If you want the RTT to be 20ms what should the delay on each
# link be?  Set this value correctly.
delay=5

for qsize in 20 100; do
    dir=-q$qsize

    # TODO: Run bufferbloat.py here...
    python3 bufferbloat.py -b $bwnet --delay $delay -d output -t $time --maxq $qsize  

    # TODO: Ensure the input file names match the ones you use in
    # bufferbloat.py script.  Also ensure the plot file names match
    # the required naming convention when submitting your tarball.
    python3 plot_queue.py -f output/q.txt -o output/reno-buffer$dir.png
    python3 plot_ping.py -f output/ping.txt -o output/reno-rtt$dir.png
    rm -f output/*.txt
done

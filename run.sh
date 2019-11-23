#!/usr/bin/env bash

function initDir {
    for dir in "$@"; do
        if [[ -e $dir ]]; then
            rm -rf $dir
        fi
        mkdir $dir
    done
}

time=30
min_rto=1000
qsize=4

initDir graphs cleanOutput
for cong in reno cubic westwood vegas; do
    for i in 1 2 3; do

        echo "Running without attacker"
        sudo mn --clean
        dir=data-q$qsize-p0.0-i$i
		python topology.py --dir $dir --t $time --maxq $qsize --min_rto $min_rto --disable_attacker true --cong $cong

		echo "Running with attacker"
		# Always have a "." in the interburst_period numbers. E.g., use "4.0" not "4"
		for interburst_period in 0.4 0.45 0.5 0.55 0.6 0.65 0.7 0.75 0.8 0.85 0.9 0.95 1.0 1.05 1.2 1.4 1.6 1.8 2.0 3.0 4.0 5.0; do
		    sudo mn --clean
		    dir=data-q$qsize-p$interburst_period-i$i
			python topology.py --dir $dir --t $time --maxq $qsize --burst_period $interburst_period --min_rto $min_rto --cong $cong
		done
	done

	python collect_throughputs.py
	python cleanData.py --cong $cong
done

sudo python -m SimpleHTTPServer 80
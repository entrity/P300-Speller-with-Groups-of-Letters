#!/bin/bash

[[ -f analysis.tsv ]] && rm analysis.tsv

DIR=OpenvibeScenarios
DIR=Scenarios
DIR=.

find $DIR -name \*-features.tsv | while read -r fea; do
	sti=${fea/features/stims}
	# echo $fea
	# echo $sti
	d=$(dirname "$fea")
	pd=$(dirname "$d")
	if [[ $pd =~ OpenvibeScenarios$ ]]; then
		echo base
		N=6
	elif [[ $pd =~ Scenarios$ ]]; then
		echo eeg
		N=2
	fi
	python2 ./python/scripts/my_p300_3_analyzer.py $fea $sti $N analysis.tsv || exit 8
done

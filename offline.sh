#!/bin/bash

des=$HOME/openvibe/openvibe-designer.sh

function run()
{
	ovfile="$1"
	d=$(dirname "$ovfile")
	pd=$(dirname "$d")
	b=$(basename "$ovfile")
	echo $b
	if [[ $ovfile =~ ^OpenvibeScenarios ]]; then
		echo -n base
		scen2=OpenvibeScenarios/p300-xdawn-2-train-xDAWN.xml
		scen3=OpenvibeScenarios/p300-xdawn-3-train-classifier.xml
		N=6
	elif [[ $ovfile =~ ^Scenarios ]]; then
		echo -n eeg
		scen2=Scenarios/my-p300-xdawn-2-train-xDAWN.xml
		scen3=Scenarios/my-p300-xdawn-3-train-classifier.xml
		N=2
	else
		>&2 echo ERR
	fi
	echo " $ovfile"
	# Names
	scen2mod="$pd/tmp-2.xml"
	cspfile="$pd/tmp-csp-filter.cfg"
	scen3mod="$pd/tmp-3.xml"
	featuretsv="${ovfile}-features.tsv"
	stimtsv="${ovfile}-stims.tsv"
	if [[ -e "$featuretsv" ]] && [[ -e "$stimtsv" ]]; then
		echo "Outputs exist. SKIPPING."
		return
	fi
	# Update scenario 2
	xmlstarlet ed \
		-u "/OpenViBE-Scenario/Boxes/Box[Name='Generic stream reader']/Settings/Setting[Name='Filename']/Value" -v "$ovfile" \
		-u "/OpenViBE-Scenario/Boxes/Box[Name='xDAWN Spatial Filter Trainer']/Settings/Setting[Name='Spatial filter configuration']/Value" -v "$cspfile" \
		"$scen2" > "$scen2mod"
	# Run scenario 2
	if [[ -f $des ]]; then
		echo Starting 2
		rm -rf $HOME/.config/openvibe
		if ! $des --no-gui --play-fast "$scen2mod" >/dev/null; then
			>&2 echo fail 2
			return
			>&2 echo this should not be echoed
		fi
	fi
	# Update scenario 3
	xmlstarlet ed \
		-u "/OpenViBE-Scenario/Boxes/Box[Name='Generic stream reader']/Settings/Setting[Name='Filename']/Value" -v "$ovfile" \
		-u "/OpenViBE-Scenario/Boxes/Box[Name='xDAWN Spatial Filter']/Attributes/Attribute[Value='\${Player_ScenarioDirectory}/p300-spatial-filter.cfg']/Value" -v "$cspfile" \
		"$scen3" > "$scen3mod"
	# Run scenario 3
	if [[ -f $des ]]; then
		echo Starting 3
		rm -rf $HOME/.config/openvibe
		if ! $des --no-gui --play-fast "$scen3mod" >/dev/null; then
			>&2 echo fail 3
			return
			>&2 echo this should not be echoed
		fi
	fi
	# Run analyzer
	mv features.tsv "$featuretsv"
	mv stims.tsv "$stimtsv"
	# python2 "./python/scripts/my_p300_3_analyzer.py" features.tsv stims.tsv $N >> offlinebatch.sh
	# if python2 "./python/scripts/my_p300_3_analyzer.py" features.tsv stims.tsv $N; then
	# 	echo SUCCESS
	# 	echo "$ovfile" >> success.tsv
	# else
	# 	>&2 echo ERRR
	# 	echo "$ovfile" >> redo.tsv
	# 	exit 1
	# fi
}


if [[ $1 =~ .ov$ ]]; then
	run "$1"
else
	while read -r ovfile; do
		run "$ovfile"
	done
fi

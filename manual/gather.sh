#!/bin/bash

for file in seedbank.py seedbank_daemon.py seedbank_setup.py seedbank_node.py; do
	"../seedbank/${file}" -h > core/help/${file%.py}
done

for file in seedbank_node.py; do
	"../seedbank/${file}" -h > addons/help/${file%.py}
done


#!/bin/bash

for file in seedbank.py seedbank_daemon.py seedbank_setup.py; do
	"../seedbank/${file}" -h > core/help/${file%.py}
done

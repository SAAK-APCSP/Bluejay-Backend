#!/bin/bash

# Build and test backend
docker-compose up -d --build
curl localhost:8080 # PORTS MUST NOT OVERLAP


# IF you want to code a script, this is an example checkpoint
# Checkpoint -- does the backend work?
# put exact all caps YES to proceed or else the script will exit (safety)
echo -n "CHECKPOINT. Does the curl command return the right page? YES/NO: " 
read checkpoint
if [checkpoint == "YES"]; then
    # In future scripts, we will not exit here, but assuming we have done R53 we will continue
    echo "CHECKPOINT PASSED. Proceed."
    exit 0 # This will exit without displaying the output as an error
else
    echo "CHECKPOINT FAILED. Must fix issues."
    exit 1 # This will exit while displaying the output as an error
fi

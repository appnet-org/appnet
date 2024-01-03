#!/bin/bash

# Define the base directory
BASE_DIR="$HOME/adn-controller/envoy/elements"

# Change to the base directory using pushd
pushd $BASE_DIR > /dev/null

# Check if the change directory operation was successful
if [ $? -ne 0 ]; then
    echo "Failed to change directory to $BASE_DIR. Exiting."
    exit 1
fi

# Iterate over each directory in the base directory
for dir in */ ; do
    # Use pushd to change to the sub-directory
    pushd "$dir" > /dev/null

    # Check if build.sh exists and is executable
    if [ -x "build.sh" ]; then
        echo "Executing build.sh in $dir"
        ./build.sh
    else
        echo "build.sh not found or not executable in $dir"
    fi

    # Use popd to go back to the base directory
    popd > /dev/null
done

# Return to the original directory
popd > /dev/null

echo "Script execution completed."
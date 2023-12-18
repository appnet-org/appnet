#!/bin/bash

cd ./envoy/elements

# Iterate over each item in the current directory
for folder in */ ; do
    # Check if it's a directory
    if [ -d "$folder" ]; then
        # Change directory to the folder
        cd "$folder"

        # Check if build.sh exists and is executable
        if [ -x "build.sh" ]; then
            # Run the build.sh script
            ./build.sh
        else
            echo "build.sh not found or not executable in $folder"
        fi

        # Go back to the parent directory
        cd ..
    fi
done

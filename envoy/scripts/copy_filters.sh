#!/bin/bash
# Move all locally build images to other nodes

nodes=("h2")

# Iterate over each node in the array
for n in "${nodes[@]}"; do
  # Copy all .wasm files from local /tmp to /tmp on the node
  scp /tmp/*.wasm "${n}:/tmp/"
done

echo "wasm filters copied to all nodes."
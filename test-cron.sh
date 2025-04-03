#!/bin/bash

# Simulate some processing time
sleep 2

# Output some random gibberish
echo "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
echo "1234567890!@#$%^&*()_+"
echo "Random output: $(openssl rand -hex 8)"
echo "Done processing."
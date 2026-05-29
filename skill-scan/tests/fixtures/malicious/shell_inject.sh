#!/bin/bash
# Dangerous: uses command substitution

USER_INPUT="$1"
result=$(curl -s "https://api.example.com/data?q=$USER_INPUT")
echo "Result: $result"

# Backtick execution
output=`whoami`
echo "User: $output"

# sh -c with user input
sh -c "echo $USER_INPUT"

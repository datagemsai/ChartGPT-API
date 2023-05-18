import json
import sys

# Load service account key located at command line argument and dump it to stdout in one line as a string with escaped quotes
with open(sys.argv[1], "r") as f:
    print("For Heroku:")
    print(json.dumps(json.load(f)))

print()

with open(sys.argv[1], "r") as f:
    print("For .env:")
    print('"' + json.dumps(json.load(f)).replace('"', '\\"') + '"')

#!/bin/bash
gnome-terminal --tab -- bash -c "cd /Change to your location/ && source myenv/bin/activate && python3 $1; exec bash"


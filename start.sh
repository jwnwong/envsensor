cd ~/Projects/envsensor
. myenv/bin/activate
python envServer.py >> envServer.out 2>&1 &
python envsensor_livingroom.py >> envsensor_livingroom.out 2>&1 &

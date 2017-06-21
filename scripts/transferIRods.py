import getfiles
from datetime import datetime

# The month and days of interest
months = {'may': 5}
days = {'may': range(7, 24)}

yr = 2016
times = range(0, 24)

# Generate hourly datetime objects for each date
maydates = [datetime(yr, months['may'], d, t) for d in days['may'] 
            for t in times]

# Get the files from SR1. Easy peasy, lemon squeazy.
getter = getfiles.iRodsGetter(workdir='/cunyZone/home/luis.ortiz/forecast/')

for dt in maydates:
    getter.getFiles(dt)

#!/scratch/luis.ortiz/anaconda2/bin/python
import forecastdownload
import time

# Script to Download forecast gribfiles
# Laying down the groundwork for adding further initialization times

downloader = forecastdownload.GRIBDownloader(model='NAM', date='today')
start = time.time()
downloader.getFiles(inittime='00')

print 'Downloads took ', time.time() - start, ' seconds'

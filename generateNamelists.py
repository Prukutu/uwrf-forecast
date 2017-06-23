import namelist
from datetime import datetime, timedelta


today = datetime.today()
startdate = datetime(today.year, today.month, today.day, 0)
enddate = startdate + timedelta(hours=84)

# The WPS format for start and end dates is:
#   'YYYY-mm-dd_HH:MM:SS' (max doms)
doms = 3  # number of domains
wpsdatefmt = "'%Y-%m-%d_%H:%M:%S'"
wps_start = [startdate.strftime(wpsdatefmt)]*doms + ['']
wps_end = [enddate.strftime(wpsdatefmt)]*doms + ['']

# for the WRF namelist, start year, month, and day are seprate parameters
start_year = [startdate.strftime('%Y')]*doms + ['']
start_month = [startdate.strftime('%m')]*doms + ['']
start_day = [startdate.strftime('%d')]*doms + ['']

end_year = [enddate.strftime('%Y')]*doms + ['']
end_month = [enddate.strftime('%m')]*doms + ['']
end_day = [enddate.strftime('%d')]*doms + ['']

# Initialize the namelist objects and update dates
wrf = namelist.Namelist(program='wrf')
wps = namelist.Namelist(program='wps')

wrf_fields = wrf.load()
wps_fields = wps.load()

# Update the WPS date fields
wps_fields['&share']['start_date'] = wps_start
wps_fields['&share']['end_date'] = wps_end

# Likewise for the WRF date fields
wrf_fields['&time_control']['start_year'] = start_year
wrf_fields['&time_control']['start_month'] = start_month
wrf_fields['&time_control']['start_day'] = start_day

wrf_fields['&time_control']['end_year'] = end_year
wrf_fields['&time_control']['end_month'] = end_month
wrf_fields['&time_control']['end_day'] = end_day

# Finally, write the updated files
wrf.generateNamelist('namelist.input')
wps.generateNamelist('namelist.wps')

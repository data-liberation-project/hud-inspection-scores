# -*- coding: utf-8 -*-
"""
Created on Fri Feb 24 09:17:43 2023
@author: jebecker94
"""

# Import Packages
from datetime import date, timedelta
import requests
import time

# Date Range
def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

# Main Routine
if __name__ == '__main__' :

    ## Parameters
    # Save Folder
    save_folder = 'raw'

    # Start/End Dates
    start_date = date(2020, 6, 1)
    end_date = date(2023, 2, 25)

    # File Extension
    extension = 'xls'
    # extension = 'pdf'

    ## Download Data
    for single_date in daterange(start_date, end_date) :
        # Get Date and Report Progress
        isodate = single_date.strftime("%Y-%m-%d")
        date_string = single_date.strftime("%m%d%Y")
        print('Checking Multifamily for date:', isodate)

        # URL
        url = f'https://www.hud.gov/sites/dfiles/Housing/documents/MF_Inspection_Report{date_string}.{extension}'

        # Get Page Contents
        r = requests.request('GET', url)
        content = r.content

        # Save Page Contents
        save_file = f'{save_folder}/{isodate}_MF_Inspection_Report{date_string}.{extension}'
        with open(save_file, 'wb') as f:
            f.write(content)

        # Courtesy Pause
        time.sleep(1)

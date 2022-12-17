import pandas as pd
import datetime as dt
import os

path = os.getcwd() # get the current directory where the script is placed
try: 
    filename = f'{path}/iControl IR experiment.xlsx'
    open(filename)
except: 
    print("File named ‘iControl IR experiment.xlsw' does not exist.")
else:
    print('Processing...')

#read files
measured_values = pd.read_excel(filename,sheet_name='Measured values', skiprows=[1])
recipe = pd.read_excel(filename,sheet_name='Recipe', usecols=['Action / Note / Sample','Type','Start Time'])

#slice columns that are needed
recipe_note = recipe[recipe['Type']=='Note'].iloc[:,[1,2]]
measured_values_filtered = measured_values.iloc[:,[1,4,5,6,7,9,10,11]].copy()

#convert datetime type
recipe_note['Start Time'] = pd.to_datetime(recipe_note['Start Time'], format='%H:%M:%S')
measured_values_filtered['Rel. Time'] = pd.to_datetime(measured_values_filtered['Rel. Time'], format='%H:%M:%S') 

#sort data by time
measured_values_filtered = measured_values_filtered.sort_values('Rel. Time')
recipe_note = recipe_note.sort_values('Start Time')

#merge on time and fill note data into the nearest time (1 second tolerance)
output = pd.merge_asof(measured_values_filtered,recipe_note,left_on = 'Rel. Time',right_on='Start Time',direction='forward',tolerance=pd.Timedelta(seconds=1)).drop(columns=['Start Time'])
output['Rel. Time'] = output['Rel. Time'].dt.time

#rename columns
output = output.rename({'Rel. Time':'DateTime'},axis=1)
output.to_excel('iControl IR experiment_output.xlsx',sheet_name = 'Output',index=False)
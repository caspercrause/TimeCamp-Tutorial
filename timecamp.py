from pytimecamp import Timecamp
import pandas as pd
import numpy as np
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta
import os
from dotenv import load_dotenv
import dlt

# Load environmnet file
load_dotenv()

# Create a TimeCamp object
tc = Timecamp( os.getenv("TIMECAMP_API_KEY") )

ids = [id for id in tc.users]
# Helper function

def create_dict(Input_list):
    """
    Creates a dict with an empty list of values but assigns the keys from a list of names provided by the user.
    """
    CustomDict = {key:[] for key in Input_list}
    return CustomDict

# Map the columns of the dataframe to attributes of the timecamp object to be queried:
Field_Names_Mapped_to_TimeCamp = {
    'Entry_id' : 'id',
    'Date': 'date', 
    'User_Name': 'user_name',
    'Project_Name': 'project_name', 
    'Task_Name' :'name',
    'Description' : 'description', 
    'Timer_Start': 'start_time', 
    'Timer_End' : 'end_time', 
    'Duration': 'duration'}

DataFrame_Column_Names = [ col for col in Field_Names_Mapped_to_TimeCamp.keys() ]

dictionary = create_dict( Input_list=DataFrame_Column_Names )

Now = dt.now()

print(f"Executing script at {Now.strftime('%A %b %d, %Y at %H:%M:%S')}")

# Create upper and lower limits in the format "YYYY-MM-DD" to query timecamp:
LowerLimit = (Now - relativedelta(days=7)).strftime('%F')

UpperLimit = (Now - relativedelta(days=0)).strftime('%F')

# Iteratively retrieve entries from the timecamp API and append them into our dictionary:
"""

Example of how this code iterates: 

dictionary['Date'].append(entry.date)
dictionary['User_Name'].append(entry.user_name)
dictionary['Project_Name'].apppend(entry.project.name)
...
...
dictionary['Duration'].apppend(entry.project.duration)

""" 
for entry in tc.entries(from_date=LowerLimit, to_date=UpperLimit, user_ids=id):
    for ColumnName, timecamp_attr_name in Field_Names_Mapped_to_TimeCamp.items():
        try:
            dictionary.get(ColumnName).append(getattr(entry, timecamp_attr_name)) 
        except:
            dictionary.get(ColumnName).append(np.nan)

    
Timecamp_DF = pd.DataFrame(dictionary)

print(f'    ** Retrieved {len(Timecamp_DF)} rows.')

# Everything queried from the TimeCamp API is of type string so we have to convert data types

Date_Cols = ["Date", "Timer_Start", "Timer_End"]
Numeric_Cols = ["Duration"]
Time_Cols = ['Timer_Start', 'Timer_End']

# Concatenate date and time fields together:
for col in Time_Cols:
    Timecamp_DF[col] = Timecamp_DF[['Date', col]].agg(' '.join, axis=1)

# Convert to Date Time objects:
for col in Date_Cols:
    if col == "Date":
        Timecamp_DF[col] = pd.to_datetime(Timecamp_DF[col]).dt.date
    else:
        Timecamp_DF[col] = pd.to_datetime(Timecamp_DF[col])

# Convert to Float:
Timecamp_DF[Numeric_Cols] = Timecamp_DF[Numeric_Cols].astype('Float64')

# Arrange Data
Timecamp_DF.sort_values(['Date', 'User_Name', 'Timer_Start'], ascending=[True, True, True], inplace=True)

# Prepare data in a format that is ingestable for the dlt package:
data = Timecamp_DF.to_dict(orient="records")

pipeline = dlt.pipeline(
    pipeline_name="timecamp", destination="bigquery", dataset_name="timecamp_data_expirement", progress='enlighten'
)

load_info = pipeline.run(
    data,
    write_disposition="merge", 
    primary_key='Entry_id',
    table_name="daily_table"
)

print(load_info)
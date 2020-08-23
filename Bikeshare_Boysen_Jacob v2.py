
import pandas as pd
import numpy as np
import datetime as dt

#### OPTION TO SET PATH TO CSV FILES ####
#path=" "
#os.chdir(path)

##### BUILD PROMPT FOR FILTERS FUNCTION #####
def get_filters():

    """ The purpose of this function is to prompt users to provide three filters to subset the
    data - City, Month, and Day. While loops are used to handle errors and give the user another
    opportunity to enter the correct response."""

    #### BUILD UI PROMPTS FOR FILTER INPUTS ####

    #SELECT CITY
    '''The while loop will continue until the the correct spelling of the city is entered.  The lower
    function converts the user input to lower case. '''
    input_city=None
    input_city=input('Which city would you like to research: Chicago, New York City, or Washington?\n')
    cities=['chicago', 'new york city', 'washington']
    input_city=input_city.lower()

    valid_input_city=0
    while valid_input_city == 0:
        if input_city in cities:
            valid_input_city=1
            #return input_city
        else: input_city=input("That's not a valid city. Please select from one of these cities: Chicago, New York City, or Washington?").lower()

    #SELECT MONTH
    '''The while loop will continue until the the correct spelling of the month or 'All' is entered.  The lower
    function converts the user input to lower case. '''
    input_month=None
    input_month=input("Are you interested in a specific month? Enter January, February, March ... or All. ")
    month=['january','february','march','april','may','june','july','august','september','october','november','december','all']
    input_month=input_month.lower()

    valid_month=0
    while valid_month == 0:
        if input_month in month:
            valid_month=1
        else: input_month=input("That's not a valid month. Please enter the name of the month, like: January, February, etc. \n").lower()


    #SELECT DAY OF THE WEEK
    '''The while loop will continue until the the correct spelling of the day or 'All' is entered.  The lower
    function converts the user input to lower case. '''
    input_day=None
    input_day=input("Would you like to see a specific day of the week? Enter Monday, Tuesday, Wednesday ... or All. \n")
    day=['monday','tuesday','wednesday','thursday','friday','saturday','sunday','all']
    input_day=input_day.lower()

    valid_day=0
    while valid_day == 0:
        if input_day in day:
            print("Awesome! We're processing your request now.")
            valid_day=1
        else: input_day=input("That's not a valid month. Please enter the weekday by name, like: Monday, Tuesday, etc.\n").lower()

    return input_city, input_month, input_day

############ SELECT CSV FROM DICTIONARY ################
""" This block organizes the 3 CSV files in a dictionary and then then creatds a DataFrame
based on the the users selection.
"""
filters=get_filters()
#print(filters[0])
city_filter=filters[0].lower()

city_data = { 'chicago': 'chicago.csv',
              'new york city': 'new_york_city.csv',
              'washington': 'washington.csv' }

df= pd.DataFrame(pd.read_csv(city_data[filters[0].lower()]))

############ BUILD FEATURES & DEFINE DATA TYPES ################
""" We now set the data types and build new features in the selected dataframe
to support our analysis"""

df[['Start Time','End Time']]=df[['Start Time','End Time']].apply(pd.to_datetime)
df[['Start Time','End Time']]=df[['Start Time','End Time']].apply(pd.to_datetime)
df['month']=pd.DatetimeIndex(df['Start Time']).year
df['month']=pd.DatetimeIndex(df['Start Time']).month
df['year']=pd.DatetimeIndex(df['Start Time']).year
df['day']=pd.DatetimeIndex(df['Start Time']).dayofweek
df['month_name'] = df['Start Time'].dt.month_name()
df['day_of_week'] = df['Start Time'].dt.day_name()

#Create Trip Duration Categories
bins = [0,60,120,300, 600, 900, 1200, 1500, np.inf]
names = ['<1hr', '1-2hr', '2-5hr','5-10hr','10-15hr','15hr-20hr', '20hr-25hr', '25hr+']
df['TripDurationRange'] = pd.cut(df['Trip Duration'], bins, labels=names)

""" Ignore Approx_Age and Age Cagegory calculated features for city= Washington as Birth Year
and Gender are missing from the Washington CSV """
if filters[0] != 'washington':
    df['approx_age']=df['year']-df['Birth Year']

    #Create Age Categories
    bins = [0, 10, 18, 25, 35, 45, 55, 65, np.inf]
    names = ['<10', '11-18', '19-25','26-35','36-45','46-55', '56-65', '65+']
    df['AgeRange'] = pd.cut(df['approx_age'], bins, labels=names)

############ FILTER DATA BY MONTH AND DAY ################
""" Filter dataframe based on the month and day of week selected by the user.  We use an if
statement to handle when the user selects ALL for either filter. Before comparing, we convert
the dataframe value to lowercase to match the filter."""

#filter by month
filtered_df=df
if filters[1]=='all':
    filtered_df
else: filtered_df[(filtered_df['month_name'].str.lower() == filters[1])]

#filter by day
if filters[2]=='all':
    filtered_df
else: filtered_df=filtered_df[(filtered_df['day_of_week'].str.lower() == filters[2])]

############ BUILD STATISTICS FROM SELECTED DATAFRAME ################

#Average trip duration
"""Calculate the Trip Duration field in the filtered dataframe. Mean() automatically ignores NULL records"""
avg_trip_duration=round(filtered_df['Trip Duration'].mean(),2)

#Most popular stations
'''Calculate the most popular stations in the filtered dataframe by grouping the data by
Start Station, counting the total number of records, then taking the top 5.'''
most_popular_stations=pd.DataFrame(filtered_df.groupby(by=["Start Station"]).size().nlargest(5))

#Least popular stations
least_popular_stations=pd.DataFrame(filtered_df.groupby(by=["Start Station"]).size().nsmallest(5))

#Distribution of riders by Gender. Age & Gender data not available for Washington.
'''For the Chicago and New York, group and count by gender, then calculate the percent of total
ignoring NULL values. The if statement is used to exlcude washington because Gender and Birth Year
were not collected from riders in that city'''
if filters[0] == 'washington':
    gender_group="***** Birth Year / Age demographic data not available for Washington *******"
else:
    gender_group=pd.DataFrame(filtered_df['Gender'].value_counts(normalize=True))

#Distribution of riders by Age Group. Age & Gender data not available for Washington.
if filters[0] == 'washington':
    age_group="***** Gender demographic data not available for Washington *******"
else:
    age_group=pd.DataFrame(filtered_df['AgeRange'].value_counts(normalize=True, sort=False))

#Distribution of riders by trip duration
trip_group=pd.DataFrame(filtered_df['TripDurationRange'].value_counts(normalize=True, sort=False))

############ RETURN STATISTICS TO USER ################

print('Got it! Here are the summary statistics for {}:\n'.format(filters[0]))
print()

#Total Number of Riders
'''Print the total number of riders for the timeframe selected'''
print('Total number of riders:\n')
print(len(filtered_df))
print()

#Average Trip Duration
'''Print the average trip duration the timeframe selected'''
print('Average trip duration in minutes:\n')
print(avg_trip_duration)
print()

#Most Popular Station
''' Print the most frequented stations based on the total count of starts at the station within the timeframe selected'''
print('Most frequented stations:\n')
print(most_popular_stations)
print()

#Least Popular Stations
''' Print the least frequented stations based on the total count of starts at the station within the timeframe selected'''
print('Least frequented stations:\n')
print(least_popular_stations)
print()

#Distribution of Riders by Trip Segment
''' Print the distribution (%) of riders that fall within the given trip length segments'''
print('Segmentation of riders by trip length:\n')
print(trip_group)
print()

'''Only prints demographic related statistics when Chicago or New York are selected '''
if filters[0] != 'washington':
    print('Segmentation of riders by Gender:\n')
    print(gender_group)
    print()
    print('Segmentation of riders by age group:\n')
    print(age_group)
    print()

print('Segmentation of riders by trip length:\n')
print(trip_group)
print()
print('We hope you found this information useful.\n')

############ ASK USER TO SEE RAW DATA ################
"""Ask user if they would like to see the raw data.  We use a While Loop to handle errors in the
response of the user."""

input_raw=None
input_raw =input('Would you like to see a sample of the raw data? Enter Yes or No. \n')
#input_raw_follow_up = input('Would you like to see more raw data? Enter Yes or No. \n')
answer=['yes','no']
input_raw=input_raw.lower()

#Return raw data if the user selects 'Yes'
'''The following set of while loops will ask the user if they would like to see a sample of the raw data. The first
loop will provide the first 5 records. The second loop will ask if they would like to see more. The second loop will continue to provide
the next 5 records until the user says replies 'No' '''

raw_data=0
while raw_data == 0:
    if (input_raw in answer) & (input_raw.lower() == 'yes'):
        print(filtered_df.head(5))
        break
    elif (input_raw in answer) & (input_raw.lower() == 'no'):
        print("Sounds good. Have a great day. \n")
        raw_data = 1
        break
    else:input_raw=input("Hmm...you're response doesn't look right. Please enter Yes or No. \n").lower()

#####################################
sample_start=0
sample_end=5
raw_data=1

while raw_data == 1:
    input_raw_follow_up =  None
    sample_start = sample_start + 5
    sample_end = sample_end +5
    input_raw_follow_up = input('Would you like to see more raw data? Enter Yes or No. \n')
    input_raw_follow_up=input_raw_follow_up.lower()

    if (input_raw_follow_up in answer) & (input_raw_follow_up.lower() == 'yes'):
        print(filtered_df.iloc[sample_start:sample_end])
        continue

    elif (input_raw_follow_up in answer) & (input_raw_follow_up.lower() == 'no'):
        raw_data == 2
        print("Sounds good. Have a great day. \n")
        break
    else: input_raw=input("Hmm...you're response doesn't look right. Please enter Yes or No. \n").lower()

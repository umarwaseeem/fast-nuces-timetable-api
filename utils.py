import pandas as pd

# this function will be called in a loop and unnecessary rows of all days dataframes will be dropped
def drop_top_rows(df):
    df.drop([0, 1, 2], axis=0, inplace=True)
    df.columns = df.iloc[0] # make time schedule the column name/header
    try:
        df = df[['Room', '08:30-09:50','10:00-11:20','11:30-12:50','01:00-02:20','02:30-03:50','03:55-05:15','05:20-06:40 ', '06:45-08:05']]
    except: # friday exceptional case
        df = df[['Room', '08:30-09:50','10:00-11:20','11:30-12:50','02:00-03:20','03:30-04:50','05:20-06:40 ','06:45-08:05']]
    df.drop([3], axis=0, inplace=True)
    return df

def separate_labs_and_classes(day, classes, labs):
    # finding the splitting point of labs and classes
    lab_df = day[day.eq('Lab').any(axis=1)]
    ind = list(lab_df.index)
    ind = ind[0]
    
    classes.append(day[:ind-4])
    
    lab_df = day[ind-4:]
    lab_df.columns = lab_df.iloc[0]
    try:
        lab_df = lab_df[['Lab','08:30-11:15','11:25-02:10','02:25-05:10','05:20 - 08:05 (inc. 10 min. break)  ']]
    except: 
        # friday exceptional case
        lab_df = lab_df[['Lab', '08:30-11:15', '02:25-05:10', '05:20 - 08:05 (inc. 10 min. break)  ']]
    lab_df.drop([ind], axis=0, inplace=True)
    labs.append(lab_df)

TimeTable = pd.ExcelFile("timetable_spring_2024.xlsx")

day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
week=[] # list to store dataframe of timetables of all days of the week
classes=[] # list to store dataframe of all classes of all days of the week
labs=[] # list to store dataframe of all labs of all days of the week

for day in day_names:
    temp = pd.read_excel(TimeTable, day)
    week.append(temp)
    
for day in week:
    day = drop_top_rows(day) # drop unncessary top rows
    separate_labs_and_classes(day, classes, labs) # separate lab data and class data
    # database is ready at this point

def find_lab(find, subject, day_names, i, fhandle): # parameters: dataframe, subject name
    lab = find['Lab']
    lab = list(lab)
    lab = lab.pop()    
    
    cond = find==subject
    find = find.transpose()
    find.columns = [i for i in range(len(find.columns))]
    cond=find[0]==subject
    find = find[cond]
    
    time = find.index
    time = list(time)
    time = time.pop()
    
    fhandle.write('Subject : ')
    fhandle.write(subject)
    fhandle.write('\n')
    fhandle.write('Lab : ')
    fhandle.write(lab)
    fhandle.write('\n')
    fhandle.write('Time : ')
    fhandle.write(time)
    fhandle.write('\n')
    fhandle.write('Day : ')
    fhandle.write(day_names[i])
    fhandle.write('\n')
#     print('Subject : ', subject)
#     print('Lab : ', lab)
#     print('Time : ', time)
#     print('Day : ', day_names[i])    
    
def find_class(find, subject, day_names, i, fhandle): # parameters: dataframe, subject name
    room = find['Room']
    room = list(room)
    room = room.pop()    
    
    cond = find==subject
    find = find.transpose()
    find.columns = [i for i in range(len(find.columns))]
    cond=find[0]==subject
    find = find[cond]
    
    time = find.index
    time = list(time)
    time = time.pop()
    
    fhandle.write('Subject : ')
    fhandle.write(subject)
    fhandle.write('\n')
    fhandle.write('Room : ')
    fhandle.write(room)
    fhandle.write('\n')
    fhandle.write('Time : ')
    fhandle.write(time)
    fhandle.write('\n')
    fhandle.write('Day : ')
    fhandle.write(day_names[i])
    fhandle.write('\n')
#     print('Subject : ', subject)
#     print('Room : ', room)
#     print('Time : ', time)
#     print('Day : ', day_names[i])


def find_details(subject, fhandle):
    # one df in list of dfs
    not_found_count=0
    for i in range(len((classes))):
        find = classes[i][classes[i].eq(subject).any(axis=1)]

        if len(find)==0: # important checks
            # user might have entered the name of a lab
            find=labs[i][labs[i].eq(subject).any(axis=1)]
            if len(find)==0:
                not_found_count+=1
                continue
                # search in next day
            else:
                find_lab(find, subject, day_names, i, fhandle)
        else:
            find_class(find, subject, day_names, i, fhandle)
    if not_found_count==5:
        print('No class or lab with name {} found.'.format(subject))

def map_days(day):
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    return days.index(day.strip())
    
def sort_timetable(timetable: str) -> pd.DataFrame():
    timetable = timetable.split('Subject')[1:]
    subject_title = []
    room = []
    time = []
    day = []
    for subject in timetable:
        details = subject.split('\n')
        subject_title.append(details[0].split(' : ')[1])
        room.append(details[1].split(' : ')[1])
        time.append(details[2].split(' : ')[1])
        day.append(details[3].split(' : ')[1])

    df = pd.DataFrame(list(zip(subject_title, room, time, day)), index = subject_title)
    df.columns = [ "Subject", 'Room', 'Time', 'Day']
    df['Day Number'] = df['Day'].apply(map_days)
    df = df.sort_values(by='Day Number')
    df.drop('Day Number', axis=1, inplace=True)

    # split time into start and end time
    df['Start-Time'] = df['Time'].apply(lambda x: x.split('-')[0])
    df['End-Time'] = df['Time'].apply(lambda x: x.split('-')[1])

    # drop the time column
    df.drop('Time', axis=1, inplace=True)

    return df

def generate_timetable(subjects: list) -> pd.DataFrame():
    fhandle = open('/tmp/unsorted_timetable.txt', 'w')
    for subject in subjects:
        find_details(subject, fhandle)
        fhandle.write('\n')
    #     print()    
    
    timetable = ''

    fhandle = open('/tmp/unsorted_timetable.txt', 'r')

    for line in fhandle:
        timetable += line

    df = sort_timetable(timetable)
    
    return df
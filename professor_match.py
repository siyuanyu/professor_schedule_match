import os
import numpy as np
import pandas as pd

from student import Student
from schedule_writer import ScheduleWriter

# -----CONSTANTS AND VARIABLES-----
CONST_STUDENT_DATA_PATH = "Data Files\Student Data - Feb 11.csv"
CONST_PROF_DATA_PATH = "Data Files\Professor Data - Feb 11.csv"
CONST_STUDENT_OUTPUT_PATH = "Data Files\Output\Student Schedules\Weekend 1 - Feb 11"
CONST_PROF_OUTPUT_PATH = "Data Files\Output\Professor Schedules"
CONST_WEEK = "Weekend 1"

# CONST_STUDENT_DATA_PATH = "Data Files\Student Data - Feb 25.csv"
# CONST_PROF_DATA_PATH = "Data Files\Professor Data - Feb 25.csv"
# CONST_STUDENT_OUTPUT_PATH = "Data Files\Output\Student Schedules\Weekend 2 - Feb 25"
# CONST_PROF_OUTPUT_PATH = "Data Files\Output\Professor Schedules"
# CONST_WEEK = "Weekend 2"

CONST_MAX_MEETING_SIZE = 20
CONST_SESSION_START_HEADER = "Start time"
CONST_SESSION_END_HEADER = "End time"
CONST_PREF_NAME_HEADER = "Preferred Name"
CONST_LEGAL_NAME_HEADER = "Legal Name"
CONST_OUT_DEPT_HEADER = 'Faculty Member 5 (out of department)'
CONST_OUT_DEPT_RESPONSE = "(out of department, listed below)"
CONST_PROF_PREF_HEADERS = ['Faculty Member 1','Faculty Member 2','Faculty Member 3','Faculty Member 4','Faculty Member 5']
CONST_REPLACE_PROF_HEADERS = ['Replace', 'Replace 2']

# -----PARSE DATA FILES-----
script_dir = os.path.dirname(__file__)
student_data = pd.read_csv(os.path.join(script_dir, CONST_STUDENT_DATA_PATH))
raw_prof_data = pd.read_csv(os.path.join(script_dir, CONST_PROF_DATA_PATH))
prof_data = pd.DataFrame.drop(raw_prof_data, columns= [CONST_SESSION_START_HEADER,CONST_SESSION_END_HEADER])
profdf = pd.DataFrame(prof_data)
prof_list = profdf.columns.values
prof_schedules = profdf.to_numpy()
prof_schedules = CONST_MAX_MEETING_SIZE*(prof_schedules == 'YES').astype(int)
session_data = pd.DataFrame(raw_prof_data, columns= [CONST_SESSION_START_HEADER,CONST_SESSION_END_HEADER])
num_sessions = prof_schedules.shape[0]

# -----OPTIMIZE SCHEDULES-----
students = {}
sessions_dict = {}
writer = ScheduleWriter()
student_schedule_path = os.path.join(script_dir, CONST_STUDENT_OUTPUT_PATH)
prof_schedule_path = os.path.join(script_dir, CONST_PROF_OUTPUT_PATH)

for x in range(num_sessions):
    meeting_roster = {}
    for prof in prof_list:
        meeting_roster[prof] = []
    sessions_dict[x] = meeting_roster

# Determine student schedules
for i in student_data.index:
    # Parse all necessary student data
    if pd.isnull(student_data[CONST_PREF_NAME_HEADER][i]):
        pref_name = None
    else:
        pref_name = student_data[CONST_PREF_NAME_HEADER][i]

    legal_name = student_data[CONST_LEGAL_NAME_HEADER][i]
    prof_interest = []
    replace_index = 0
    for header in CONST_PROF_PREF_HEADERS:
        if student_data[header][i] == CONST_OUT_DEPT_RESPONSE:
            prof_pref = student_data[CONST_OUT_DEPT_HEADER][i]
        else:
            prof_pref = student_data[header][i]

        if prof_pref not in prof_list:
            try:
                replace_header = CONST_REPLACE_PROF_HEADERS[replace_index]
                prof_interest.append(student_data[replace_header][i])
                replace_index += 1
            except IndexError:
                print("{} - No replacement for {}".format(legal_name, prof_pref))
        else:
            prof_interest.append(prof_pref)

    # Create new student object and optimize schedule
    new_student = Student(legal_name, pref_name, prof_interest)
    new_student.optimize_schedule(prof_list, prof_schedules, sessions_dict, num_sessions)
    students[legal_name] = new_student
    meeting_count, unique_check, unscheduled_interests = new_student.validate_schedule()

    if meeting_count != len(CONST_PROF_PREF_HEADERS):
        print("{}'s schedule does not have the correct amount of meetings scheduled: {} meetings".format(legal_name, meeting_count))
        print("Unscheduled interests: {}".format(unscheduled_interests))

    if not unique_check:
        print("{} does not have a unique schedule")

    # Write student schedule to CSV
    writer.write_student_schedule(
        student_schedule_path, new_student,
        session_data[CONST_SESSION_START_HEADER], session_data[CONST_SESSION_END_HEADER])

# Write professor schedules to CSV
for faculty in prof_list:
    writer.write_prof_schedule(
        prof_schedule_path, CONST_WEEK, faculty, sessions_dict, num_sessions,
        session_data[CONST_SESSION_START_HEADER], session_data[CONST_SESSION_END_HEADER])

print("Scheduling Complete!")

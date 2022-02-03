import csv
import os
from student import Student

class ScheduleWriter:
    '''Provides methods for writing formatted schedules to CSV files'''
    def __init__(self) -> None:
        pass

    def write_student_schedule(self, folder, student: Student, sess_start_info, sess_end_info):
        filepath = folder + '\{} Schedule.csv'.format(student.legal_name)
        with open(filepath, 'w', newline='') as csvfile:
            csvWriter = csv.writer(csvfile, delimiter=',',
                                    quoting=csv.QUOTE_MINIMAL)
            for i in range(len(student.schedule)):
                sess_header = 'Session{}'.format(i+1)
                row = [sess_header, sess_start_info[i], sess_end_info[i], student.schedule[i]]
                csvWriter.writerow(row)

    def write_prof_schedule(self, folder, week, prof_name, prof_schedules, num_sessions, sess_start_info, sess_end_info):
        folderpath = folder + '\{}'.format(prof_name)
        if not os.path.exists(folderpath):
            os.mkdir(folderpath)
        filepath = folderpath + '\{} Schedule.csv'.format(week)
        with open(filepath, 'w', newline='') as csvfile:
            csvWriter = csv.writer(csvfile, delimiter=',',
                                    quoting=csv.QUOTE_MINIMAL)
            for i in range(num_sessions):
                sess_header = 'Session{}'.format(i+1)
                studentsList = prof_schedules[i][prof_name]
                row = [sess_header, sess_start_info[i], sess_end_info[i]] + studentsList
                csvWriter.writerow(row)

import numpy as np
import pandas as pd
from pulp import *

class Student:
    '''Stores each student's info such as schedule, faculty interests, names, etc and provides method for optimizing meeting schedules'''
    def __init__(self, legal_name, pref_name, faculty_interest = []):
        self.legal_name = legal_name
        self.pref_name = pref_name
        self.faculty_interest = faculty_interest
        self.schedule = None

    def optimize_schedule(self, prof_list, prof_availability, sessions_dict, num_sessions):
        # Defining optimization goal of maximizing the objective.
        prob = LpProblem("Professor_Match", LpMaximize)

        # Create filtered faculty matrix for student's interests
        student_no_interest = np.setdiff1d(prof_list, self.faculty_interest)
        student_no_interest_indices = np.where(np.isin(prof_list, student_no_interest))
        interested_prof_avail = np.delete(prof_availability, student_no_interest_indices, 1)
        interested_prof_list = np.delete(prof_list, student_no_interest_indices)

        # Define range of meeting slots and professors
        meeting_slots = range(num_sessions)
        profs = range(interested_prof_avail.shape[1])

        # Create optimization variable
        meeting_matrix =  LpVariable.dicts("pair", [(i,j) for i in meeting_slots for j in profs] ,cat='Binary')

        # Define optimization objective
        prob += lpSum([interested_prof_avail[i][j] * meeting_matrix[(i,j)] for i in meeting_slots for j in profs])

        # -----constraints-----
        # 1) only one professor can be in a student's meeting slot at a time
        # 2) each professor can only be in a student's meeting slot once
        # 3) a student must meet with all of their desired professors
        for i in meeting_slots:
            prob += lpSum(meeting_matrix[(i,j)] for j in profs) <= 1
        for j in profs:
            prob += lpSum(meeting_matrix[(i,j)] for i in meeting_slots) <= 1
        prob += lpSum(meeting_matrix[(i,j)] for i in meeting_slots for j in profs) == interested_prof_avail.shape[1]
        prob.solve(PULP_CBC_CMD(msg=0))

        # Format for usability
        student_schedule = []
        for i in meeting_slots:
            meeting_count = 0
            for j in profs:
                if meeting_matrix[(i,j)].varValue == 1:
                    # Add to student's schedule
                    student_schedule.append(interested_prof_list[j])
                    meeting_count += 1

                    # Update overall faculty schedule weights and add to sessions dictionary
                    current_prof = interested_prof_list[j]
                    prof_index = np.where(np.isin(prof_list, current_prof))
                    prof_availability[i,prof_index] -= 1
                    if self.pref_name is None:
                        formatted_name = self.legal_name
                    else:
                        formatted_name = "{} ({})".format(self.legal_name,self.pref_name)
                    sessions_dict[i][current_prof].append(formatted_name)
            if meeting_count == 0:
                student_schedule.append(None)
        self.schedule = student_schedule
        return student_schedule

    def validate_schedule(self):
        prof_list = []
        for prof in self.schedule:
            if prof is not None:
                prof_list.append(prof)

        num_meetings = len(prof_list)
        unique_check = len(set(prof_list)) == len(prof_list)
        unscheduled_interests = list(set(self.faculty_interest) - set(prof_list))
        return num_meetings, unique_check, unscheduled_interests

if __name__ == '__main__':
    names =['Ben','Kate','Thinh','Jorge','Alfredo','Francisco']
    c = np.array([
            [0, 10, 1, 1, 1, 1],
            [0, 1, 1, 1, 0, 10],
            [1, 1, 0, 1, 10, 0],
            [1, 0, 1, 10, 0, 0],
            [0, 1, 1, 0, 20, 0],
            [10, 1, 30, 0, 10, 1]
        ])

    sessions_dict = {}
    for x in range(6):
        faculty_dict = {}
        for faculty in names:
            faculty_dict[faculty] = []
        sessions_dict[x] = faculty_dict
    student1 = Student('Siyuan Yu', 'Ryan', ['Jorge','Ben','Kate','Francisco'])
    print(student1.optimize_schedule(names, c, sessions_dict, c.shape[0]))
    print(student1.validate_schedule())
    print(c)

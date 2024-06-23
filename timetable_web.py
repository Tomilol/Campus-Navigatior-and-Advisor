import streamlit as st
import pandas as pd
import base64
from PIL import Image
import json
from fuzzywuzzy import process
import threading

# Function to generate study timetable
def generate_study_timetable(class_timetable, extracurricular_activities, course_difficulty_ranking, study_preference, weekend_plans):
    # Define study times based on study preference
    if study_preference == 'morning':
        study_times = ['4am-5am', '5am-6am', '6am-7am', '7am-8am', '8am-9am']
    elif study_preference == 'evening':
        study_times = ['7pm-8pm', '8pm-9pm', '9pm-10pm', '10pm-11pm', '11pm-12am']
    else:
        study_times = ['4am-5am', '5am-6am', '6am-7am', '7am-8am', '8am-9am']  # Default to morning if preference is not specified

    # Initialize timetable
    timetable = {
        'Monday': [],
        'Tuesday': [],
        'Wednesday': [],
        'Thursday': [],
        'Friday': [],
        'Saturday': [],
        'Sunday': []
    }

    # Assign more time for studying to more difficult courses
    course_index = 0
    for day, slots in timetable.items():
        if day in class_timetable:
            slots += [f'Class {slot}' for slot in class_timetable[day].split(',')]
        if day in extracurricular_activities:
            slots += extracurricular_activities[day]

        # Assign study times based on course difficulty ranking
        for time in study_times:
            if course_index < len(course_difficulty_ranking):
                course = course_difficulty_ranking[course_index]
                slots.append(f'Study {course} {time}')
                course_index += 1
            else:
                break

        # Add weekend plans
        if day == 'Saturday' or day == 'Sunday':
            if day in weekend_plans:
                slots += weekend_plans[day]

        # Add break times
        if len(slots) > 0:
            slots.append(f'Break 1hr')

        timetable[day] = slots

    return timetable

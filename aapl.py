import pandas as pd
import requests
import streamlit as st
from PIL import Image
from fuzzywuzzy import process
import json
import subprocess
import threading
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet


from actions.actions import ActionProvideStudyTips, ActionSetVarkResults
from timetable_web import generate_study_timetable

# Function to get response from Rasa
def get_rasa_response(user_input):
    try:
        response = requests.post(
            'http://localhost:5005/webhooks/rest/webhook',  # Update the port if needed
            json={"sender": "user", "message": user_input}
        )
        response.raise_for_status()  # Raise an HTTPError for bad responses
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error: {e}")
        return []

# Function to start Flask app for directions
def start_flask_app():
    subprocess.Popen(["python", "app2.py"])  # Replace with your Flask app start command

# Function to get directions from Flask backend
def get_directions(origin, destination):
    try:
        response = requests.post(
            'http://127.0.0.1:5000/get_directions',
            json={"origin": origin, "destination": destination}
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error: {e}")
        return None

# Create a mock Tracker for testing
def create_mock_tracker():
    sender_id = "test_user"
    slots = {"slot_name": "slot_value"}
    latest_message = {"text": "Hello"}
    events = []
    paused = False
    followup_action = None
    active_loop = {}
    latest_action_name = "action_listen"

    return Tracker(
        sender_id=sender_id,
        slots=slots,
        latest_message=latest_message,
        events=events,
        paused=paused,
        followup_action=followup_action,
        active_loop=active_loop,
        latest_action_name=latest_action_name,
    )

# Set page configuration
st.set_page_config(
    page_title="School Assistant Chatbot",
    page_icon=":school:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load and display a header image
#image = Image.open(r'C:\Users\DELL\Documents\Chatbot_Project\logo2\logo.jpeg')  # Update with your logo path
#st.image(image, caption='School Logo', use_column_width=True)
sidebar_image = Image.open(r'C:\Users\DELL\Documents\Chatbot_Project\logo2\logo.jpeg')  # Update with your logo path
sidebar_image = sidebar_image.resize((150, 150))  # Resize logo to fit the sidebar
st.sidebar.image(sidebar_image, caption='School Logo', use_column_width=False)
# Main title and description
st.title("Welcome to School Chatbot")
st.write("Ask me anything about your school!")

# Sidebar for feature selection
st.sidebar.title('Navigation')
feature_selected = st.sidebar.radio("Select Feature", ('Home', 'Navigate Around Campus', 'Study Tips', 'Communication Channels', 'Generate Study Timetable'))

# Define feature icons
feature_icons = {
    'Navigate Around Campus': '🗺️',
    'Study Tips': '📚',
    'Communication Channels': '📞',
    'Generate Study Timetable': '🗓️'
}

# Feature Cards
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.image("https://via.placeholder.com/150", caption="Home")
    if st.button("Home"):
        st.session_state.feature = "home"

with col2:
    st.image("https://via.placeholder.com/150", caption=f"{feature_icons['Navigate Around Campus']} Navigate Around Campus")
    if st.button("Navigate Around Campus"):
        st.session_state.feature = "navigate"

with col3:
    st.image("https://via.placeholder.com/150", caption=f"{feature_icons['Study Tips']} Study Tips")
    if st.button("Study Tips"):
        st.session_state.feature = "study_tips"

with col4:
    st.image("https://via.placeholder.com/150", caption=f"{feature_icons['Communication Channels']} Communication Channels")
    if st.button("Communication Channels"):
        st.session_state.feature = "communication_channels"

with col5:
    st.image("https://via.placeholder.com/150", caption=f"{feature_icons['Generate Study Timetable']} Generate Study Timetable")
    if st.button("Generate Study Timetable"):
        st.session_state.feature = "generate_timetable"


# Render selected feature
if feature_selected == 'Home' or st.session_state.get('feature') == 'home':
    st.header("Welcome to School Assistant Chatbot")
    st.write("""
        This is your one-stop solution to get all information related to your school. 
        Use the navigation bar or feature cards above to explore the features.
    """)

elif feature_selected == 'Navigate Around Campus' or st.session_state.get('feature') == 'navigate':
    st.header("Navigate Around Campus")

    origin = st.text_input("Current Location")
    destination = st.text_input("Destination")

    if st.button("Get Directions"):
        if origin and destination:
            directions = get_directions(origin, destination)
            if directions:
                st.subheader("Directions")
                st.write(directions['directions'])
                st.image(directions['static_map_url'])
            else:
                st.write("No directions found.")
        else:
            st.write("Please enter both origin and destination.")

elif feature_selected == 'Study Tips' or st.session_state.get('feature') == 'study_tips':
    st.header("Study Tips")

    user_input = st.text_input("Tell me about yourself and how you learn best.")

    if st.button("Submit"):
        if user_input:
            rasa_response = get_rasa_response(user_input)
            if rasa_response:
                dispatcher = CollectingDispatcher()
                action_set_vark_results = ActionSetVarkResults()
                action_provide_study_tips = ActionProvideStudyTips()

                tracker = create_mock_tracker()
                vark_results = action_set_vark_results.run(dispatcher, tracker, {})
                study_tips = action_provide_study_tips.run(dispatcher, tracker, {})

                st.write(study_tips)

                # Add interaction to chat history
                # add_to_chat_history(user_input, study_tips)
            else:
                st.write("No response from Rasa server.")
        else:
            st.write("Please provide some input.")

elif feature_selected == 'Communication Channels' or st.session_state.get('feature') == 'communication_channels':
    st.header("Communication Channels")

    issue = st.text_input("What do you need help with?")
    info_type = st.selectbox("Type of Information", ['All', 'Emails', 'Location'])  # New slot for specifying type of information

    if st.button("Get Information"):
        with open('contacts.json', 'r') as f:
            contacts = json.load(f)

        # Fuzzy matching to handle flexible input
        contact_info = process.extractOne(issue, [contact['issue'] for contact in contacts['contacts']])
        if contact_info[1] > 80:  # Adjust threshold as needed
            contact_info = next((contact for contact in contacts['contacts'] if contact['issue'] == contact_info[0]), None)
        else:
            contact_info = None

        if contact_info:
            if info_type == 'Emails':  # Return only email if specified
                message = f"Emails: " + ", ".join(contact_info['emails'])
            else:  # Return all information if not specified
                message = f"Contact Information for {contact_info['issue']}:\nPersonnel: {contact_info['personnel']}\n"
                if contact_info['emails']:
                    message += "Emails: " + ", ".join(contact_info['emails']) + "\n"
                if contact_info['location']:
                    message += f"Location: {contact_info['location']}"
        else:
            message = f"Sorry, I don't have information on your issue right now."

        st.write(message)

elif feature_selected == 'Generate Study Timetable' or st.session_state.get('feature') == 'generate_timetable':
    st.header("Generate Study Timetable")

    st.sidebar.title('User Inputs')
    class_timetable = {}
    extracurricular_activities = {}
    course_difficulty_ranking = []
    study_preference = ''
    weekend_plans = {}

    st.sidebar.header('Class Timetable')
    for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
        class_timetable[day] = st.sidebar.text_input(f'{day}: Enter class timings (comma-separated e.g., 8am-10am,3pm-5pm)')

    st.sidebar.header('Extracurricular Activities')
    for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
        extracurricular_activities[day] = st.sidebar.text_input(f'{day}: Enter activities (e.g., 6pm-8pm Service Unit meeting)')

    st.sidebar.header('Course Difficulty Ranking')
    for i in range(7):  # Assuming up to 7 courses for simplicity
        course_difficulty_ranking.append(st.sidebar.text_input(f'Course {i + 1}'))

    study_preference = st.sidebar.selectbox('Study Preference', ['Morning', 'Evening'])

    st.sidebar.header('Weekend Plans')
    for day in ['Saturday', 'Sunday']:
        weekend_plans[day] = st.sidebar.text_input(f'{day}: Enter plans (e.g., Study time, outings)')

    # Generate timetable based on inputs
    if st.sidebar.button('Generate Timetable'):
        timetable = generate_study_timetable(class_timetable, extracurricular_activities, course_difficulty_ranking, study_preference.lower(), weekend_plans)

        # Display timetable
        st.header('Generated Study Timetable')

        # Create a DataFrame to organize the timetable data
        #timetable_df = pd.DataFrame({day: pd.Series(slots) for day, slots in timetable.items()})
        
        # Display the timetable
        #st.dataframe(timetable_df.style.apply(lambda x: ['background: lightblue' if 'Study' in str(cell) else '' for cell in x]))
        # Convert timetable to a structured DataFrame
        timetable_df = pd.DataFrame()
        for day, activities in timetable.items():
            day_df = pd.DataFrame(activities, columns=[day])
            timetable_df = pd.concat([timetable_df, day_df], axis=1)

        # Fill NaN with empty strings for better display
        timetable_df.fillna('', inplace=True)

        # Apply styling to highlight study sessions
        def highlight_study(val):
            color = 'lightblue' if 'Study' in val else ''
            return f'background-color: {color}'
        
        st.dataframe(timetable_df.style.applymap(highlight_study))
# Footer
st.markdown("""
    <style>
        footer {
            visibility: hidden;
        }
        .footer {
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            background-color: #4CAF50;
            color: white;
            text-align: center;
            padding: 10px;
        }
    </style>
    <div class="footer">
        <p>© 2024 School Chatbot | Designed by Your Name</p>
    </div>
""", unsafe_allow_html=True)

# Start Flask app in a separate thread for directions
threading.Thread(target=start_flask_app).start()

# Run the Streamlit app
if __name__ == '__main__':
    st.run()


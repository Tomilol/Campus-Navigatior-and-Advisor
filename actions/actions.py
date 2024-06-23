from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet 
import json
from fuzzywuzzy import process
import re
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet 
import requests
import streamlit as st


# STUDY TIPS
class ActionSetVarkResults(Action):
    def name(self) -> Text:
        return "action_set_vark_results"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        user_message = tracker.latest_message.get('text', '')
        results = []

        # Define mapping of common terms to VARK categories
        vark_mapping = {
            'Visual':'visual','visual': 'V', 'v': 'V',
            'auditory': 'A', 'a': 'A', 'audio': 'A',
            'read/write': 'R', 'r': 'R', 'read': 'R', 'write': 'R',
            'kinesthetic': 'K', 'k': 'K'
        }

        # Extract VARK results from the user message
        for key, value in vark_mapping.items():
            if key in user_message.lower():
                results.append(value)

        if results:
            dispatcher.utter_message(text="Thanks for providing your VARK results.")
            return [SlotSet("vark_results", results)]
        else:
            dispatcher.utter_message(text="I didn't understand your VARK results. Please provide them in the format 'I am a V and A learner'.")
            return []

class ActionProvideStudyTips(Action):
    def name(self) -> str:
        return "action_provide_study_tips"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker, domain: Dict) -> List[Dict[Text, Any]]:
        
        vark_results = tracker.get_slot('vark_results')
        if not vark_results:
            dispatcher.utter_message(text="Please provide your VARK results first.")
            return []

        study_tips = self.generate_study_tips(vark_results)
        
        dispatcher.utter_message(text=study_tips)
        return []

    def generate_study_tips(self, results: List[str]) -> str:
        print("I actually ran")
        tips = {
            'V': (
                "1. Find a quiet place to study to avoid distractions. Read alone, study alone at first. "
                "2. Make your study notes colourful. Since you are stimulated by pictures or colours, use different coloured pens. "
                "3. Make charts, graphs, images. Interpret the notes with visuals that make sense to you. "
                "4. Outline your notes as it visually organizes the information in your mind. "
                "5. Sit in front in class. It helps you visualize and memorize the slides on the board as the lecturer teaches."
            ),
            'A': (
                "1. Record everything you can or learn. When you are reading, also record yourself so you can listen and playback. "
                "2. Find podcasts and YouTube videos and try to learn about the topic that way. "
                "3. Repeat facts out loud with your eyes closed. This helps you focus on what you are hearing and listen to your voice. "
                "4. Get a tutor or a study buddy. Since you like hearing things explained to you, group or study buddy learning is preferable compared to independent learning. "
                "5. Experiment with background music while you learn. Auditory learners don't like absolute silence or noise while they study. Try using music without lyrics; it could be ambient or classical music. Test out what kind of music works for you. "
                "6. Read out loud. In case you are in the library or quiet spaces, you could mouth or whisper as you study. "
                "7. Ask questions."
            ),
            'R': (
                "1. Read and write extensively, make notes, and use lists. "
                "2. Summarize your notes into your own words. "
                "3. Use bullet points and numbered lists to organize information. "
                "4. Read textbooks, handouts, and other written material thoroughly. "
                "5. Practice writing out your notes from memory."
            ),
            'K': (
                "1. Engage in hands-on activities, use physical objects, and practice by doing. "
                "2. Participate in labs, field trips, and practical exercises. "
                "3. Study in short bursts with frequent breaks to move around. "
                "4. Use flashcards, Notecards- write down and make physical notecards. "
                "5. Take active breaks- be physical and move around. "
                "6. Relate what you are learning to real-life situations either by using real-life circumstances like cooking or relating to actual happenings in the world. "
                "7. Have something to keep your hands and legs busy- such as squeezing a stress ball, foam rollers for your feet, fidget spinners. "
                "8. Be active while you study- study while your body is physically active. Go for a walk and take your notes with you, you could even try chewing a gum. "
                "9. Teach- find a partner or friend and teach what you have learnt. "
                "10. Act or Trace. Act out what you are learning so for courses like history act like the character you are studying about."
            )
        }
        
        study_tips = [tips[result] for result in results if result in tips]
        return " ".join(study_tips)



# actions.py
# Import Google Maps API client library
from googlemaps import Client as GoogleMapsClient

class ActionDirections(Action):

    def name(self) -> Text:
        return "action_directions"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        origin = tracker.get_slot("origin")
        destination = tracker.get_slot("destination")

        print(f"Origin: {origin}")
        print(f"Destination: {destination}")
        # Define custom locations that are not on Google Maps
        # Custom locations mapping
        custom_locations = {
        "100/200 Lab (H111)": "First Floor, CST",
        "Hall 107": "First Floor, CST",
        "Hall 108": "First Floor, CST",
        "Molecular Biology Research Laboratory": "First Floor, CST",
        "Hall 201": "Second Floor, CST",
        "Hall 202": "Second Floor, CST",
        "Hall 203": "Second Floor, CST",
        "Hall 204": "Second Floor, CST",
        "Software Engineering Laboratory": "Second Floor, CST",
        "Biology Teaching Laboratory": "Second Floor, CST",
        "Buttery": "Second Floor, CST",
        "Physics Departmental Library": "Second Floor, CST",
        "Department of Estate Management": "Second Floor, CST",
        "Dean of CST's office": "Second Floor, CST",
        "400 Level Physics Lab": "Second Floor, CST",
        "Building Technology Departmental Library": "Second Floor, CST",
        "Microbiology Teaching Lab": "Second Floor, CST",
        "Building Technology Computer Laboratory": "Second Floor, CST",
        "Hall 306": "Third Floor, CST",
        "Hall 307": "Third Floor, CST",
        "Hall 308": "Third Floor, CST",
        "Computer Lab": "Third Floor, CST",
        "Physics Dark Room (A312)": "Third Floor, CST",
        "Biochemistry Laboratory II": "Third Floor, CST",
        "Biochemistry Laboratory 1": "Third Floor, CST",
        "Hall 302- Physics 100lvl Laboratory": "Third Floor, CST",
        "Department of Computer and Information Sciences": "Third Floor, CST",
        "Computer and Information Sciences (CIS) Library": "Third Floor, CST",
        "Department of Building Technology": "Fourth Floor, CST",
        "Department of Architecture": "Fourth Floor, CST",
        "CST Conference Room": "Fourth Floor, CST"
        }

        # Check if origin and destination are in custom locations
        if origin in custom_locations:
            origin_address = custom_locations[origin]
        else:
            origin_address = origin  # Use original input if not custom location found

        if destination in custom_locations:
            destination_address = custom_locations[destination]
        else:
            destination_address = destination  # Use original input if not custom location found

        # Initialize Google Maps client with your API key
        gmaps = GoogleMapsClient(api_key='AIzaSyCRcTKldG7WcUGWKTSCoOKWzUHuAd0EHTs')

        # Fetch directions from Google Maps API
        directions_result = gmaps.directions(origin_address, destination_address, mode="driving")

        # Extract and format directions steps
        if directions_result:
            steps = directions_result[0]['legs'][0]['steps']
            directions_text = "\n".join([step['html_instructions'] for step in steps])
        else:
            directions_text = "Sorry, I could not find directions for that route."

        # Send directions back to the user
        dispatcher.utter_message(text=directions_text)

        return []
    
    def format_step(self, step: str) -> str:
        """
        Format the HTML instructions from Google Maps to be compatible with Telegram.
        """
        step = re.sub(r'<div.*?>|</div>', '', step)
        step = re.sub(r'<span.*?>|</span>', '', step)
        step = re.sub(r'<p.*?>|</p>', '\n', step)
        step = re.sub(r'<br.*?>', '\n', step)
        
        supported_html = ['b', 'i', 'code', 'pre', 'a', 'u', 's', 'tg-spoiler']
        for tag in supported_html:
            step = re.sub(rf'<{tag}.*?>', f'<{tag}>', step)
        
        return step

    def generate_static_map_url(self, origin: str, destination: str) -> str:
        """
        Generate a URL for the Google Static Map image.
        """
        base_url = "https://maps.googleapis.com/maps/api/staticmap"
        params = {
            "size": "600x400",
            "maptype": "roadmap",
            "markers": f"color:red|label:A|{origin}",
            "markers": f"color:blue|label:B|{destination}",
            "path": f"color:0x0000ff|weight:5|{origin}|{destination}",
            "key": 'AIzaSyDdxoBKQ2p8lJos07sUgCg3L6Ro8eaCxag'
        }
        
        params_str = "&".join(f"{key}={value}" for key, value in params.items())
        return f"{base_url}?{params_str}"


# COMMUNICATION CHANNEL


class ActionProvideContactInfo(Action):

    def name(self) -> Text:
        return "action_provide_contact_info"

    def run(self, dispatcher: CollectingDispatcher, 
            tracker: Tracker, 
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        issue = tracker.get_slot('issue')
        info_type = tracker.get_slot('info_type')  # New slot for specifying type of information

        with open('contacts.json', 'r') as f:
            contacts = json.load(f)

        # Fuzzy matching to handle flexible input
        contact_info = process.extractOne(issue, [contact['issue'] for contact in contacts['contacts']])
        if contact_info[1] > 80:  # Adjust threshold as needed
            contact_info = next((contact for contact in contacts['contacts'] if contact['issue'] == contact_info[0]), None)
        else:
            contact_info = None

        if contact_info:
            if info_type == 'email':  # Return only email if specified
                message = f"Emails: " + ", ".join(contact_info['emails'])
            else:  # Return all information if not specified
                message = f"Contact Information for {contact_info['issue']}:\nPersonnel: {contact_info['personnel']}\n"
                if contact_info['emails']:
                    message += "Emails: " + ", ".join(contact_info['emails']) + "\n"
                if contact_info['location']:
                    message += f"Location: {contact_info['location']}"
        else:
            message = f"Sorry, I don't have information on your issue right now."

        dispatcher.utter_message(text=message)
        return []

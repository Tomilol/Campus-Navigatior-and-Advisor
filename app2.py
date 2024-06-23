# flask_app.py

from flask import Flask,render_template, request, jsonify
import googlemaps

app = Flask(__name__)
gmaps = googlemaps.Client(key='AIzaSyDdxoBKQ2p8lJos07sUgCg3L6Ro8eaCxag')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_directions', methods=['POST'])
def get_directions():
    origin = request.json.get('origin')
    destination = request.json.get('destination')

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
    

    origin_address = custom_locations.get(origin, origin)
    destination_address = custom_locations.get(destination, destination)

    directions = gmaps.directions(origin_address, destination_address, mode="driving")

    if directions:
        steps = directions[0]['legs'][0]['steps']
        directions_text = "\n".join([step['html_instructions'] for step in steps])
        static_map_url = generate_static_map_url(origin_address, destination_address)
    else:
        directions_text = "Sorry, I could not find directions for that route."
        static_map_url = ""

    return jsonify({'directions': directions_text, 'static_map_url': static_map_url})

def generate_static_map_url(origin, destination):
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

if __name__ == '__main__':
    app.run( host='127.0.0.1', port=5000)

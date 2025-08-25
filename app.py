from flask import Flask, jsonify, request, send_from_directory
import json
import os

app = Flask(__name__)
DATA_FILE = 'components.json'

def load_components():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_components(components):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(components, f, indent=2)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/components', methods=['GET'])
def get_components():
    components = load_components()
    q = request.args.get('q', '').strip().lower()
    if q:
        filtered = []
        for c in components:
            def to_str(val):
                if val is None:
                    return ''
                if isinstance(val, list):
                    return ' '.join(str(x) for x in val).lower()
                return str(val).lower()

            # Prepare searchable strings from relevant fields
            fields_to_search = [
                c.get('ID'),
                c.get('Component_Name'),
                c.get('Tags'),
                c.get('Type'),
                c.get('Manufacturer'),
                c.get('Status'),
                c.get('Notes'),
                c.get('Location'),  # include Location in search
            ]
            combined_text = ' '.join(to_str(field) for field in fields_to_search)
            if q in combined_text:
                filtered.append(c)
        return jsonify(filtered)
    return jsonify(components)

@app.route('/api/components', methods=['POST'])
def add_component():
    components = load_components()
    new_comp = request.json

    # Validate required fields
    if not new_comp.get('ID') or not new_comp.get('Component_Name'):
        return jsonify({"error": "ID and Component_Name are required"}), 400

    # Ensure 'Location' field exists in the new component, default to empty string if not provided
    if 'Location' not in new_comp:
        new_comp['Location'] = ''

    # Check for duplicate ID
    for c in components:
        if c.get('ID') == new_comp.get('ID'):
            return jsonify({"error": "Component with this ID already exists"}), 400

    # Append new component
    components.append(new_comp)
    save_components(components)
    return jsonify(new_comp), 201

@app.route('/api/components/<string:comp_id>', methods=['PUT'])
def update_component(comp_id):
    components = load_components()
    data = request.json

    # Ensure 'Location' field exists
    if 'Location' not in data:
        data['Location'] = ''

    for i, c in enumerate(components):
        if c.get('ID') == comp_id:
            # Update the component
            components[i] = data
            save_components(components)
            return jsonify(data)
    return jsonify({"error": "Component not found"}), 404

@app.route('/api/components/<string:comp_id>', methods=['DELETE'])
def delete_component(comp_id):
    components = load_components()
    new_list = [c for c in components if c.get('ID') != comp_id]
    if len(new_list) == len(components):
        return jsonify({"error": "Component not found"}), 404
    save_components(new_list)
    return jsonify({"message": "Deleted successfully"})

if __name__ == '__main__':
    app.run(debug=True)
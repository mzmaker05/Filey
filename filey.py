import os
import json
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from datetime import datetime
import subprocess

app = Flask(__name__)
app.secret_key = 'a1234!'

# Define the folder where the Python files are located
FILES_DIR = '/Change to your location/'  # Change to your folder with Python files
NOTES_FILE = 'file_notes.json'  # JSON file to store notes and colors

# Load the notes and color tags from the JSON file
def load_notes():
    if os.path.exists(NOTES_FILE):
        with open(NOTES_FILE, 'r') as f:
            return json.load(f)
    return {}

# Save the notes and color tags to the JSON file
def save_notes(notes):
    with open(NOTES_FILE, 'w') as f:
        json.dump(notes, f, indent=4)

# Get the list of files and sort them based on criteria
def get_files(sort_by='name', order='asc'):
    files = []
    notes = load_notes()
    for file_name in os.listdir(FILES_DIR):
        if file_name.endswith('.py'):
            file_path = os.path.join(FILES_DIR, file_name)
            
            # Check if the note is a string, and convert it to a dictionary with 'note' and 'color' keys
            if isinstance(notes.get(file_name), str):
                notes[file_name] = {'note': notes[file_name], 'color': 'none'}
            
            file_info = {
                'name': file_name,
                'size': os.path.getsize(file_path),
                'modified': os.path.getmtime(file_path),
                'modified_readable': datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S'),
                'note': notes.get(file_name, {}).get('note', ''),  # Load the note for each file
                'color': notes.get(file_name, {}).get('color', 'none')  # Load the color tag for each file
            }
            files.append(file_info)

    # Sorting logic
    reverse = True if order == 'desc' else False
    if sort_by == 'name':
        files.sort(key=lambda x: x['name'].lower(), reverse=reverse)
    elif sort_by == 'size':
        files.sort(key=lambda x: x['size'], reverse=reverse)
    elif sort_by == 'modified':
        files.sort(key=lambda x: x['modified'], reverse=reverse)

    return files

@app.route('/')
def index():
    sort_by = request.args.get('sort_by', 'name')
    order = request.args.get('order', 'asc')
    files = get_files(sort_by=sort_by, order=order)
    return render_template('index.html', files=files, sort_by=sort_by, order=order)

# Route to delete a file
@app.route('/home/mz/ai/<filename>')
def delete_file(filename):
    try:
        os.remove(os.path.join(FILES_DIR, filename))
        flash(f'File {filename} deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting {filename}: {e}', 'danger')
    return redirect(url_for('index'))

# Route to rename a file
@app.route('/rename/<filename>', methods=['POST'])
def rename_file(filename):
    new_name = request.form.get('new_name')
    if new_name and new_name.endswith('.py'):
        try:
            os.rename(os.path.join(FILES_DIR, filename), os.path.join(FILES_DIR, new_name))
            notes = load_notes()
            notes[new_name] = notes.pop(filename, '')  # Rename the note
            save_notes(notes)
            flash(f'File {filename} renamed to {new_name} successfully!', 'success')
        except Exception as e:
            flash(f'Error renaming {filename}: {e}', 'danger')
    else:
        flash('Invalid file name. Ensure the new name ends with .py', 'danger')
    return redirect(url_for('index'))

# Route to run a Python file
@app.route('/run/<filename>')
def run_file(filename):
    try:
        # Call the shell script and pass the filename as an argument
        subprocess.Popen(['bash', 'run_script.sh', filename])
        flash(f'File {filename} is being executed in a new terminal tab.', 'success')
    except Exception as e:
        flash(f'Error running {filename}: {e}', 'danger')
    return redirect(url_for('index'))

# Route to open the file in the browser (acts as a simple download link)
@app.route('/open/<filename>')
def open_file(filename):
    file_path = os.path.join(FILES_DIR, filename)
    try:
        return send_file(file_path, as_attachment=False)  # Serve the file directly
    except Exception as e:
        flash(f'Error opening {filename}: {e}', 'danger')
        return redirect(url_for('index'))

# Route to update the note and color for a file
@app.route('/update_note/<filename>', methods=['POST'])
def update_note(filename):
    note = request.form.get('note')
    color = request.form.get('color')
    notes = load_notes()
    notes[filename] = {'note': note, 'color': color}  # Update or add the note and color for the file
    save_notes(notes)
    flash(f'Note and color for {filename} updated successfully.', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)


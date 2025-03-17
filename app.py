import csv
import re
import json
import datetime
from flask import Flask, render_template, request, redirect, url_for, Response
from collections import defaultdict

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# In-memory data stores
contacts = []
nodes = []
hierarchy_tree = defaultdict(list)
course_prefix_map = defaultdict(list)
college_depts = defaultdict(list)  # College to departments mapping
CONTACTS_CSV = 'contacts.csv'
CONTACTS_FIELDS = [
    'id', 'linkblue', 'first_name', 'last_name', 'primary_contact',
    'contact_type', 'college', 'department', 'course', 'prefix', 'level_type'
]
def load_hierarchy():
    global nodes, hierarchy_tree, course_prefix_map, college_depts
    with open('hierarchy.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            node = {
                'node_id': row['Node Id'],
                'caption': row['Node Caption'],
                'parent_id': row['Parent Node Id'],
                'level': int(row['Level']),
                'course_no': row['CourseNo'] if row['Level'] == '4' else None
            }
            
            # Build college-department relationships
            if node['level'] == 3:  # Department level
                parent_college = next((n for n in nodes if n['node_id'] == node['parent_id']), None)
                if parent_college:
                    college_depts[parent_college['caption']].append(node['caption'])
            
            if node['level'] == 4:
                parts = node['caption'].split(' ', 1)
                node['prefix'] = parts[0] if len(parts) > 1 else ''
                node['course_num'] = parts[1] if len(parts) > 1 else node['caption']
                course_prefix_map[node['prefix']].append(node)
            
            nodes.append(node)
            hierarchy_tree[node['parent_id']].append(node)

def validate_prefix(prefix, department_id):
    if not re.match(r'^[A-Za-z]{2,3}$', prefix):
        return False
    department_courses = [n for n in nodes if n['parent_id'] == department_id]
    return any(c['prefix'] == prefix.upper() for c in department_courses)

def validate_course_number(course):
    return re.match(r'^\d{3}$', course) is not None

def find_course_node(prefix, number, department_id):
    full_code = f"{prefix} {number}"
    return next((n for n in nodes 
               if n['level'] == 4 
               and n['course_no'] == full_code
               and n['parent_id'] == department_id), None)

def find_node(caption, level, parent_caption=None):
    for node in nodes:
        if node['caption'] == caption and node['level'] == level:
            if parent_caption:
                parent = next((n for n in nodes if n['node_id'] == node['parent_id']), None)
                if parent and parent['caption'] == parent_caption:
                    return node
            else:
                return node
    return None

def load_contacts():
    global contacts
    try:
        with open(CONTACTS_CSV, 'r') as f:
            reader = csv.DictReader(f)
            contacts = [{
                'id': int(row['id']),
                'linkblue': row['linkblue'],
                'first_name': row['first_name'],
                'last_name': row['last_name'],
                'primary_contact': row['primary_contact'].lower() == 'yes',
                'contact_type': row['contact_type'],
                'college': row['college'],
                'department': row['department'],
                'course': row['course'],
                'prefix': row['prefix'],
                'level_type': row['level_type']
            } for row in reader]
    except FileNotFoundError:
        contacts = []

def save_contacts():
    with open(CONTACTS_CSV, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=CONTACTS_FIELDS)
        writer.writeheader()
        for contact in contacts:
            # Create a copy to preserve original data types
            row = contact.copy()
            row['primary_contact'] = str(row['primary_contact']).lower()
            writer.writerow(row)

load_hierarchy()
load_contacts()

@app.route('/')
def index():
    unique_colleges = list({n['caption']: n for n in nodes if n['level'] == 2}.values())
    return render_template('index.html', contacts=contacts)

@app.route('/add', methods=['GET', 'POST'])
def add_contact():
    colleges = [n for n in nodes if n['level'] == 2]
    
    if request.method == 'POST':
        contact_type = request.form['contact_type']
        college = request.form['college']
        department = request.form.get('department', '')
        is_primary = request.form.get('primary_contact') == 'yes'
        error = None
        print(json.dumps(college_depts, indent=2))

        # Validation
        if contact_type == 'Department' and not department:
            error = "Department is required for department contacts"
        elif contact_type == 'College' and department:
            error = "College contacts cannot have a department selected"
        elif contact_type == 'College' and is_primary:
            existing = next((c for c in contacts 
                           if c['college'] == college 
                           and c['primary_contact'] 
                           and c['contact_type'] == 'College'), None)
            if existing:
                error = "Only one primary contact allowed per college"
        
        if error:
            return render_template('add_contact.html',
                                  colleges=colleges,
                                  college_depts=json.dumps(college_depts),
                                  error=error)

        new_contact = {
            'id': len(contacts) + 1,
            'linkblue': request.form['linkblue'],
            'first_name': request.form['first_name'],
            'last_name': request.form['last_name'],
            'primary_contact': 'Yes' if is_primary else 'No',
            'contact_type': 'Course Coordinator' if request.form.get('course_coordinator') else 'Department',
            'college': college,
            'department': department,
            'course': request.form.get('course', ''),
            'prefix': request.form.get('prefix', ''),
            'level_type': request.form['level_type']
        }

        # Additional validation for course coordinators
        if contact_type == 'Department' and request.form.get('course_coordinator'):
            prefix = request.form['prefix'].strip().upper()
            course = request.form['course'].strip()
            dept_node = find_node(department, 3, college)
            
            if not validate_prefix(prefix, dept_node['node_id']):
                error = f"Invalid prefix {prefix} for department {department}"
            elif course:  # Only validate course if provided
                if not validate_course_number(course):
                    error = "Course number must be 3 digits"
                elif not find_course_node(prefix, course, dept_node['node_id']):
                    error = f"Course {prefix} {course} not found in department"
        
            if error:
                return render_template('add_contact.html',
                                      colleges=colleges,
                                      college_depts=json.dumps(college_depts),
                                      error=error)

        contacts.append(new_contact)
        save_contacts()
        return redirect(url_for('index'))
    print(json.dumps(college_depts, indent=2))

    return render_template('add_contact.html',
                          colleges=colleges,
                          college_depts=json.dumps(college_depts),
                          hierarchy_tree=json.dumps(hierarchy_tree))


@app.route('/edit/<int:contact_id>', methods=['GET', 'POST'])
def edit_contact(contact_id):
    contact = next((c for c in contacts if c['id'] == contact_id), None)
    if not contact:
        return redirect(url_for('index'))

    if request.method == 'POST':
        contact.update({
            'linkblue': request.form['linkblue'],
            'first_name': request.form['first_name'],
            'last_name': request.form['last_name'],
            'primary_contact': request.form.get('primary_contact') == 'yes',
            'college': request.form['college'],
            'department': request.form.get('department', 'All'),
            'course': request.form.get('course', ''),
            'prefix': request.form.get('prefix', ''),
            'level_type': request.form['level_type']
        })

        # Determine contact type
        if contact['department'] == 'All':
            contact['contact_type'] = 'College'
        elif not contact['course']:
            contact['contact_type'] = 'Department'
        else:
            contact['contact_type'] = 'Course Coordinator'

        # Validate primary contact
        if contact['primary_contact'] and contact['contact_type'] == 'College':
            existing = next((c for c in contacts if c['id'] != contact_id 
                            and c['college'] == contact['college'] 
                            and c['primary_contact'] 
                            and c['contact_type'] == 'College'), None)
            if existing:
                error = "Only one primary contact allowed per college"
                colleges = [n for n in nodes if n['level'] == 2]
                return render_template('edit_contact.html', contact=contact, colleges=colleges, error=error)
        save_contacts()  
        return redirect(url_for('index'))

    colleges = [n for n in nodes if n['level'] == 2]
    return render_template('edit_contact.html', contact=contact, colleges=colleges)

@app.route('/delete/<int:contact_id>')
def delete_contact(contact_id):
    global contacts
    # Remove the contact
    contacts = [c for c in contacts if c['id'] != contact_id]
    
    # Reassign sequential IDs
    for index, contact in enumerate(contacts, start=1):
        contact['id'] = index
    
    save_contacts()
    return redirect(url_for('index'))

@app.route('/export')
def export_contacts():
    output = []
    for contact in contacts:
        if contact['contact_type'] == 'College':
            node = find_node(contact['college'], 2)
            target_type = 'C4'
        elif contact['contact_type'] == 'Department':
            node = find_node(contact['department'], 3, contact['college'])
            target_type = 'D3'
        else:
            # Course Coordinator handling
            dept_node = find_node(contact['department'], 3, contact['college'])
            if contact['course']:
                # Single course
                node = find_node(f"{contact['prefix']} {contact['course']}", 4, contact['department'])
                if node:
                    output.append({
                        'source': node['node_id'],
                        'target': contact['linkblue'],
                        'targetType': 'CRS1'
                    })
            else:
                # All courses with prefix
                prefix_courses = [n for n in nodes 
                                if n['level'] == 4 
                                and n['parent_id'] == dept_node['node_id']
                                and n['prefix'] == contact['prefix']]
                for course_node in prefix_courses:
                    output.append({
                        'source': course_node['node_id'],
                        'target': contact['linkblue'],
                        'targetType': 'CRS1'
                    })
            continue

        if node:
            output.append({
                'source': node['node_id'],
                'target': contact['linkblue'],
                'targetType': target_type
            })

    csv_data = "source,target,targetType\n"
    csv_data += "\n".join([f"{row['source']},{row['target']},{row['targetType']}" for row in output])
    date = datetime.datetime.now().strftime("%Y%m%d")
    filename = f"ReportViewers_export_{date}.csv"
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename={filename}"}
        # headers={"Content-disposition": "attachment; filename=contacts_export.csv"}
    )

if __name__ == '__main__':
    app.run(debug=True)
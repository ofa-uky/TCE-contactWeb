import pandas as pd
import re

def process_class_number(cls):
    """Process CLASS numbers to ensure proper spacing for 2-character prefixes"""
    if pd.isna(cls):
        return ''
    
    # Remove whitespace and split into letters/numbers
    clean_cls = str(cls).strip().upper()
    match = re.match(r'^([A-Z]{2,})(\d+)$', clean_cls)  # Find prefix without space
    
    if match:
        prefix = match.group(1)
        numbers = match.group(2)
        
        # Insert space for 2-character prefixes
        if len(prefix) == 2:
            return f"{prefix} {numbers}"
        
        # Maintain existing spacing for longer prefixes
        return f"{prefix} {numbers}"
    
    # Return original if format doesn't match
    return clean_cls

# Load courses data
courses_df = pd.read_csv('Courses.csv')

# Initialize hierarchy list
hierarchy = []

# 1. Add University Node
hierarchy.append({
    'Node Id': 'University',
    'Node Caption': 'University',
    'Parent Node Id': '',
    'Parent Node Caption': '',
    'Level': 1,
    'CourseNo': ''
})

# 2. Process Colleges
unique_colleges = courses_df[['CLASS_COLLEGE_SHORT', 'CLASS_COLLEGE']].drop_duplicates()
for _, row in unique_colleges.iterrows():
    hierarchy.append({
        'Node Id': row['CLASS_COLLEGE_SHORT'],
        'Node Caption': row['CLASS_COLLEGE'],
        'Parent Node Id': 'University',
        'Parent Node Caption': 'University',
        'Level': 2,
        'CourseNo': ''
    })

# 3. Process Departments
unique_depts = courses_df[['CLASS_DEPARTMENT_ID', 'CLASS_DEPARTMENT', 
                          'CLASS_COLLEGE_SHORT', 'CLASS_COLLEGE']].drop_duplicates()
for _, row in unique_depts.iterrows():
    hierarchy.append({
        'Node Id': row['CLASS_DEPARTMENT_ID'],
        'Node Caption': row['CLASS_DEPARTMENT'],
        'Parent Node Id': row['CLASS_COLLEGE_SHORT'],
        'Parent Node Caption': row['CLASS_COLLEGE'],
        'Level': 3,
        'CourseNo': ''
    })

# 4. Process Classes
unique_classes = courses_df[['CLASS_ID', 'SECTION_TITLE', 'CLASS_DEPARTMENT_ID',
                            'CLASS_DEPARTMENT', 'CLASS']].drop_duplicates()
for _, row in unique_classes.iterrows():
    processed_class = process_class_number(row['CLASS'])
    hierarchy.append({
        'Node Id': row['CLASS_ID'],
        'Node Caption': row['SECTION_TITLE'],
        'Parent Node Id': row['CLASS_DEPARTMENT_ID'],
        'Parent Node Caption': row['CLASS_DEPARTMENT'],
        'Level': 4,
        'CourseNo': processed_class
    })

# Create DataFrame and save
hierarchy_df = pd.DataFrame(hierarchy)
hierarchy_df = hierarchy_df[['Node Id', 'Node Caption', 'Parent Node Id', 
                            'Parent Node Caption', 'Level', 'CourseNo']]
hierarchy_df.to_csv('hierarchy.csv', index=False)

print("Successfully generated hierarchy.csv")
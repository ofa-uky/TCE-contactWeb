import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import datetime

# Load and preprocess data (replace with your actual file paths)
def load_data():
    # Load courses data with explicit dtype for problem column
    courses = pd.read_csv('courses.csv', dtype={'column_31': str})  # Replace 'column_31' with actual column name
    courses = courses[['SECTION_KEY', 'TCE_INVITE', 'TCE_END_DATE']]
    courses['TCE_INVITE'] = pd.to_datetime(courses['TCE_INVITE'], errors='coerce')
    courses['TCE_END_DATE'] = pd.to_datetime(courses['TCE_END_DATE'], errors='coerce')
    
    # Drop rows with invalid dates
    courses = courses.dropna(subset=['TCE_INVITE', 'TCE_END_DATE'])
    
    # Load student-course data
    student_courses = pd.read_csv('Student_Course.csv')
    
    # Count students per course
    student_counts = student_courses.groupby('SECTION_KEY')['USER_ID'].nunique().reset_index()
    student_counts.columns = ['SECTION_KEY', 'STUDENT_COUNT']
    
    # Merge with courses data
    merged = pd.merge(courses, student_counts, on='SECTION_KEY', how='left')
    
    # Filter for courses with >5 students and in 2025
    merged = merged[merged['STUDENT_COUNT'] > 5]
    merged = merged[
        (merged['TCE_INVITE'].dt.year == 2025) | 
        (merged['TCE_END_DATE'].dt.year == 2025)
    ]
    
    return merged

data = load_data()

# Filter for June-August 2025
summer_data = data[
    ((data['TCE_INVITE'].dt.month >= 6) & (data['TCE_INVITE'].dt.month <= 8)) |
    ((data['TCE_END_DATE'].dt.month >= 6) & (data['TCE_END_DATE'].dt.month <= 8))
].copy()

# Add duration column for visualization
summer_data['DURATION'] = (summer_data['TCE_END_DATE'] - summer_data['TCE_INVITE']).dt.days

# Create Dash app
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Course Evaluation Schedule Dashboard", style={'textAlign': 'center'}),
    
    html.Div([
        html.Div([
            html.H3("Evaluation Timeline (June-August 2025)"),
            dcc.Graph(id='timeline-graph')
        ], style={'width': '80%', 'display': 'inline-block'}),
        
        html.Div([
            html.H3("Course Statistics"),
            html.Div(id='course-stats')
        ], style={'width': '18%', 'display': 'inline-block', 'verticalAlign': 'top'})
    ]),
    
    html.Div([
        html.H3("Downtime Finder"),
        html.P("Potential downtime periods with no evaluations:"),
        html.Ul(id='downtime-list')
    ])
])

@app.callback(
    [Output('timeline-graph', 'figure'),
     Output('course-stats', 'children'),
     Output('downtime-list', 'children')],
    [Input('timeline-graph', 'hoverData')]
)
def update_dashboard(hover_data):
    # Create timeline visualization
    fig = px.timeline(
        summer_data,
        x_start="TCE_INVITE",
        x_end="TCE_END_DATE",
        y="SECTION_KEY",
        color="STUDENT_COUNT",
        color_continuous_scale='Viridis',
        title="Course Evaluation Periods",
        hover_data={
            'SECTION_KEY': True, 
            'STUDENT_COUNT': True, 
            'TCE_INVITE': '|%b %d, %Y', 
            'TCE_END_DATE': '|%b %d, %Y',
            'DURATION': True
        },
        labels={
            'SECTION_KEY': 'Course', 
            'STUDENT_COUNT': 'Students',
            'DURATION': 'Duration (days)'
        }
    )
    
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(height=600)
    
    # Calculate statistics
    total_courses = len(summer_data)
    avg_students = summer_data['STUDENT_COUNT'].mean()
    active_days = summer_data['DURATION'].mean()
    
    stats = [
        html.P(f"Total Courses: {total_courses}"),
        html.P(f"Avg Students/Course: {avg_students:.1f}"),
        html.P(f"Avg Evaluation Duration: {active_days:.1f} days")
    ]
    
    # Find downtime periods
    timeline = []
    for _, row in summer_data.iterrows():
        timeline.append((row['TCE_INVITE'], 'start'))
        timeline.append((row['TCE_END_DATE'], 'end'))
    
    timeline.sort(key=lambda x: x[0])
    
    downtime_periods = []
    active_evaluations = 0
    prev_time = datetime.datetime(2025, 6, 1)
    
    for time, event in timeline:
        if active_evaluations == 0 and prev_time < time:
            downtime_periods.append((prev_time, time))
        
        if event == 'start':
            active_evaluations += 1
        else:
            active_evaluations -= 1
        
        prev_time = time
    
    # Add potential downtime after last evaluation ends
    last_day = datetime.datetime(2025, 8, 31, 23, 59, 59)
    if active_evaluations == 0 and prev_time < last_day:
        downtime_periods.append((prev_time, last_day))
    
    # Filter meaningful downtimes (at least 1 day)
    meaningful_downtimes = [
        (start, end) for start, end in downtime_periods 
        if (end - start) >= datetime.timedelta(days=1)
    ]
    
    downtime_items = [
        html.Li(f"{start.strftime('%b %d')} to {end.strftime('%b %d')} ({(end-start).days} days)")
        for start, end in meaningful_downtimes
    ] or [html.Li("No significant downtime periods found")]
    
    return fig, stats, downtime_items

if __name__ == '__main__':
    app.run(debug=True)  # Changed from app.run_server()
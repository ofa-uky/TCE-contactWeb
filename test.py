import pandas as pd
from datetime import datetime, timedelta
import numpy as np

def calculate_longest_evaluation_gap(csv_file_path):
    """
    Calculate the longest time period with no course evaluations.
    
    Args:
        csv_file_path (str): Path to the CSV file containing course data
    
    Returns:
        dict: Dictionary containing gap information
    """
    
    # Read the CSV file
    try:
        df = pd.read_csv(csv_file_path)
    except FileNotFoundError:
        print(f"Error: File '{csv_file_path}' not found.")
        return None
    
    # Clean and prepare the data
    # Remove rows where TCE_INVITE or TCE_END_DATE are missing/null
    df_clean = df.dropna(subset=['TCE_INVITE', 'TCE_END_DATE'])
    
    if df_clean.empty:
        print("No valid evaluation data found.")
        return None
    
    # Convert date columns to datetime
    df_clean['TCE_INVITE'] = pd.to_datetime(df_clean['TCE_INVITE'])
    df_clean['TCE_END_DATE'] = pd.to_datetime(df_clean['TCE_END_DATE'])
    
    # Create evaluation periods (each course has an evaluation period from invite to end)
    evaluation_periods = []
    
    for _, row in df_clean.iterrows():
        evaluation_periods.append({
            'course': row['SECTION_KEY'],
            'start': row['TCE_INVITE'],
            'end': row['TCE_END_DATE'],
            'term': row['ACADEMIC_TERM']
        })
    
    # Sort evaluation periods by start date
    evaluation_periods.sort(key=lambda x: x['start'])
    
    # Find gaps between evaluation periods
    gaps = []
    
    for i in range(len(evaluation_periods) - 1):
        current_end = evaluation_periods[i]['end']
        next_start = evaluation_periods[i + 1]['start']
        
        # Check if there's a gap (next evaluation starts after current one ends)
        if next_start > current_end:
            gap_duration = (next_start - current_end).days
            gaps.append({
                'gap_start': current_end,
                'gap_end': next_start,
                'duration_days': gap_duration,
                'previous_course': evaluation_periods[i]['course'],
                'next_course': evaluation_periods[i + 1]['course'],
                'previous_term': evaluation_periods[i]['term'],
                'next_term': evaluation_periods[i + 1]['term']
            })
    
    if not gaps:
        return {
            'longest_gap_days': 0,
            'message': 'No gaps found - evaluation periods overlap or are continuous',
            'total_evaluation_periods': len(evaluation_periods),
            'date_range': f"{evaluation_periods[0]['start'].date()} to {evaluation_periods[-1]['end'].date()}"
        }
    
    # Find the longest gap
    longest_gap = max(gaps, key=lambda x: x['duration_days'])
    
    # Calculate summary statistics
    total_gap_days = sum(gap['duration_days'] for gap in gaps)
    average_gap_days = total_gap_days / len(gaps) if gaps else 0
    
    return {
        'longest_gap_days': longest_gap['duration_days'],
        'longest_gap_start': longest_gap['gap_start'].date(),
        'longest_gap_end': longest_gap['gap_end'].date(),
        'previous_course': longest_gap['previous_course'],
        'next_course': longest_gap['next_course'],
        'previous_term': longest_gap['previous_term'],
        'next_term': longest_gap['next_term'],
        'total_gaps_found': len(gaps),
        'total_gap_days': total_gap_days,
        'average_gap_days': round(average_gap_days, 1),
        'all_gaps': gaps,
        'total_evaluation_periods': len(evaluation_periods),
        'evaluation_date_range': f"{evaluation_periods[0]['start'].date()} to {evaluation_periods[-1]['end'].date()}"
    }

def print_gap_analysis(results):
    """Print a formatted analysis of the evaluation gaps."""
    
    if results is None:
        return
    
    if results['longest_gap_days'] == 0:
        print("=== EVALUATION GAP ANALYSIS ===")
        print(results['message'])
        print(f"Total evaluation periods analyzed: {results['total_evaluation_periods']}")
        print(f"Date range: {results['date_range']}")
        return
    
    print("=== EVALUATION GAP ANALYSIS ===")
    print(f"Longest gap without evaluations: {results['longest_gap_days']} days")
    print(f"Gap period: {results['longest_gap_start']} to {results['longest_gap_end']}")
    print(f"Previous course: {results['previous_course']} ({results['previous_term']})")
    print(f"Next course: {results['next_course']} ({results['next_term']})")
    print()
    print("=== SUMMARY STATISTICS ===")
    print(f"Total gaps found: {results['total_gaps_found']}")
    print(f"Total days without evaluations: {results['total_gap_days']} days")
    print(f"Average gap length: {results['average_gap_days']} days")
    print(f"Total evaluation periods: {results['total_evaluation_periods']}")
    print(f"Evaluation date range: {results['evaluation_date_range']}")
    
    if results['total_gaps_found'] > 1:
        print("\n=== ALL GAPS ===")
        for i, gap in enumerate(results['all_gaps'], 1):
            print(f"{i}. {gap['duration_days']} days ({gap['gap_start'].date()} to {gap['gap_end'].date()})")

# Example usage
if __name__ == "__main__":
    # Replace 'Courses copy.csv' with your actual file path
    csv_file = 'Courses.csv'
    
    print("Analyzing course evaluation gaps...")
    results = calculate_longest_evaluation_gap(csv_file)
    print_gap_analysis(results)
    
    # Optional: Save detailed results to a file
    if results and results['longest_gap_days'] > 0:
        try:
            import json
            with open('evaluation_gap_analysis.json', 'w') as f:
                # Convert datetime objects to strings for JSON serialization
                json_results = results.copy()
                json_results['longest_gap_start'] = str(json_results['longest_gap_start'])
                json_results['longest_gap_end'] = str(json_results['longest_gap_end'])
                
                for gap in json_results['all_gaps']:
                    gap['gap_start'] = gap['gap_start'].isoformat()
                    gap['gap_end'] = gap['gap_end'].isoformat()
                
                json.dump(json_results, f, indent=2, default=str)
            print("\nDetailed results saved to 'evaluation_gap_analysis.json'")
        except Exception as e:
            print(f"Could not save detailed results: {e}")
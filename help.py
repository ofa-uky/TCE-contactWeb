import pandas as pd
from collections import defaultdict

def analyze_course_quality(csv_file_path):
    """
    Analyze course and instructor quality scores by academic year and semester.
    
    Args:
        csv_file_path (str): Path to the CSV file containing course data
    
    Returns:
        dict: Grouped averages by semester
    """
    
    # Read the CSV file
    try:
        df = pd.read_csv(csv_file_path)
    except FileNotFoundError:
        print(f"Error: File '{csv_file_path}' not found.")
        return None
    except Exception as e:
        print(f"Error reading file: {e}")
        return None
    
    # Filter out rows where quality scores are 0 or NaN
    df_filtered = df[(df['SECT_CRS_QUAL20'] > 0) & (df['SECT_INS_QUAL21'] > 0)]
    
    # Create term labels combining ATERM and AYEAR
    def create_term_label(row):
        year = str(row['AYEAR'])
        term = str(row['PERSONID'])  # Pad with zeros to make it 3 digits
        return f"Term {term}-{year}"
    
    df_filtered['term'] = df_filtered.apply(create_term_label, axis=1)
    
    # Group by term and calculate means
    results = {}
    grouped = df_filtered.groupby('term')
    
    for term, group in grouped:
        course_mean = group['SECT_CRS_QUAL20'].mean()
        instructor_mean = group['SECT_INS_QUAL21'].mean()
        count = len(group)
        
        results[term] = {
            'course_mean': round(course_mean, 2),
            'instructor_mean': round(instructor_mean, 2),
            'count': count
        }
    
    return results

def print_results(results):
    """Print the results in a formatted way."""
    if not results:
        print("No results to display.")
        return
    
    print("Course and Instructor Quality Averages by Term")
    print("=" * 50)
    
    # Sort by term
    sorted_terms = sorted(results.keys())
    
    for term in sorted_terms:
        data = results[term]
        print(f"\n{term}")
        print(f"- Instructor mean = {data['instructor_mean']}")
        print(f"- Course mean = {data['course_mean']}")
        print(f"- Number of records = {data['count']}")

def analyze_sample_data():
    """Analyze the sample data provided in the question."""
    
    
    # Create term labels combining ATERM and AYEAR
    def create_term_label(row):
        year = str(row['AYEAR'])
        term = str(row['ATERM']).zfill(3)  # Pad with zeros to make it 3 digits
        print(f"Creating term label for ATERM: {row['ATERM']}, AYEAR: {year}")
        return f"Term {term}-{year}"
    
    df['term'] = df.apply(create_term_label, axis=1)
    
    # Group by term and calculate means
    results = {}
    grouped = df.groupby('term')
    
    for term, group in grouped:
        course_mean = group['SECT_CRS_QUAL20'].mean()
        instructor_mean = group['SECT_INS_QUAL21'].mean()
        count = len(group)
        
        results[term] = {
            'course_mean': round(course_mean, 2),
            'instructor_mean': round(instructor_mean, 2),
            'count': count
        }
    
    return results

# Main execution
if __name__ == "__main__":
    # print("=== SAMPLE DATA ANALYSIS ===")
    # sample_results = analyze_sample_data()
    # print_results(sample_results)
    
    # print("\n" + "="*60)
    print("To analyze your own CSV file, use:")
    print("results = analyze_course_quality('your_file.csv')")
    print("print_results(results)")
    
    results = analyze_course_quality('/Users/elnoelakwa/Downloads/data.csv')
    print_results(results)
    # Example usage with actual file:
    # results = analyze_course_quality('course_data.csv')
    # print_results(results)
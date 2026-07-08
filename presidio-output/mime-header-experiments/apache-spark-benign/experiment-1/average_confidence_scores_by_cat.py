import csv
import argparse
from collections import defaultdict

def get_average_scores(filename):
    score_sums = defaultdict(float)
    score_counts = defaultdict(int)

    try:
        with open(filename, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                entity = row['entity_type']
                score = float(row['score'])
                
                score_sums[entity] += score
                score_counts[entity] += 1
                
    except FileNotFoundError:
        print(f"Error: Could not find the file '{filename}'.")
        return

    print(f"{'Entity Type':<20} | {'Average Score'}")
    print("-" * 38)
    
    averages = {}
    for entity in score_sums:
        avg = score_sums[entity] / score_counts[entity]
        averages[entity] = avg
        print(f"{entity:<20} | {avg:.4f}")

    return averages

if __name__ == "__main__":
    # Set up the command-line argument parser
    parser = argparse.ArgumentParser(description="Calculate average confidence scores by entity type from a CSV.")
    parser.add_argument("csv_path", help="Path to the Presidio output CSV file")
    
    # Parse the arguments and pass the path to the function
    args = parser.parse_args()
    get_average_scores(args.csv_path)
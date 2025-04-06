import json
import time
import os
from tabulate import tabulate

def count_jsonl_items(file_path):
    """Count the number of items in a JSONL file."""
    try:
        with open(file_path, 'r') as file:
            count = sum(1 for _ in file)
        return count
    except FileNotFoundError:
        print(f"File {file_path} not found.")
        return None

def main():
    file_path = 'output/aime24_bz64.jsonl'
    previous_count = None
    
    while True:
        count = count_jsonl_items(file_path)
        if count is not None:
            table = [['Time', 'Count', '% Complete'],
                     [time.strftime('%Y-%m-%d %H:%M:%S'), count, f"{(count/1920)*100:.2f}%"]]
            os.system('clear')
            print(tabulate(table, headers='firstrow', tablefmt='rounded_grid'))
            previous_count = count
        time.sleep(5)  # Wait for 5 seconds

if __name__ == "__main__":
    main()

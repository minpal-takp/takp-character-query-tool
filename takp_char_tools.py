import requests
import sqlite3
import csv
from io import StringIO
import argparse
from tabulate import tabulate
import sys

# Constants
URL = "https://www.takproject.net/magelo/export/TAKP_character.txt"
DB_NAME = "takp_characters.db"
TABLE_NAME = "characters"

DEFAULT_COLUMNS = [
    "name", 
    "last_name", 
    "guild_name", 
    "hp_max_total", 
    "mana_max_total", 
    "ac_total", 
    "hp_regen_item", 
    "mana_regen_item"
]

def download_and_import_data():
    print("Downloading and importing character data...")
    response = requests.get(URL)
    response.raise_for_status()

    csv_data = StringIO(response.text)
    reader = csv.reader(csv_data, delimiter='\t')
    headers = next(reader)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    text_columns = {"name", "last_name", "guild_name", "deity", "gender", "class", "race"}
    columns_sql = []
    for header in headers:
        column_type = "TEXT" if header in text_columns else "INTEGER"
        columns_sql.append(f'"{header}" {column_type}')
    create_table_sql = f'''
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
        {', '.join(columns_sql)}
    )
    '''
    cursor.execute(create_table_sql)

    print("Clearing existing data from the characters table...")
    cursor.execute(f"DELETE FROM {TABLE_NAME}")

    placeholders = ', '.join(['?'] * len(headers))
    insert_sql = f'INSERT INTO {TABLE_NAME} VALUES ({placeholders})'

    for row in reader:
        if len(row) == len(headers):
            cursor.execute(insert_sql, row)

    conn.commit()
    conn.close()
    print("Data import complete.")

def get_column_headers():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({TABLE_NAME})")
    headers = [row[1] for row in cursor.fetchall()]
    conn.close()
    return headers

def query_characters(filter_column, filter_value, limit, order_by, selected_columns):
    headers = get_column_headers()

    if order_by not in headers:
        print(f"\nERROR: '{order_by}' is not a valid column name.")
        print("Available columns:\n")
        print(tabulate([[h] for h in sorted(headers)], headers=["Valid Columns"], tablefmt="grid"))
        sys.exit(1)

    for col in selected_columns:
        if col not in headers:
            print(f"\nERROR: '{col}' is not a valid column name.")
            print("Available columns:\n")
            print(tabulate([[h] for h in sorted(headers)], headers=["Valid Columns"], tablefmt="grid"))
            sys.exit(1)

    print(f"Querying by {filter_column}: {filter_value}, ordering by {order_by}, limit {limit}...")
    columns_sql = ", ".join(f'"{col}"' for col in selected_columns)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    query = f'''
    SELECT {columns_sql}
    FROM characters 
    WHERE "{filter_column}" = ? 
    ORDER BY "{order_by}" DESC 
    LIMIT ?
    '''
    cursor.execute(query, (filter_value, limit))
    results = cursor.fetchall()
    conn.close()

    if results:
        print("\nResults:\n")
        print(tabulate(results, headers=[col.replace("_", " ").title() for col in selected_columns], tablefmt="grid"))
    else:
        print("No matching characters found in the database.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="TAKP Character Importer and Query Tool",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
Examples:
  python script.py                        # Download and import data (default)
  python script.py --refresh-data        # Same as default: download and import data
  python script.py --class paladin       # Query top 10 Paladins by default columns
  python script.py --name Sirblade --columns name,class,guild_name
"""
    )

    parser.add_argument(
        '--class', dest='char_class',
        help="Query top characters by class name (e.g., Paladin)."
    )
    parser.add_argument(
        '--name', dest='char_name',
        help="Query a specific character by exact name."
    )
    parser.add_argument(
        '--limit', type=int, default=10,
        help="Number of results to return. Default is 10."
    )
    parser.add_argument(
        '--order-by', dest='order_by', default='hp_max_total',
        help="Column name to sort results by. Default is 'hp_max_total'."
    )
    parser.add_argument(
        '--columns',
        help="Comma-separated list of columns to include in output.\n"
             "Default:\n  name, last_name, guild_name, hp_max_total, mana_max_total, ac_total, hp_regen_item, mana_regen_item"
    )
    parser.add_argument(
        '--refresh-data', action='store_true',
        help="Download and import the latest character data (default action if no flags are used)."
    )

    args = parser.parse_args()

    # If no arguments passed (except script name), treat it as --refresh-data
    if len(sys.argv) == 1 or args.refresh_data:
        download_and_import_data()
        sys.exit(0)

    if args.char_name and args.char_class:
        print("ERROR: --name and --class cannot be used together. Please choose one.")
        sys.exit(1)

    if args.columns:
        selected_columns = [col.strip() for col in args.columns.split(",") if col.strip()]
    else:
        selected_columns = DEFAULT_COLUMNS

    if args.char_name:
        query_characters(
            filter_column="name",
            filter_value=args.char_name,
            limit=args.limit,
            order_by=args.order_by,
            selected_columns=selected_columns
        )
    elif args.char_class:
        query_characters(
            filter_column="class",
            filter_value=args.char_class.capitalize(),
            limit=args.limit,
            order_by=args.order_by,
            selected_columns=selected_columns
        )
    else:
        print("ERROR: No valid query specified. Use --class or --name.")
        sys.exit(1)
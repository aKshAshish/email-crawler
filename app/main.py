import argparse

from dotenv import load_dotenv
from rule import create_composite_rule
from db import init_db

def create_file_parser():
    parser = argparse.ArgumentParser(description='Specify the path to a file.')
    parser.add_argument(
        '-p', 
        '--path', 
        type=str, 
        required=False, 
        help='Path to rule file'
    )
    return parser

def main():
    parser = create_file_parser()
    args = parser.parse_args()

    path_to_rule = 'rule.json' if not args.path else args.path

    # Load environment variables
    load_dotenv()
    # Initialise DB
    init_db()

    try:
        composite_rule = create_composite_rule(path_to_rule)
        composite_rule.apply()
    except Exception as e:
        print(f"Following error occured {e}")


if __name__ == "__main__":
    main()





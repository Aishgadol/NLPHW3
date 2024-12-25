import json
from collections import defaultdict
import os
import re

# Define the path to the file located in the same directory as the script
file_path = os.path.join(os.path.dirname(__file__), "result_orig.jsonl")

# Titles and departments to remove from names
titles = [
    '<<.*>>', 'תשובת', 'הד"ר', 'ד"ר', 'מ"מ היו"ר', 'היו"ר', 'יו"ר', 'נשיא הפרלמנט האירופי', 'שר', 'שרת',
    'עו"ד', 'המשנה לראש הממשלה', 'משנה לראש הממשלה', 'ראש הממשלה', 'נצ"מ', 'מר', 'ניצב', 'טפסר משנה', 'רשף',
    "פרופ'", 'סגן', 'סגנית', 'השר', 'השרה', 'מזכיר', 'מזכירת', 'ועדת'
]
departments = [
    'הכנסת', 'הכלכלה', 'הכלכלה והתכנון', 'האנרגיה והמים', 'החינוך', 'החינוך והתרבות',
    'התשתיות הלאומיות', 'התשתיות הלאומיות, האנרגיה והמים', 'חינוך', 'המודיעין', 'לשיתוף פעולה אזורי',
    'ההסברה והתפוצות', 'האוצר', 'להגנת הסביבה', 'התעשייה, המסחר והתעסוקה', 'לאיכות הסביבה',
    'התרבות והספורט', 'התשתיות', 'המשפטים', 'הרווחה', 'הרווחה והשירותים החברתיים', 'הבינוי והשיכון',
    'התחבורה והבטיחות בדרכים', 'המשטרה', 'הבריאות', 'החקלאות ופיתוח הכפר', 'התקשורת',
    'במשרד ראש הממשלה', 'הפנים', 'הביטחון', 'לביטחון פנים', 'המדע והטכנולוגיה', 'העלייה והקליטה',
    'לקליטת העלייה', 'התיירות', 'החוץ', 'המדע,', 'למודיעין', 'לאזרחים ותיקים', 'לענייני דתות', 'לענייני מודיעין',
    'המדע', 'התרבות', 'הספורט', 'תרבות', 'ספורט'
]

# Compile a regex pattern to match titles and departments
# The pattern will remove any of the specified titles or departments from the speaker's name
bad_words_pattern = re.compile(rf"({'|'.join(map(re.escape, titles + departments))})", re.IGNORECASE)

# Function to normalize full names by removing titles and departments
def normalize_full_name(full_name):
    # Remove any titles or departments from the name
    cleaned_name = bad_words_pattern.sub("", full_name).strip()

    # Remove any extra spaces that might have been left after removal
    cleaned_name = re.sub(r'\s+', ' ', cleaned_name)

    return cleaned_name

# Initialize counter and set for variations
burg_count = 0
burg_variations = set()

# Read and process the JSONL file
try:
    with open(file_path, "r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            try:
                # Parse each line as JSON
                record = json.loads(line)
                if "speaker_name" in record:
                    speaker_name = record["speaker_name"]

                    # Normalize the speaker's full name by removing titles and departments
                    normalized_name = normalize_full_name(speaker_name)

                    # Split the normalized name to extract the last name
                    name_parts = normalized_name.split(" ")
                    if len(name_parts) >= 1:
                        last_name = name_parts[-1]

                        # Check if the last name is "בורג"
                        if last_name == "בורג":
                            burg_count += 1
                            burg_variations.add(speaker_name)
            except json.JSONDecodeError as e:
                print(f"JSON parsing error on line {line_number}: {e}")
                continue  # Skip lines with JSON errors

except FileNotFoundError:
    print(f"Error: File not found at {file_path}")
    exit()
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    exit()

# Print the results
print(f"Total number of sentences where the speaker's last name is 'בורג': {burg_count}")
print("\nVarious ways 'בורג' appears in the speaker_name column:")
for variation in sorted(burg_variations):
    print(f"- {variation}")

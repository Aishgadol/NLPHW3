import json
from collections import defaultdict
import os
import re

# Define the path to the file located in the same directory as the script
file_path = os.path.join(os.path.dirname(__file__), "result.jsonl")

# Updated predefined pairs of shortened (nicknames) and lengthened (full) names
nickname_map = {
    "בני": "בנימין",
    "יוסי": "יוסף",
    "אבי": "אברהם",
    "א'": "אברהם",          # Map "א'" to "אברהם"
    "אברהם": "אברהם",      # Ensure full name maps to itself
    "צחי": "יצחק",
    "איציק": "יצחק",
    "שמוליק": "שמואל",
    "מושי": "משה",
    "דודי": "דוד",
    "שוקי": "יהושע",
    "אלי": "אליהו",
    "מוטי": "מרדכי",
    "שלומי": "שלמה",
    "ריקי": "רבקה",
    "מירי": "מרים",
    "חני": "חנה",
    "ציפי": "ציפורה",
    "רחלי": "רחל",
    "אתי": "אסתר",
    "רובי": "ראובן",
    "ר'": "ראובן",          # Map "ר'" to "ראובן"
    "ראובן": "ראובן",        # Ensure full name maps to itself
}

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
bad_words_pattern = re.compile(rf"({'|'.join(map(re.escape, titles + departments))})", re.IGNORECASE)

# Normalize full names by handling shortened first names and cleaning up titles/departments
def normalize_full_name(full_name):
    # Remove any titles or departments from the name
    cleaned_name = bad_words_pattern.sub("", full_name).strip()

    # Remove any extra spaces that might have been left after removal
    cleaned_name = re.sub(r'\s+', ' ', cleaned_name)

    parts = cleaned_name.split(" ", 1)
    if len(parts) == 2:
        first_name, last_name = parts

        # Normalize first name if it's in the nickname map
        if first_name in nickname_map:
            first_name = nickname_map[first_name]
        else:
            # If first name is a single-letter initial without a mapping, remove it
            if re.match(r"^[א-ת]'", first_name):
                return last_name

        return f"{first_name} {last_name}"
    return cleaned_name  # Return as-is if it doesn't fit the expected structure

# A dictionary to uniquely identify speakers, regardless of name variations
unique_speaker_counter = defaultdict(int)

# A dictionary to map specific name variations to normalized names
variation_to_normalized = defaultdict(set)

# Read and process the JSONL file
try:
    with open(file_path, "r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            try:
                # Parse each line as JSON
                record = json.loads(line)
                if "speaker_name" in record:
                    speaker_name = record["speaker_name"]

                    # Normalize the speaker's full name
                    normalized_name = normalize_full_name(speaker_name)

                    # Increment the count for the normalized name
                    unique_speaker_counter[normalized_name] += 1

                    # Map the original variation to the normalized name
                    variation_to_normalized[normalized_name].add(speaker_name)
            except json.JSONDecodeError as e:
                print(f"JSON decoding error on line {line_number}: {e}")
                continue  # Skip lines with JSON errors
except FileNotFoundError:
    print(f"Error: File not found at {file_path}")
    exit()
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    exit()

# Get the top 5 most common unique speakers
top_speakers = sorted(unique_speaker_counter.items(), key=lambda x: x[1], reverse=True)[:5]

# Print the top 5 unique speakers
print("5 speakers with most sentences:")
for normalized_name, count in top_speakers:
    variations = variation_to_normalized[normalized_name]
    print(f"{normalized_name}: {count}")

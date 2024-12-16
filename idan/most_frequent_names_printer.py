import json
from collections import defaultdict, Counter
import os
import re

# Define the relative path to the file
file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "result_fixed.jsonl")

# Updated predefined pairs of shortened and lengthened names
nickname_map = {
    "בני": "בנימין",
    "יוסי": "יוסף",
    "אבי": "אברהם",
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
}

# Reverse map for quicker lookup
nickname_map.update({v: k for k, v in nickname_map.items()})

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
bad_words_pattern = re.compile(rf"({'|'.join(map(re.escape, titles + departments))})")

# Normalize full names by handling shortened first names and cleaning up titles/departments
def normalize_full_name(full_name):
    # Remove any titles or departments from the name
    full_name = bad_words_pattern.sub("", full_name).strip()

    parts = full_name.split(" ", 1)
    if len(parts) == 2:
        first_name, last_name = parts

        # Handle first names that are just a single letter (e.g., "ב'")
        if re.match(r"^[א-ת]'", first_name):  # Single-letter first name
            return f"{last_name}"  # Use only the last name for comparison

        # Normalize first name if it's in the nickname map
        for short, long in nickname_map.items():
            if first_name == short or first_name == long:
                first_name = long  # Normalize to the long form
                break

        return f"{first_name} {last_name}"
    return full_name  # Return as-is if it doesn't fit the expected structure

# A dictionary to uniquely identify speakers, regardless of name variations
unique_speaker_counter = defaultdict(int)

# A dictionary to map specific name variations to normalized names
variation_to_normalized = defaultdict(set)

# Read and process the JSONL file
try:
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
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
            except json.JSONDecodeError:
                continue
except FileNotFoundError:
    print(f"Error: File not found at {file_path}")
    exit()

# Get the top 10 most common unique speakers
top_speakers = sorted(unique_speaker_counter.items(), key=lambda x: x[1], reverse=True)[:10]

# Print the top 10 unique speakers
print("Top 10 Unique Speakers and Counts:")
for normalized_name, count in top_speakers:
    variations = variation_to_normalized[normalized_name]
    print(f"{normalized_name}: {count} (Variations: {', '.join(variations)})")

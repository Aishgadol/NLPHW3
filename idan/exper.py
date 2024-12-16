import json
import re
import os

# Define the relative path to the file
file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "result.jsonl")

# Forbidden words: titles and departments
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

# Compile a regex pattern to match forbidden words as whole words
forbidden_pattern = re.compile(rf"\b({'|'.join(map(re.escape, titles + departments))})\b")

# Read and process the JSONL file
forbidden_names = {}

try:
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            try:
                # Parse each line as JSON
                record = json.loads(line)
                if "speaker_name" in record:
                    speaker_name = record["speaker_name"]
                    # Find all forbidden words in the name
                    matches = forbidden_pattern.findall(speaker_name)
                    if matches:
                        forbidden_names[speaker_name] = matches
            except json.JSONDecodeError:
                continue
except FileNotFoundError:
    print(f"Error: File not found at {file_path}")
    exit()

# Print all names containing forbidden words and the reason
print("Names with Forbidden Words and Reasons:")
for name, reasons in forbidden_names.items():
    print(f"{name}: Forbidden because it contains {', '.join(reasons)}")

import json
from collections import defaultdict
import os
import re
import random
import sys

# Define the path to the file located in the same directory as the script
file_path = os.path.join(os.path.dirname(__file__), "result.jsonl")

# Original predefined pairs of shortened (nicknames) and lengthened (full) first names
nickname_map = {
    "בני": "בנימין",
    "יוסי": "יוסף",
    "אבי": "אברהם",
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
    "ראובן": "ראובן",        # Ensure full name maps to itself
}

# New mapping for entire speaker name variations to normalized full names
speaker_map = {
    "א' בורג": "אברהם בורג",
    "מר א' בורג": "אברהם בורג",
    "אבי בורג": "אברהם בורג",
    "מר אבי בורג": "אברהם בורג",
    "אברהם בורג": "אברהם בורג",  # Ensure full name maps to itself

    "ר' ריבלין": "ראובן ריבלין",
    "מר ר' ריבלין": "ראובן ריבלין",
    "רבי ריבלין": "ראובן ריבלין",
    "ראובן ריבלין": "ראובן ריבלין",  # Ensure full name maps to itself

    # Add more mappings as needed
    # Example:
    # "מרדכי כהן": "מרדכי כהן",
    # "מוטי כהן": "מרדכי כהן",
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

def normalize_full_name(full_name):
    """
    Normalize the speaker's full name by:
    1. Removing titles and departments.
    2. Mapping entire speaker name variations to normalized names via speaker_map.
    3. If not in speaker_map, mapping first names via nickname_map.
    4. Removing single-letter initials if they are not in nickname_map.
    """
    # Remove any titles or departments from the name
    cleaned_name = bad_words_pattern.sub("", full_name).strip()

    # Remove any extra spaces that might have been left after removal
    cleaned_name = re.sub(r'\s+', ' ', cleaned_name)

    # First, check if the entire cleaned name is in speaker_map
    if cleaned_name in speaker_map:
        return speaker_map[cleaned_name]
    else:
        # If not, split into first and last names
        parts = cleaned_name.split(" ", 1)
        if len(parts) == 2:
            first_name, last_name = parts

            # Normalize first name if it's in nickname_map
            if first_name in nickname_map:
                first_name = nickname_map[first_name]
            else:
                # If first name is a single-letter initial without a mapping, remove it
                if re.match(r"^[א-ת]'", first_name):
                    return last_name

            return f"{first_name} {last_name}"
    return cleaned_name  # Return as-is if it doesn't fit the expected structure

def downsample_sentences_random(sentences, target_size):
    """
    Downsamples a list of sentences to the target_size by removing sentences randomly.
    Returns the downsampled list and the list of removed sentences.
    """
    if len(sentences) > target_size:
        # Shuffle the sentences randomly
        shuffled = sentences.copy()
        random.shuffle(shuffled)
        # Take the first target_size sentences
        downsampled = shuffled[:target_size]
        # The removed sentences are the rest
        removed_sentences = shuffled[target_size:]
        return downsampled, removed_sentences
    else:
        # If already at or below target size, return as is with no removed sentences
        return sentences, []

def calculate_statistics_random(removed_sentences):
    """
    Calculates statistics (count) of removed sentences.
    Since removal is random, we won't calculate lengths.
    """
    return {
        "count": len(removed_sentences)
    }

def main():
    # Optional: Set a random seed for reproducibility
    # Uncomment the following line to have reproducible results
    # random.seed(42)

    # Initialize a dictionary to uniquely identify speakers
    unique_speaker_counter = defaultdict(int)

    print("Starting first pass to count sentences per speaker...")

    # First Pass: Read and count speakers
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
                except json.JSONDecodeError as e:
                    print(f"JSON decoding error on line {line_number}: {e}")
                    continue  # Skip lines with JSON errors
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred during the first pass: {e}")
        sys.exit(1)

    # Get the top 5 most common unique speakers
    top_speakers = sorted(unique_speaker_counter.items(), key=lambda x: x[1], reverse=True)[:5]

    # Check if there are at least two speakers
    if len(top_speakers) < 2:
        print("Error: Less than two speakers found.")
        sys.exit(1)

    # Extract the names of the top 2 speakers
    top_2_speakers = [speaker for speaker, count in top_speakers[:2]]

    print(f"Top 2 speakers identified: {top_2_speakers[0]} and {top_2_speakers[1]}")

    # Initialize lists to hold sentences for the top 2 speakers
    top_2_sentences = {speaker: [] for speaker in top_2_speakers}

    # Initialize list to hold sentences not belonging to top 2 speakers
    none_top_2_speakers_sentences = []

    print("Starting second pass to collect sentences...")

    # Second Pass: Collect sentences for the top 2 speakers and others
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                try:
                    # Parse each line as JSON
                    record = json.loads(line)
                    if "speaker_name" in record and "sentence_text" in record:
                        speaker_name = record["speaker_name"]
                        sentence_text = record["sentence_text"]

                        # Normalize the speaker's full name
                        normalized_name = normalize_full_name(speaker_name)

                        # If the speaker is in the top 2, add the sentence to the corresponding list
                        if normalized_name in top_2_speakers:
                            top_2_sentences[normalized_name].append(sentence_text)
                        else:
                            none_top_2_speakers_sentences.append(sentence_text)
                except json.JSONDecodeError as e:
                    print(f"JSON decoding error on line {line_number}: {e}")
                    continue  # Skip lines with JSON errors
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred during the second pass: {e}")
        sys.exit(1)

    # Determine the target size based on the second speaker's sentence count
    target_size = len(top_2_sentences[top_2_speakers[1]])

    # Validate target_size
    if target_size <= 0:
        print("Error: The second top speaker has zero sentences. Cannot downsample.")
        sys.exit(1)

    print(f"Target size for downsampling: {target_size} sentences")

    # Downsample the first top speaker's sentences
    top_1_speaker = top_2_speakers[0]
    original_size_top1 = len(top_2_sentences[top_1_speaker])
    print(f"Original number of sentences for '{top_1_speaker}': {original_size_top1}")
    if original_size_top1 > target_size:
        downsampled_sentences_top1, removed_sentences_top1 = downsample_sentences_random(
            top_2_sentences[top_1_speaker], target_size
        )
        top_2_sentences[top_1_speaker] = downsampled_sentences_top1
        print(f"Downsampled '{top_1_speaker}' to {len(top_2_sentences[top_1_speaker])} sentences")
    else:
        removed_sentences_top1 = []
        print(f"No downsampling needed for '{top_1_speaker}'")

    # Downsample the 'other sentences' list
    original_size_others = len(none_top_2_speakers_sentences)
    print(f"Original number of 'other sentences': {original_size_others}")
    if original_size_others > target_size:
        downsampled_others, removed_sentences_others = downsample_sentences_random(
            none_top_2_speakers_sentences, target_size
        )
        none_top_2_speakers_sentences = downsampled_others
        print(f"Downsampled 'other sentences' to {len(none_top_2_speakers_sentences)} sentences")
    else:
        removed_sentences_others = []
        print("No downsampling needed for 'other sentences'")

    # Calculate statistics for removed sentences
    stats_top1 = calculate_statistics_random(removed_sentences_top1)
    stats_others = calculate_statistics_random(removed_sentences_others)

    # Print the top 5 unique speakers and the size of the top 2 sentence lists
    print("\n=== Summary ===")
    print("Top 5 speakers with most sentences:")
    for normalized_name, count in top_speakers:
        print(f"{normalized_name}: {count}")

    print("\nSize of the top 2 speakers' sentence lists after downsampling:")
    for speaker in top_2_speakers:
        print(f"{speaker}: {len(top_2_sentences[speaker])}")

    print(f"\nSize of the 'other sentences' list after downsampling: {len(none_top_2_speakers_sentences)}")

    # Optional: Verify that the counts match
    print("\n=== Verification ===")
    for speaker in top_2_speakers:
        print(f"Count from counter for '{speaker}': {unique_speaker_counter[speaker]}")
        print(f"Number of sentences collected for '{speaker}': {len(top_2_sentences[speaker])}\n")

    print(f"Number of other sentences after downsampling: {len(none_top_2_speakers_sentences)}")

    # Print statistics about removed sentences
    print("\n=== Removed Sentences Statistics ===")
    print(f"Top 1 Speaker ('{top_1_speaker}'):")
    print(f"Number of sentences removed: {stats_top1['count']}")

    print("\n'Other Sentences':")
    print(f"Number of sentences removed: {stats_others['count']}")

if __name__ == "__main__":
    main()

# Knesset Transcript Normalization Toolkit

A set of Python utilities for normalizing and analyzing Hebrew Knesset plenary transcripts. The tools parse a JSONL corpus of speaker sentences, clean inconsistent names, and downsample the dataset for experimentation.

## Purpose & Objectives

- Clean speaker names by stripping titles and departmental references.
- Detect nickname variations and map them to canonical Hebrew names.
- Identify the top speakers and balance sentence counts via random downsampling.
- Provide quick checks for forbidden words or anomalous patterns in the raw data.

## Architecture & Module Breakdown

- **`result*.jsonl`** – Line-delimited JSON files containing the original and cleaned transcripts. Each line resembles:
  ```json
  {"protocol_name": "13_ptm_532058.docx", "kneset_number": 13, "protocol_type": "plenary", "protocol_number": 40, "speaker_name": "ש' וייס", "sentence_text": "..."}
  ```
  【F:result.jsonl†L1-L2】
- **`print_top_5_common_speakers.py`** – Normalizes speaker names, counts occurrences, selects the top two speakers, and optionally downsamples sentences. Core logic is implemented in `normalize_full_name` and `downsample_sentences_random`:
  ```python
  bad_words_pattern = re.compile(rf"({'|'.join(map(re.escape, titles + departments))})", re.IGNORECASE)

  def normalize_full_name(full_name):
      """Normalize by removing titles, mapping nicknames, and stripping initials."""
      cleaned_name = bad_words_pattern.sub("", full_name).strip()
      cleaned_name = re.sub(r'\s+', ' ', cleaned_name)
      if cleaned_name in speaker_map:
          return speaker_map[cleaned_name]
      ...
  ```
  【F:print_top_5_common_speakers.py†L72-L104】
  ```python
  def downsample_sentences_random(sentences, target_size):
      """Randomly remove sentences until `target_size` is reached."""
      if len(sentences) > target_size:
          shuffled = sentences.copy()
          random.shuffle(shuffled)
          downsampled = shuffled[:target_size]
          removed_sentences = shuffled[target_size:]
          return downsampled, removed_sentences
      return sentences, []
  ```
  【F:print_top_5_common_speakers.py†L108-L125】
- **`res_fixer.py`** – Strips prefixes/suffixes from names and counts instances where the last name equals "בורג":
  ```python
  bad_words_pattern = re.compile(rf"({'|'.join(map(re.escape, titles + departments))})", re.IGNORECASE)

  def normalize_full_name(full_name):
      cleaned_name = bad_words_pattern.sub("", full_name).strip()
      cleaned_name = re.sub(r'\s+', ' ', cleaned_name)
      return cleaned_name
  ```
  【F:res_fixer.py†L24-L38】
- **`idan/exper.py`** – Scans the dataset for forbidden words in `speaker_name` fields:
  ```python
  with open(file_path, "r", encoding="utf-8") as file:
      for line in file:
          record = json.loads(line)
          if "speaker_name" in record:
              matches = forbidden_pattern.findall(record["speaker_name"])
              if matches:
                  forbidden_names[speaker_name] = matches
  ```
  【F:idan/exper.py†L28-L42】

## Installation & Environment Setup

1. Install Python ≥3.10.
2. Clone this repository and install the minimal requirements:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. No additional system libraries or CUDA components are required.

## Usage & Examples

- **Analyze top speakers and balance dataset**
  ```bash
  python print_top_5_common_speakers.py \
      > analysis.log     # prints summary statistics to stdout
  ```

- **Check for names containing forbidden titles**
  ```bash
  python idan/exper.py
  # Outputs lines such as:
  # שמואל ריבלין: Forbidden because it contains יו"ר
  ```

## Outputs & Artifacts

- `result.jsonl` – Cleaned transcript sentences.
- `result_fixed.jsonl` – Additional normalization pass.
- `result_orig.jsonl` / `result_orig.jsonl.bak` – Raw input data.
- `analysis.log` – Example log from running `print_top_5_common_speakers.py` showing speaker counts and downsampling stats.

## Development & Contribution Workflow

1. Format new Python code with `black` and run linting tools of your choice.
2. Open pull requests against the `main` branch with clear descriptions.
3. Tests can be added using `pytest`; run them via `pytest -vv`.

## Project Status & Roadmap

This toolkit is in **alpha**. Planned improvements include:
- Automating name normalization with heuristic rules.
- Adding unit tests and continuous integration.
- Providing configuration options for different downsampling strategies.

## License & Attribution

No license file is present. Consider releasing the code under the MIT License or another OSI-approved license for clarity.

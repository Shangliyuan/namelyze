"""
Prompt template for scholar nationality and gender inference
"""

from typing import List


PROMPT_TEMPLATE = """
Please determine the nationality (using ISO 3166-1 alpha-3 country codes) and gender for each provided scholar's name.
Base your inferences on historical context, cultural background, and naming conventions (such as common surnames or given-name patterns). Assign a confidence level (high/medium/low) to each judgment.

Confidence level definitions:
- High: Based on clear historical records, reliable biographical information, or strong cultural naming traits (e.g., typical surname–given name combinations).
  Examples:
  - "Adam Smith" → GBR, Male (well-documented British economist)
  - "Steven N.S. Cheung" → CHN, Male (typical Chinese name and a well-known Chinese scholar)

- Medium: Based on strong cultural naming patterns or common nationality/gender associations, though exceptions may exist.
  Examples:
  - "Maria Garcia" → likely ESP or another Spanish-speaking country, Female (common Spanish name)
  - "Thomas Müller" → likely DEU or AUT, Male (common German-speaking name)

- Low: Based on vague or cross-culturally common name features, with significant uncertainty.
  Examples:
  - "John Lee" → may be GBR, USA, KOR, etc. (cross-cultural name)
  - "Alex Taylor" → gender unclear (can be male or female)

Output must be in strict JSON format with the following keys for each entry:
- `name` (original name)
- `gender` (inferred gender or 'Unknown')
- `conf_gender` (confidence for gender)
- `nation` (inferred country code or 'Unknown')
- `conf_nation` (confidence for nationality)

If information is uncertain, use 'Unknown' for nation or gender and assign a low confidence level.
Each 'name' field must be copied exactly as provided without any modification.

Example Output Format:

[
    {{
      "name": "Adam Smith",
      "gender": "Male",
      "conf_gender": "High",
      "nation": "GBR",
      "conf_nation": "High"
    }},
    {{
      "name": "Elinor Ostrom",
      "gender": "Female",
      "conf_gender": "High",
      "nation": "USA",
      "conf_nation": "High"
    }},
    {{
      "name": "Wei Zhang",
      "gender": "Unknown",
      "conf_gender": "Low",
      "nation": "CHN",
      "conf_nation": "High"
    }}
]

Following is the names you need to analyse:
{names_list}
"""


def generate_prompt(names: List[str]) -> str:
    """
    Generate complete prompt with provided names

    Args:
        names: List of scholar names to analyze

    Returns:
        Complete prompt ready to send to LLM
    """
    # Format names as a numbered list
    names_list = "\n".join([f"{i+1}. {name}" for i, name in enumerate(names)])

    return PROMPT_TEMPLATE.format(names_list=names_list)

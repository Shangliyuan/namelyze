"""
Data validation module for inference results
"""

from typing import Dict, List, Set
import logging
import pycountry

logger = logging.getLogger(__name__)

# Valid values for gender and confidence fields
VALID_GENDERS: Set[str] = {"Male", "Female", "Unknown"}
VALID_CONFIDENCES: Set[str] = {"High", "Medium", "Low"}


def is_valid_nation_code(nation_code: str) -> bool:
    """
    Validate ISO 3166-1 alpha-3 country code using pycountry library

    Args:
        nation_code: 3-letter country code to validate

    Returns:
        True if valid ISO 3166-1 alpha-3 code or "Unknown", False otherwise
    """
    # "Unknown" is explicitly allowed per prompt specification
    if nation_code == "Unknown":
        return True

    # Validate using pycountry library
    country = pycountry.countries.get(alpha_3=nation_code)
    return country is not None


def validate_result(result: Dict) -> tuple[bool, List[str]]:
    """
    Validate a single inference result

    Args:
        result: Dictionary containing inference result for one name

    Returns:
        Tuple of (is_valid, error_messages)
        - is_valid: True if no errors, False otherwise
        - error_messages: List of error descriptions

    Note:
        This function only validates and identifies errors.
        It does NOT modify the result data.
    """
    errors = []

    # Validate required fields exist
    if "name" not in result:
        errors.append("Missing name field")

    if "gender" not in result:
        errors.append("Missing gender field")

    if "nation" not in result:
        errors.append("Missing nation field")

    if "conf_gender" not in result:
        errors.append("Missing conf_gender field")

    if "conf_nation" not in result:
        errors.append("Missing conf_nation field")

    # Validate field values (only if field exists)
    if "gender" in result and result["gender"] not in VALID_GENDERS:
        errors.append(f"Invalid gender value: {result['gender']}")

    if "nation" in result and not is_valid_nation_code(result["nation"]):
        errors.append(f"Invalid nation code: {result['nation']}")

    if "conf_gender" in result and result["conf_gender"] not in VALID_CONFIDENCES:
        errors.append(f"Invalid conf_gender value: {result['conf_gender']}")

    if "conf_nation" in result and result["conf_nation"] not in VALID_CONFIDENCES:
        errors.append(f"Invalid conf_nation value: {result['conf_nation']}")

    is_valid = len(errors) == 0

    if not is_valid:
        logger.warning(f"Validation errors for '{result.get('name', 'UNKNOWN')}': {'; '.join(errors)}")

    return is_valid, errors


def validate_batch_results(results: List[Dict]) -> List[Dict]:
    """
    Validate a batch of inference results

    Args:
        results: List of result dictionaries from LLM

    Returns:
        List of results with added validation fields:
        - has_error: "Yes" or "No"
        - error_reason: semicolon-separated error messages (empty if no errors)

    Note:
        Original data is preserved. Only validation fields are added.
    """
    validated_results = []

    for result in results:
        is_valid, errors = validate_result(result)

        # Add validation fields (do NOT modify original data)
        result["has_error"] = "No" if is_valid else "Yes"
        result["error_reason"] = "; ".join(errors) if errors else ""

        validated_results.append(result)

    # Log summary
    total = len(validated_results)
    failed = sum(1 for r in validated_results if r["has_error"] == "Yes")
    passed = total - failed

    logger.info(f"Batch validation: {passed}/{total} passed, {failed}/{total} failed")

    return validated_results


def add_validation_fields_for_error(name: str, error_message: str) -> Dict:
    """
    Create a result entry for a name that failed processing

    Args:
        name: Scholar name
        error_message: Description of the error

    Returns:
        Dictionary with name and error information
    """
    return {
        "name": name,
        "gender": "",
        "conf_gender": "",
        "nation": "",
        "conf_nation": "",
        "has_error": "Yes",
        "error_reason": error_message
    }

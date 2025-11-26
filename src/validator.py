"""
Data validation module for inference results
"""

from typing import Dict, List, Set
import logging

logger = logging.getLogger(__name__)

# Valid values for gender and confidence fields
VALID_GENDERS: Set[str] = {"Male", "Female", "Unknown"}
VALID_CONFIDENCES: Set[str] = {"High", "Medium", "Low"}

# ISO 3166-1 alpha-3 country codes (partial list - can be extended)
# Including "Unknown" as valid value per prompt specification
VALID_NATIONS: Set[str] = {
    "Unknown",  # Explicitly allowed per prompt
    "AFG", "ALB", "DZA", "AND", "AGO", "ATG", "ARG", "ARM", "AUS", "AUT",
    "AZE", "BHS", "BHR", "BGD", "BRB", "BLR", "BEL", "BLZ", "BEN", "BTN",
    "BOL", "BIH", "BWA", "BRA", "BRN", "BGR", "BFA", "BDI", "KHM", "CMR",
    "CAN", "CPV", "CAF", "TCD", "CHL", "CHN", "COL", "COM", "COG", "COD",
    "CRI", "CIV", "HRV", "CUB", "CYP", "CZE", "DNK", "DJI", "DMA", "DOM",
    "ECU", "EGY", "SLV", "GNQ", "ERI", "EST", "ETH", "FJI", "FIN", "FRA",
    "GAB", "GMB", "GEO", "DEU", "GHA", "GRC", "GRD", "GTM", "GIN", "GNB",
    "GUY", "HTI", "HND", "HUN", "ISL", "IND", "IDN", "IRN", "IRQ", "IRL",
    "ISR", "ITA", "JAM", "JPN", "JOR", "KAZ", "KEN", "KIR", "PRK", "KOR",
    "KWT", "KGZ", "LAO", "LVA", "LBN", "LSO", "LBR", "LBY", "LIE", "LTU",
    "LUX", "MKD", "MDG", "MWI", "MYS", "MDV", "MLI", "MLT", "MHL", "MRT",
    "MUS", "MEX", "FSM", "MDA", "MCO", "MNG", "MNE", "MAR", "MOZ", "MMR",
    "NAM", "NRU", "NPL", "NLD", "NZL", "NIC", "NER", "NGA", "NOR", "OMN",
    "PAK", "PLW", "PAN", "PNG", "PRY", "PER", "PHL", "POL", "PRT", "QAT",
    "ROU", "RUS", "RWA", "KNA", "LCA", "VCT", "WSM", "SMR", "STP", "SAU",
    "SEN", "SRB", "SYC", "SLE", "SGP", "SVK", "SVN", "SLB", "SOM", "ZAF",
    "SSD", "ESP", "LKA", "SDN", "SUR", "SWZ", "SWE", "CHE", "SYR", "TJK",
    "TZA", "THA", "TLS", "TGO", "TON", "TTO", "TUN", "TUR", "TKM", "TUV",
    "UGA", "UKR", "ARE", "GBR", "USA", "URY", "UZB", "VUT", "VAT", "VEN",
    "VNM", "YEM", "ZMB", "ZWE"
}


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

    if "nation" in result and result["nation"] not in VALID_NATIONS:
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

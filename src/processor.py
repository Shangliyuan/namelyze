"""
Core processing logic for batch inference and CSV handling
"""

import json
import pandas as pd
from typing import List, Dict
from pathlib import Path
import logging
from tqdm import tqdm

from .llm_client import LLMClient
from .prompt_template import generate_prompt
from .validator import validate_batch_results, add_validation_fields_for_error

logger = logging.getLogger(__name__)


class ScholarProcessor:
    """Main processor for scholar nationality and gender inference"""

    def __init__(
        self,
        llm_client: LLMClient,
        batch_size: int = 20
    ):
        """
        Initialize processor

        Args:
            llm_client: Configured LLM client
            batch_size: Number of names to process in each batch
        """
        self.llm_client = llm_client
        self.batch_size = batch_size

    def read_names_from_csv(self, file_path: str, name_column: str) -> List[str]:
        """
        Read scholar names from CSV file

        Args:
            file_path: Path to input CSV file
            name_column: Name of the column containing scholar names

        Returns:
            List of scholar names

        Raises:
            FileNotFoundError: If CSV file doesn't exist
            KeyError: If name column doesn't exist in CSV
        """
        csv_path = Path(file_path)

        if not csv_path.exists():
            raise FileNotFoundError(f"Input CSV file not found: {file_path}")

        logger.info(f"Reading names from {file_path}")
        df = pd.read_csv(csv_path)

        if name_column not in df.columns:
            raise KeyError(
                f"Column '{name_column}' not found in CSV. "
                f"Available columns: {', '.join(df.columns)}"
            )

        # Extract names and remove duplicates while preserving order
        names = df[name_column].dropna().astype(str).tolist()
        unique_names = list(dict.fromkeys(names))  # Preserve order

        logger.info(f"Loaded {len(unique_names)} unique names from {len(names)} total entries")

        return unique_names

    def process_batch(self, names: List[str]) -> List[Dict]:
        """
        Process a single batch of names

        Args:
            names: List of names to process

        Returns:
            List of validated result dictionaries
        """
        try:
            # Generate prompt
            prompt = generate_prompt(names)

            # Call LLM
            response = self.llm_client.infer_batch(prompt)

            # Parse JSON response
            try:
                results = json.loads(response)

                if not isinstance(results, list):
                    raise ValueError("Response is not a JSON array")

            except json.JSONDecodeError as e:
                logger.error(f"JSON parse error: {str(e)}")
                logger.error(f"Raw response: {response[:500]}...")

                # Mark all names in this batch as errors
                return [
                    add_validation_fields_for_error(
                        name,
                        f"JSON parse error: {str(e)}"
                    )
                    for name in names
                ]

            # Validate results
            validated_results = validate_batch_results(results)

            # Check if all names are present in results
            result_names = {r.get("name") for r in validated_results}
            for name in names:
                if name not in result_names:
                    logger.warning(f"Name '{name}' missing in LLM response")
                    validated_results.append(
                        add_validation_fields_for_error(
                            name,
                            "Missing in LLM response"
                        )
                    )

            return validated_results

        except Exception as e:
            logger.error(f"Batch processing error: {str(e)}")

            # Mark all names as errors
            return [
                add_validation_fields_for_error(
                    name,
                    f"Batch processing error: {str(e)}"
                )
                for name in names
            ]

    def process_all(self, names: List[str]) -> List[Dict]:
        """
        Process all names in batches

        Args:
            names: List of all names to process

        Returns:
            List of all validated results
        """
        all_results = []

        # Split into batches
        batches = [
            names[i:i + self.batch_size]
            for i in range(0, len(names), self.batch_size)
        ]

        logger.info(f"Processing {len(names)} names in {len(batches)} batches")

        # Process each batch with progress bar
        for batch in tqdm(batches, desc="Processing batches"):
            batch_results = self.process_batch(batch)
            all_results.extend(batch_results)

        logger.info(f"Completed processing {len(all_results)} results")

        return all_results

    def save_results_to_csv(self, results: List[Dict], output_path: str):
        """
        Save results to CSV file

        Args:
            results: List of result dictionaries
            output_path: Path to output CSV file
        """
        # Define column order
        columns = [
            "name",
            "gender",
            "conf_gender",
            "nation",
            "conf_nation",
            "has_error",
            "error_reason"
        ]

        # Convert to DataFrame
        df = pd.DataFrame(results)

        # Ensure all columns exist
        for col in columns:
            if col not in df.columns:
                df[col] = ""

        # Reorder columns
        df = df[columns]

        # Create output directory if it doesn't exist
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Save to CSV
        df.to_csv(output_path, index=False)
        logger.info(f"Results saved to {output_path}")

        # Log summary statistics
        total = len(df)
        errors = (df["has_error"] == "Yes").sum()
        success = total - errors

        logger.info(f"Summary: {success}/{total} successful, {errors}/{total} with errors")

    def run(self, input_csv: str, output_csv: str, name_column: str):
        """
        Run the complete processing pipeline

        Args:
            input_csv: Path to input CSV file
            output_csv: Path to output CSV file
            name_column: Name of column containing names in input CSV
        """
        logger.info("=" * 60)
        logger.info("Starting Scholar Nationality & Gender Inference")
        logger.info("=" * 60)

        # Read names
        names = self.read_names_from_csv(input_csv, name_column)

        # Process all names
        results = self.process_all(names)

        # Save results
        self.save_results_to_csv(results, output_csv)

        logger.info("=" * 60)
        logger.info("Processing Complete!")
        logger.info("=" * 60)

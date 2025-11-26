#!/usr/bin/env python3
"""
Namelyze - Scholar Nationality and Gender Inference Tool

Main entry point for the application
"""

import sys
import logging
from pathlib import Path

from src.config import load_settings
from src.llm_client import LLMClient
from src.processor import ScholarProcessor


def setup_logging():
    """Configure logging for the application"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('namelyze.log')
        ]
    )


def main():
    """Main execution function"""
    try:
        # Setup logging
        setup_logging()
        logger = logging.getLogger(__name__)

        # Load configuration
        logger.info("Loading configuration...")
        try:
            settings = load_settings()
        except Exception as e:
            logger.error(f"Failed to load configuration: {str(e)}")
            logger.error("Please ensure .env file exists with required settings")
            logger.error("See .env.example for reference")
            sys.exit(1)

        # Validate input file exists
        input_path = Path(settings.input_csv)
        if not input_path.exists():
            logger.error(f"Input CSV file not found: {settings.input_csv}")
            logger.error("Please create the input file or update INPUT_CSV in .env")
            sys.exit(1)

        # Initialize LLM client
        logger.info(f"Initializing LLM client for model: {settings.model_name}")
        llm_client = LLMClient(
            api_base=settings.openai_api_base,
            api_key=settings.openai_api_key,
            model_name=settings.model_name,
            timeout=settings.timeout,
            max_retries=settings.max_retries
        )

        # Initialize processor
        processor = ScholarProcessor(
            llm_client=llm_client,
            batch_size=settings.batch_size
        )

        # Run processing pipeline
        processor.run(
            input_csv=settings.input_csv,
            output_csv=settings.output_csv,
            name_column=settings.name_column
        )

        logger.info(f"Results saved to: {settings.output_csv}")
        logger.info("Processing completed successfully!")

    except KeyboardInterrupt:
        logger.warning("\nProcessing interrupted by user")
        sys.exit(1)

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

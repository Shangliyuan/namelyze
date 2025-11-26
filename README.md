# Namelyze

**Scholar Nationality and Gender Inference Tool**

English | [简体中文](README_CN.md) | [📓 Tutorial](tutorial.ipynb)

A research tool that uses Large Language Models (LLMs) to infer nationality and gender from scholar names, based on historical context, cultural background, and naming conventions.

## Features

- **LLM-Powered Inference**: Leverages the knowledge and reasoning capabilities of commercial LLMs
- **OpenAI Compatible**: Works with any OpenAI-compatible API (OpenAI, Azure OpenAI, DeepSeek, Zhipu, etc.)
- **Batch Processing**: Efficient batch processing to reduce API costs
- **Comprehensive Validation**: Built-in validation with error tracking and reporting
- **Confidence Levels**: Provides High/Medium/Low confidence ratings for each inference
- **ISO Standards**: Uses ISO 3166-1 alpha-3 country codes for nationalities

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. Clone or download this repository

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your API settings:
```bash
# Copy the example configuration file
cp .env.example .env

# Edit the .env file with your preferred text editor
# On Linux/Mac:
nano .env
# or
vim .env

# On Windows:
notepad .env
```

## Configuration

### Basic Configuration

Edit the `.env` file to configure the tool. Here's what each parameter means:

```bash
# API Configuration
OPENAI_API_BASE=https://api.openai.com/v1  # API endpoint URL
OPENAI_API_KEY=sk-your-api-key-here        # Your API key
MODEL_NAME=gpt-4                            # Model name to use

# Processing Settings
BATCH_SIZE=50                               # Number of names to process in each batch
MAX_RETRIES=3                               # Maximum retry attempts for failed API calls
TIMEOUT=60                                  # API request timeout in seconds
MAX_WORKERS=5                               # Number of concurrent workers
ENABLE_CONCURRENT=True                      # Enable concurrent processing

# File Paths
INPUT_CSV=data/input/names.csv              # Input CSV file path
OUTPUT_CSV=data/output/results.csv          # Output CSV file path
NAME_COLUMN=name                            # Column name containing scholar names
```

### Understanding Key Parameters

#### **BATCH_SIZE** (Default: 50)
- **What it does**: Groups this many names together in a single API request
- **Impact**: Larger batches reduce the total number of API calls but may hit token limits
- **Recommendations**:
  - Small models (gpt-3.5): 20-30
  - Large models (gpt-4): 40-60
  - Context-optimized models: 50-100

#### **MAX_WORKERS** (Default: 5)
- **What it does**: Number of batches processed simultaneously
- **Impact**: Higher values = faster processing but may trigger rate limits
- **Recommendations**:
  - **Conservative** (3 workers): Safe for most providers
  - **Balanced** (5 workers): Good balance of speed and safety
  - **Aggressive** (10-20 workers): Only if provider allows high concurrency

⚠️ **Important**: Different API providers have different rate limits:
- **OpenAI Official**: 3-5 workers recommended
- **Azure OpenAI**: Check your deployment's TPM/RPM limits
- **DeepSeek**: Supports high concurrency (10-20 workers)
- **Other providers**: Start with 3 workers and increase gradually

#### How BATCH_SIZE and MAX_WORKERS Work Together

```
Example: Processing 1000 names
├─ BATCH_SIZE=50 → Creates 20 batches (1000 ÷ 50)
└─ MAX_WORKERS=5 → Processes 5 batches at once
   └─ Total time ≈ Serial time ÷ 5
```

**Performance Estimation**:
- Serial (1 worker): ~20 API calls sequentially
- Concurrent (5 workers): ~4 rounds of 5 parallel calls
- Speedup: ~5x faster

## Usage

### 1. Prepare Input Data

Create a CSV file with scholar names:

```csv
name
Adam Smith
Elinor Ostrom
Wei Zhang
Maria Garcia
Thomas Müller
```

Place it in `data/input/names.csv` (or path specified in `.env`)

### 2. Run the Tool

```bash
python main.py
```

### 3. View Results

Results will be saved to `data/output/results.csv`:

```csv
name,gender,conf_gender,nation,conf_nation,has_error,error_reason
Adam Smith,Male,High,GBR,High,No,
Elinor Ostrom,Female,High,USA,High,No,
Wei Zhang,Unknown,Low,CHN,High,No,
```

## Output Format

| Column | Description |
|--------|-------------|
| `name` | Original scholar name (unchanged) |
| `gender` | Inferred gender: Male, Female, or Unknown |
| `conf_gender` | Confidence level: High, Medium, or Low |
| `nation` | ISO 3166-1 alpha-3 country code or Unknown |
| `conf_nation` | Confidence level: High, Medium, or Low |
| `has_error` | Yes if validation errors occurred, No otherwise |
| `error_reason` | Description of validation errors (if any) |

## Confidence Levels

- **High**: Based on clear historical records, reliable biographical information, or strong cultural naming traits
- **Medium**: Based on strong cultural naming patterns or common nationality/gender associations, though exceptions may exist
- **Low**: Based on vague or cross-culturally common name features, with significant uncertainty

## Supported API Providers

This tool works with any OpenAI-compatible API endpoint:

- **OpenAI**: `https://api.openai.com/v1`
- **Azure OpenAI**: `https://your-resource.openai.azure.com/`
- **DeepSeek**: `https://api.deepseek.com/v1`
- **Zhipu AI**: `https://open.bigmodel.cn/api/paas/v4/`
- **Alibaba Cloud**: Configure according to provider documentation
- **Other providers**: Any service supporting OpenAI API format

## Error Handling

The tool includes robust error handling:

- **API Failures**: Automatic retry with exponential backoff
- **JSON Parsing Errors**: Captured and reported in output
- **Validation Errors**: Each result is validated against expected formats
- **Missing Data**: Incomplete responses are flagged with error reasons

Common errors in `error_reason` column:
- `JSON parse error`: LLM response was not valid JSON
- `Missing in LLM response`: Name was not included in LLM output
- `Invalid gender value`: Gender field contains unexpected value
- `Invalid nation code`: Nation code is not a valid ISO 3166-1 alpha-3 code
- `Missing [field] field`: Required field was not provided

## Project Structure

```
namelyze/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── .env.example             # Configuration template
├── main.py                  # Main entry point
├── src/
│   ├── __init__.py
│   ├── config.py            # Configuration management
│   ├── llm_client.py        # LLM API client
│   ├── prompt_template.py   # Prompt engineering
│   ├── validator.py         # Result validation
│   └── processor.py         # Core processing logic
├── data/
│   ├── input/               # Input CSV files
│   └── output/              # Output results
└── examples/
    └── sample_names.csv     # Example input
```

## Logging

Logs are written to:
- **Console**: Real-time progress and status
- **File**: `namelyze.log` for detailed debugging

## Tips for Best Results

1. **Batch Size**: Adjust `BATCH_SIZE` based on your model's context window
2. **Model Selection**: GPT-4 generally provides better accuracy than GPT-3.5
3. **Cost Management**: Use batch processing to minimize API calls
4. **Validation**: Always review results with `has_error=Yes` for accuracy
5. **Rate Limits**: Adjust `TIMEOUT` and `MAX_RETRIES` if you encounter rate limiting

## Limitations

- **Historical Accuracy**: Results depend on LLM training data and may not reflect current nationality
- **Cultural Complexity**: Some names are genuinely ambiguous across cultures
- **Name Changes**: Married names, transliterations, and name changes may affect accuracy
- **Model Dependency**: Quality depends on the capabilities of the chosen LLM

## License

This project is provided as-is for research purposes.

## Contributing

Contributions are welcome. Please ensure:
- Code follows existing style conventions
- New features include appropriate error handling
- Validation logic preserves data integrity

## Support

For issues or questions:
- Check the log file (`namelyze.log`) for detailed error messages
- Verify your `.env` configuration matches `.env.example`
- Ensure your API key and endpoint are correctly configured
- Review the `has_error` and `error_reason` columns in output for specific failures

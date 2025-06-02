# AI-Powered File Organizer

An intelligent file organization and duplicate detection system that uses AI to automatically categorize and manage your files.

## Features

- Smart file organization using AI classification
- Duplicate file detection using hash comparison
- Support for various file types (documents, images, videos, code)
- CLI interface with rich feedback
- Detailed logging and reporting
- Optional scheduling support

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/duplicate-finder-ai.git
cd duplicate-finder-ai
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
python file_organizer.py --source /path/to/source --destination /path/to/destination
```

### Options

- `--source`: Source directory to organize
- `--destination`: Destination directory for organized files
- `--detect-duplicates`: Enable duplicate detection
- `--schedule`: Run as a scheduled task (weekly)
- `--gui`: Launch GUI interface

## Project Structure

```
project/
│
├── file_organizer.py          # Main application entry point
├── classifier/                # AI classification components
│   ├── model.py              # Classification model
│   └── train_model.py        # Model training script
├── duplicate_detector.py      # Duplicate file detection
├── utils/                    # Utility functions
│   ├── logger.py            # Logging functionality
│   └── file_utils.py        # File operations
├── data/                     # Sample data and models
│   └── sample_files/
└── reports/                  # Generated reports
    └── report_2025-06-02.txt
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
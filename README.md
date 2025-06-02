# Duplicate Finder AI

A powerful tool for detecting duplicate documents using AI-based similarity detection and traditional hashing methods.

## Project Overview

This project provides an intelligent solution for finding duplicate documents in a given directory. It uses a combination of AI-based text similarity detection and traditional file hashing to identify duplicates across different file types.

## Project Structure

```
duplicate-finder-ai/
├── classifier/          # AI model for document classification
├── data/               # Data directory for storing files
├── logs/               # Log files
├── organized/          # Organized output files
├── reports/            # Generated reports
├── utils/              # Utility functions
├── duplicate_detector.py  # Core duplicate detection logic
├── gui.py              # Graphical user interface
└── requirements.txt    # Project dependencies
```

## Features

1. **Multi-file Type Support**
   - Text files: Uses AI-based similarity detection
   - Binary files: Uses SHA-256 hashing
   - Automatic file type detection

2. **AI-Powered Similarity Detection**
   - Uses document embeddings for text similarity
   - Configurable similarity threshold
   - Cosine similarity-based comparison

3. **Efficient Processing**
   - Batch processing of files
   - Optimized comparison algorithms
   - Memory-efficient file handling

## Workflow

1. **Initialization**
   - The application starts by initializing the `DuplicateDetector` class
   - Loads the AI model for document classification
   - Sets up necessary directories and configurations

2. **File Processing**
   - Scans the target directory for files
   - Automatically detects file types
   - Processes files based on their type:
     - Text files: Generates document embeddings
     - Binary files: Computes SHA-256 hashes

3. **Duplicate Detection**
   - Compares files using appropriate methods:
     - Text files: Cosine similarity of embeddings
     - Binary files: Exact hash matching
   - Identifies duplicates based on similarity threshold
   - Generates detailed comparison reports

4. **Results Handling**
   - Displays duplicate pairs with similarity scores
   - Provides options to:
     - View detailed comparison results
     - Organize duplicate files
     - Generate reports

## Usage

Run the application using the GUI interface:
```python
python gui.py
```

## Configuration

- Similarity threshold: Adjustable (default: 0.95)
- File type detection: Automatic
- Processing batch size: Configurable
- Output format: Customizable

## Dependencies

- Python 3.7+
- PyTorch
- NumPy
- scikit-learn
- Additional requirements in `requirements.txt`

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
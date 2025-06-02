import os
import click
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from utils.file_utils import FileUtils
from utils.logger import Logger
from duplicate_detector import DuplicateDetector
from classifier.model import FileClassifier

class FileOrganizer:
    def __init__(self, source_dir: str, dest_dir: str, log_dir: str = "logs"):
        self.source_dir = Path(source_dir)
        self.dest_dir = Path(dest_dir)
        self.logger = Logger(log_dir)
        self.file_utils = FileUtils()
        self.duplicate_detector = DuplicateDetector(self.logger)
        self.classifier = FileClassifier(self.logger)
        self.console = Console()

    def organize_files(self, detect_duplicates: bool = True) -> Dict:
        """
        Organize files in the source directory based on their classification.
        Returns a dictionary with operation statistics.
        """
        stats = {
            'total_files': 0,
            'organized_files': 0,
            'duplicates_found': 0,
            'duplicates_removed': 0,
            'errors': 0
        }

        # Create destination directory if it doesn't exist
        self.file_utils.create_directory(str(self.dest_dir))

        # Get all files in source directory
        files = self.file_utils.list_files(str(self.source_dir))
        stats['total_files'] = len(files)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            # Organize files
            organize_task = progress.add_task("Organizing files...", total=len(files))
            
            for file_path in files:
                try:
                    # Classify file
                    classification = self.classifier.classify_file(file_path)
                    category = classification['category']
                    
                    # Create category directory
                    category_dir = self.dest_dir / category
                    self.file_utils.create_directory(str(category_dir))
                    
                    # Move file to category directory
                    dest_path = category_dir / Path(file_path).name
                    if self.file_utils.safe_move_file(file_path, str(dest_path)):
                        stats['organized_files'] += 1
                        self.logger.log_operation(
                            operation_type="file_organization",
                            source_path=file_path,
                            destination_path=str(dest_path),
                            status="success"
                        )
                    else:
                        stats['errors'] += 1
                        self.logger.log_operation(
                            operation_type="file_organization",
                            source_path=file_path,
                            status="failure"
                        )
                
                except Exception as e:
                    stats['errors'] += 1
                    self.logger.log_operation(
                        operation_type="file_organization",
                        source_path=file_path,
                        status="failure",
                        details=str(e)
                    )
                
                progress.update(organize_task, advance=1)

            # Detect and remove duplicates if requested
            if detect_duplicates:
                progress.update(organize_task, description="Detecting duplicates...")
                duplicates = self.duplicate_detector.find_duplicates(str(self.dest_dir))
                stats['duplicates_found'] = sum(len(files) - 1 for files in duplicates.values())
                
                if duplicates:
                    progress.update(organize_task, description="Removing duplicates...")
                    removed = self.duplicate_detector.remove_duplicates(duplicates)
                    stats['duplicates_removed'] = len(removed)

        return stats

    def generate_report(self, stats: Dict) -> str:
        """Generate a report of the organization operation."""
        report = []
        report.append("File Organization Report")
        report.append("=" * 50)
        report.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Source Directory: {self.source_dir}")
        report.append(f"Destination Directory: {self.dest_dir}")
        report.append("-" * 50)
        report.append(f"Total Files Processed: {stats['total_files']}")
        report.append(f"Files Organized: {stats['organized_files']}")
        report.append(f"Duplicates Found: {stats['duplicates_found']}")
        report.append(f"Duplicates Removed: {stats['duplicates_removed']}")
        report.append(f"Errors Encountered: {stats['errors']}")
        report.append("=" * 50)
        
        return "\n".join(report)

@click.command()
@click.option('--source', required=True, help='Source directory to organize')
@click.option('--destination', required=True, help='Destination directory for organized files')
@click.option('--detect-duplicates/--no-detect-duplicates', default=True, help='Detect and remove duplicates')
@click.option('--log-dir', default='logs', help='Directory for log files')
def main(source: str, destination: str, detect_duplicates: bool, log_dir: str):
    """Organize files in a directory using AI classification."""
    console = Console()
    
    try:
        # Initialize file organizer
        organizer = FileOrganizer(source, destination, log_dir)
        
        # Organize files
        with console.status("[bold green]Organizing files..."):
            stats = organizer.organize_files(detect_duplicates)
        
        # Generate and display report
        report = organizer.generate_report(stats)
        console.print("\n[bold green]Organization Complete![/bold green]")
        console.print(report)
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise click.Abort()

if __name__ == '__main__':
    main() 
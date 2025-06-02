import os
import click
from pathlib import Path
from typing import List, Tuple
import json
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from utils.logger import Logger
from classifier.model import FileClassifier

def load_training_data(data_dir: str) -> List[Tuple[str, str]]:
    """
    Load training data from a directory.
    Expected format: Each file should be in a subdirectory named after its category.
    """
    training_data = []
    
    for category_dir in os.listdir(data_dir):
        category_path = os.path.join(data_dir, category_dir)
        if not os.path.isdir(category_path):
            continue
            
        for filename in os.listdir(category_path):
            file_path = os.path.join(category_path, filename)
            if not os.path.isfile(file_path):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                training_data.append((content, category_dir))
            except Exception as e:
                print(f"Error reading {file_path}: {str(e)}")
    
    return training_data

@click.command()
@click.option('--data-dir', required=True, help='Directory containing training data')
@click.option('--model-dir', required=True, help='Directory to save trained models')
@click.option('--log-dir', default='logs', help='Directory for log files')
def train(data_dir: str, model_dir: str, log_dir: str):
    """Train the file classifier model."""
    console = Console()
    logger = Logger(log_dir)
    
    try:
        # Load training data
        console.print("[bold blue]Loading training data...[/bold blue]")
        training_data = load_training_data(data_dir)
        
        if not training_data:
            console.print("[bold red]No training data found![/bold red]")
            return
        
        console.print(f"[bold green]Loaded {len(training_data)} training samples[/bold green]")
        
        # Initialize classifier
        classifier = FileClassifier(logger)
        
        # Train model
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            progress.add_task("Training model...", total=None)
            classifier.train_text_classifier(training_data)
        
        # Save model
        console.print("[bold blue]Saving model...[/bold blue]")
        classifier.save_models(model_dir)
        
        console.print("[bold green]Training complete![/bold green]")
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise click.Abort()

if __name__ == '__main__':
    train() 
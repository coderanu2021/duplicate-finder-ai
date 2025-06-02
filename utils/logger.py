import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

class Logger:
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Set up file logging
        self.logger = logging.getLogger('FileOrganizer')
        self.logger.setLevel(logging.INFO)
        
        # Create handlers
        log_file = self.log_dir / f"file_organizer_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file)
        console_handler = logging.StreamHandler()
        
        # Create formatters and add it to handlers
        log_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(log_format)
        console_handler.setFormatter(log_format)
        
        # Add handlers to the logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Initialize SQLite database
        self.db_path = self.log_dir / "file_organizer.db"
        self._init_db()

    def _init_db(self):
        """Initialize SQLite database with required tables."""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Create operations table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS operations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                operation_type TEXT,
                source_path TEXT,
                destination_path TEXT,
                status TEXT,
                details TEXT
            )
            ''')
            
            # Create file_metadata table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS file_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT UNIQUE,
                file_hash TEXT,
                file_type TEXT,
                file_size INTEGER,
                last_modified DATETIME,
                created_at DATETIME
            )
            ''')
            
            conn.commit()
            conn.close()
            self.logger.info("Database initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {str(e)}")
            raise

    def log_operation(self, operation_type: str, source_path: str, 
                     destination_path: Optional[str] = None, 
                     status: str = "success", details: str = ""):
        """Log an operation to both file and database."""
        # Log to file
        self.logger.info(f"{operation_type}: {source_path} -> {destination_path} ({status})")
        
        # Log to database
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO operations (operation_type, source_path, destination_path, status, details)
        VALUES (?, ?, ?, ?, ?)
        ''', (operation_type, source_path, destination_path, status, details))
        conn.commit()
        conn.close()

    def log_file_metadata(self, file_path: str, file_hash: str, file_type: str,
                         file_size: int, last_modified: datetime, created_at: datetime):
        """Log file metadata to database."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute('''
        INSERT OR REPLACE INTO file_metadata 
        (file_path, file_hash, file_type, file_size, last_modified, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (file_path, file_hash, file_type, file_size, last_modified, created_at))
        conn.commit()
        conn.close()

    def get_operation_history(self, limit: int = 100) -> List[Dict]:
        """Retrieve operation history from database."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute('''
        SELECT * FROM operations ORDER BY timestamp DESC LIMIT ?
        ''', (limit,))
        columns = [description[0] for description in cursor.description]
        operations = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        return operations

    def generate_report(self, start_date: Optional[datetime] = None,
                       end_date: Optional[datetime] = None) -> Dict:
        """Generate a summary report of operations."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        query = '''
        SELECT operation_type, status, COUNT(*) as count
        FROM operations
        WHERE 1=1
        '''
        params = []
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date)
            
        query += " GROUP BY operation_type, status"
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        report = {
            'total_operations': sum(row[2] for row in results),
            'operations_by_type': {},
            'success_rate': 0
        }
        
        for op_type, status, count in results:
            if op_type not in report['operations_by_type']:
                report['operations_by_type'][op_type] = {'success': 0, 'failure': 0}
            report['operations_by_type'][op_type][status] = count
        
        # Calculate success rate
        total_success = sum(op['success'] for op in report['operations_by_type'].values())
        if report['total_operations'] > 0:
            report['success_rate'] = (total_success / report['total_operations']) * 100
        
        conn.close()
        return report 
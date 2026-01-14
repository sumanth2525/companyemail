"""
Data Storage Module
Handles storing results in CSV, Excel, and SQLite formats.
"""

import csv
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import pandas as pd


class ResultStorage:
    """Handles storing results in multiple formats."""
    
    def __init__(self, output_dir: str = 'results'):
        """
        Initialize ResultStorage.
        
        Args:
            output_dir: Directory to store output files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate timestamp for unique filenames
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.timestamp = timestamp
    
    def save_to_csv(self, results: List[Dict], filename: Optional[str] = None) -> str:
        """
        Save results to CSV file.
        
        Args:
            results: List of result dictionaries
            filename: Optional custom filename
            
        Returns:
            Path to saved CSV file
        """
        if not filename:
            filename = f'results_{self.timestamp}.csv'
        
        filepath = self.output_dir / filename
        
        if not results:
            # Create empty file with headers
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'Company', 'URL', 'Email Found', 'Status', 
                    'Message ID', 'Error', 'Sender Email', 'Timestamp'
                ])
                writer.writeheader()
            return str(filepath)
        
        # Write results
        fieldnames = list(results[0].keys())
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        
        return str(filepath)
    
    def save_to_excel(self, results: List[Dict], filename: Optional[str] = None) -> str:
        """
        Save results to Excel file.
        
        Args:
            results: List of result dictionaries
            filename: Optional custom filename
            
        Returns:
            Path to saved Excel file
        """
        if not filename:
            filename = f'results_{self.timestamp}.xlsx'
        
        filepath = self.output_dir / filename
        
        if not results:
            # Create empty DataFrame with headers
            df = pd.DataFrame(columns=[
                'Company', 'URL', 'Email Found', 'Status', 
                'Message ID', 'Error', 'Sender Email', 'Timestamp'
            ])
        else:
            df = pd.DataFrame(results)
        
        df.to_excel(filepath, index=False, engine='openpyxl')
        
        return str(filepath)
    
    def save_to_sqlite(self, results: List[Dict], 
                      db_name: Optional[str] = None) -> str:
        """
        Save results to SQLite database.
        
        Args:
            results: List of result dictionaries
            db_name: Optional custom database name
            
        Returns:
            Path to saved database file
        """
        if not db_name:
            db_name = f'results_{self.timestamp}.db'
        
        db_path = self.output_dir / db_name
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT,
                url TEXT,
                email_found TEXT,
                status TEXT,
                message_id TEXT,
                error TEXT,
                sender_email TEXT,
                timestamp TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert results
        for result in results:
            cursor.execute('''
                INSERT INTO email_results 
                (company, url, email_found, status, message_id, error, sender_email, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                result.get('Company', ''),
                result.get('URL', ''),
                result.get('Email Found', ''),
                result.get('Status', ''),
                result.get('Message ID', ''),
                result.get('Error', ''),
                result.get('Sender Email', ''),
                result.get('Timestamp', '')
            ))
        
        conn.commit()
        conn.close()
        
        return str(db_path)
    
    def save_all_formats(self, results: List[Dict], 
                        base_name: Optional[str] = None) -> Dict[str, str]:
        """
        Save results to all formats (CSV, Excel, SQLite).
        
        Args:
            results: List of result dictionaries
            base_name: Optional base name for files
            
        Returns:
            Dictionary with paths to all saved files
        """
        if base_name:
            csv_file = self.save_to_csv(results, f'{base_name}.csv')
            excel_file = self.save_to_excel(results, f'{base_name}.xlsx')
            db_file = self.save_to_sqlite(results, f'{base_name}.db')
        else:
            csv_file = self.save_to_csv(results)
            excel_file = self.save_to_excel(results)
            db_file = self.save_to_sqlite(results)
        
        return {
            'csv': csv_file,
            'excel': excel_file,
            'sqlite': db_file
        }


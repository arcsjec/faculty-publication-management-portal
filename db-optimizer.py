"""
Database Optimization and Management Utilities
This module provides tools for database optimization, indexing, and backup management.
"""

from models import db
from sqlalchemy import text, Index
import os
import shutil
from datetime import datetime
from pathlib import Path


class DatabaseOptimizer:
    """Handles database optimization tasks including indexing"""
    
    @staticmethod
    def create_indexes():
        """Create database indexes for frequently queried fields"""
        print("Creating database indexes for optimal performance...")
        
        try:
            # User table indexes
            db.session.execute(text('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)'))
            db.session.execute(text('CREATE INDEX IF NOT EXISTS idx_users_role ON users(role)'))
            db.session.execute(text('CREATE INDEX IF NOT EXISTS idx_users_department ON users(department_id)'))
            db.session.execute(text('CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active)'))
            
            # Publication table indexes
            db.session.execute(text('CREATE INDEX IF NOT EXISTS idx_publications_user ON publications(user_id)'))
            db.session.execute(text('CREATE INDEX IF NOT EXISTS idx_publications_dept ON publications(department_id)'))
            db.session.execute(text('CREATE INDEX IF NOT EXISTS idx_publications_year ON publications(year)'))
            db.session.execute(text('CREATE INDEX IF NOT EXISTS idx_publications_status ON publications(status)'))
            db.session.execute(text('CREATE INDEX IF NOT EXISTS idx_publications_created ON publications(created_at)'))
            
            # Composite index for common query patterns
            db.session.execute(text('CREATE INDEX IF NOT EXISTS idx_publications_user_status ON publications(user_id, status)'))
            db.session.execute(text('CREATE INDEX IF NOT EXISTS idx_publications_dept_year ON publications(department_id, year)'))
            
            # Notification table indexes
            db.session.execute(text('CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id)'))
            db.session.execute(text('CREATE INDEX IF NOT EXISTS idx_notifications_read ON notifications(is_read)'))
            db.session.execute(text('CREATE INDEX IF NOT EXISTS idx_notifications_created ON notifications(created_at)'))
            db.session.execute(text('CREATE INDEX IF NOT EXISTS idx_notifications_user_read ON notifications(user_id, is_read)'))
            
            # ApplicationForm table indexes
            db.session.execute(text('CREATE INDEX IF NOT EXISTS idx_applications_tracking ON application_forms(tracking_id)'))
            db.session.execute(text('CREATE INDEX IF NOT EXISTS idx_applications_applicant ON application_forms(applicant_id)'))
            db.session.execute(text('CREATE INDEX IF NOT EXISTS idx_applications_status ON application_forms(status)'))
            db.session.execute(text('CREATE INDEX IF NOT EXISTS idx_applications_type ON application_forms(application_type)'))
            db.session.execute(text('CREATE INDEX IF NOT EXISTS idx_applications_submitted ON application_forms(submitted_at)'))
            
            # EditRequest table indexes
            db.session.execute(text('CREATE INDEX IF NOT EXISTS idx_editrequest_publication ON edit_requests(publication_id)'))
            db.session.execute(text('CREATE INDEX IF NOT EXISTS idx_editrequest_faculty ON edit_requests(faculty_id)'))
            db.session.execute(text('CREATE INDEX IF NOT EXISTS idx_editrequest_hod ON edit_requests(hod_id)'))
            db.session.execute(text('CREATE INDEX IF NOT EXISTS idx_editrequest_status ON edit_requests(status)'))
            
            # Feedback table indexes
            db.session.execute(text('CREATE INDEX IF NOT EXISTS idx_feedback_user ON feedbacks(user_id)'))
            db.session.execute(text('CREATE INDEX IF NOT EXISTS idx_feedback_dept ON feedbacks(department_id)'))
            db.session.execute(text('CREATE INDEX IF NOT EXISTS idx_feedback_status ON feedbacks(status)'))
            db.session.execute(text('CREATE INDEX IF NOT EXISTS idx_feedback_recipient ON feedbacks(recipient_role)'))
            
            # ACMPanel table indexes
            db.session.execute(text('CREATE INDEX IF NOT EXISTS idx_acmpanel_member ON acm_panel(member_id)'))
            db.session.execute(text('CREATE INDEX IF NOT EXISTS idx_acmpanel_active ON acm_panel(is_active)'))
            
            # ACMReview table indexes
            db.session.execute(text('CREATE INDEX IF NOT EXISTS idx_acmreview_application ON acm_reviews(application_id)'))
            db.session.execute(text('CREATE INDEX IF NOT EXISTS idx_acmreview_reviewer ON acm_reviews(reviewer_id)'))
            db.session.execute(text('CREATE INDEX IF NOT EXISTS idx_acmreview_decision ON acm_reviews(decision)'))
            
            # AuditLog table indexes
            db.session.execute(text('CREATE INDEX IF NOT EXISTS idx_auditlog_user ON audit_logs(user_id)'))
            db.session.execute(text('CREATE INDEX IF NOT EXISTS idx_auditlog_action ON audit_logs(action)'))
            db.session.execute(text('CREATE INDEX IF NOT EXISTS idx_auditlog_target ON audit_logs(target_type, target_id)'))
            db.session.execute(text('CREATE INDEX IF NOT EXISTS idx_auditlog_created ON audit_logs(created_at)'))
            
            # Circular table indexes
            db.session.execute(text('CREATE INDEX IF NOT EXISTS idx_circular_author ON circulars(author_id)'))
            db.session.execute(text('CREATE INDEX IF NOT EXISTS idx_circular_created ON circulars(created_at)'))
            
            # WalletTransaction table indexes
            db.session.execute(text('CREATE INDEX IF NOT EXISTS idx_wallet_user ON wallet_transactions(user_id)'))
            db.session.execute(text('CREATE INDEX IF NOT EXISTS idx_wallet_type ON wallet_transactions(transaction_type)'))
            db.session.execute(text('CREATE INDEX IF NOT EXISTS idx_wallet_created ON wallet_transactions(created_at)'))
            
            db.session.commit()
            print("✅ All database indexes created successfully!")
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating indexes: {str(e)}")
            return False
    
    @staticmethod
    def analyze_database():
        """Run ANALYZE to update database statistics for query optimization"""
        try:
            print("Analyzing database statistics...")
            db.session.execute(text('ANALYZE'))
            db.session.commit()
            print("✅ Database analysis complete!")
            return True
        except Exception as e:
            print(f"❌ Error analyzing database: {str(e)}")
            return False
    
    @staticmethod
    def vacuum_database():
        """Run VACUUM to reclaim space and optimize database (SQLite only)"""
        try:
            print("Vacuuming database to reclaim space...")
            # VACUUM cannot be run in a transaction
            db.session.execute(text('VACUUM'))
            print("✅ Database vacuum complete!")
            return True
        except Exception as e:
            print(f"❌ Error vacuuming database: {str(e)}")
            return False
    
    @staticmethod
    def get_database_stats():
        """Get database statistics and table sizes"""
        try:
            stats = {}
            
            # Get table row counts
            tables = [
                'users', 'departments', 'publications', 'notifications',
                'application_forms', 'edit_requests', 'feedbacks',
                'acm_panel', 'acm_reviews', 'audit_logs', 'circulars',
                'wallet_transactions', 'circular_reads', 'application_documents'
            ]
            
            for table in tables:
                try:
                    result = db.session.execute(text(f'SELECT COUNT(*) FROM {table}')).scalar()
                    stats[table] = result
                except:
                    stats[table] = 0
            
            return stats
            
        except Exception as e:
            print(f"❌ Error getting database stats: {str(e)}")
            return None


class DatabaseBackup:
    """Handles database backup and restoration"""
    
    BACKUP_DIR = Path('backups')
    DB_PATH = Path('sjec_publications.db')  # Updated to correct database filename
    
    def __init__(self):
        # Create backup directory if it doesn't exist
        self.BACKUP_DIR.mkdir(exist_ok=True)
    
    def create_backup(self, backup_name=None):
        """
        Create a database backup
        
        Args:
            backup_name: Optional custom name for backup. If None, uses timestamp.
        
        Returns:
            Path to backup file or None if failed
        """
        try:
            if not self.DB_PATH.exists():
                print(f"❌ Database file not found at {self.DB_PATH}")
                return None
            
            # Generate backup filename with timestamp
            if backup_name:
                backup_filename = f"{backup_name}.db"
            else:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_filename = f"backup_{timestamp}.db"
            
            backup_path = self.BACKUP_DIR / backup_filename
            
            # Copy database file
            shutil.copy2(self.DB_PATH, backup_path)
            
            # Get backup size
            size_mb = backup_path.stat().st_size / (1024 * 1024)
            
            print(f"✅ Backup created successfully!")
            print(f"   Location: {backup_path}")
            print(f"   Size: {size_mb:.2f} MB")
            
            return backup_path
            
        except Exception as e:
            print(f"❌ Backup failed: {str(e)}")
            return None
    
    def list_backups(self):
        """List all available backups"""
        try:
            backups = sorted(self.BACKUP_DIR.glob('*.db'), key=lambda p: p.stat().st_mtime, reverse=True)
            
            if not backups:
                print("No backups found.")
                return []
            
            print("\n📦 Available Backups:")
            print("-" * 70)
            
            backup_list = []
            for backup in backups:
                stat = backup.stat()
                size_mb = stat.st_size / (1024 * 1024)
                modified = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                
                backup_info = {
                    'filename': backup.name,
                    'path': backup,
                    'size_mb': size_mb,
                    'modified': modified
                }
                backup_list.append(backup_info)
                
                print(f"  {backup.name}")
                print(f"    Size: {size_mb:.2f} MB | Modified: {modified}")
                print()
            
            return backup_list
            
        except Exception as e:
            print(f"❌ Error listing backups: {str(e)}")
            return []
    
    def restore_backup(self, backup_filename):
        """
        Restore database from a backup
        
        Args:
            backup_filename: Name of backup file to restore
        
        Returns:
            True if successful, False otherwise
        """
        try:
            backup_path = self.BACKUP_DIR / backup_filename
            
            if not backup_path.exists():
                print(f"❌ Backup file not found: {backup_filename}")
                return False
            
            # Create a safety backup of current database
            print("Creating safety backup of current database...")
            safety_backup = self.create_backup('pre_restore_safety')
            
            if not safety_backup:
                print("❌ Failed to create safety backup. Restore cancelled.")
                return False
            
            # Restore the backup
            print(f"Restoring backup: {backup_filename}...")
            shutil.copy2(backup_path, self.DB_PATH)
            
            print("✅ Database restored successfully!")
            print(f"   Safety backup saved at: {safety_backup}")
            
            return True
            
        except Exception as e:
            print(f"❌ Restore failed: {str(e)}")
            return False
    
    def delete_old_backups(self, keep_count=10):
        """
        Delete old backups, keeping only the most recent ones
        
        Args:
            keep_count: Number of most recent backups to keep
        
        Returns:
            Number of backups deleted
        """
        try:
            backups = sorted(self.BACKUP_DIR.glob('*.db'), key=lambda p: p.stat().st_mtime, reverse=True)
            
            if len(backups) <= keep_count:
                print(f"No old backups to delete. Current count: {len(backups)}")
                return 0
            
            # Delete old backups
            deleted_count = 0
            for backup in backups[keep_count:]:
                # Don't delete safety backups
                if 'safety' not in backup.name:
                    backup.unlink()
                    deleted_count += 1
                    print(f"Deleted old backup: {backup.name}")
            
            print(f"✅ Deleted {deleted_count} old backups. Kept {keep_count} most recent.")
            return deleted_count
            
        except Exception as e:
            print(f"❌ Error deleting old backups: {str(e)}")
            return 0


def optimize_database():
    """Main function to run all optimization tasks"""
    print("\n" + "="*70)
    print("DATABASE OPTIMIZATION UTILITY")
    print("="*70 + "\n")
    
    optimizer = DatabaseOptimizer()
    
    # Create indexes
    print("\n[1/3] Creating Database Indexes...")
    optimizer.create_indexes()
    
    # Analyze database
    print("\n[2/3] Analyzing Database Statistics...")
    optimizer.analyze_database()
    
    # Get database stats
    print("\n[3/3] Gathering Database Statistics...")
    stats = optimizer.get_database_stats()
    
    if stats:
        print("\n📊 Database Table Statistics:")
        print("-" * 70)
        total_records = 0
        for table, count in sorted(stats.items()):
            print(f"  {table:30} {count:>10,} records")
            total_records += count
        print("-" * 70)
        print(f"  {'TOTAL':30} {total_records:>10,} records")
    
    print("\n✅ Database optimization complete!\n")


def backup_database():
    """Create a new database backup"""
    print("\n" + "="*70)
    print("DATABASE BACKUP UTILITY")
    print("="*70 + "\n")
    
    backup_manager = DatabaseBackup()
    backup_manager.create_backup()
    
    print("\n")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'optimize':
            optimize_database()
        elif command == 'backup':
            backup_database()
        elif command == 'list':
            backup_manager = DatabaseBackup()
            backup_manager.list_backups()
        elif command == 'restore':
            if len(sys.argv) < 3:
                print("Usage: python db_optimizer.py restore <backup_filename>")
            else:
                backup_manager = DatabaseBackup()
                backup_manager.restore_backup(sys.argv[2])
        elif command == 'cleanup':
            keep = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            backup_manager = DatabaseBackup()
            backup_manager.delete_old_backups(keep)
        elif command == 'stats':
            optimizer = DatabaseOptimizer()
            stats = optimizer.get_database_stats()
            if stats:
                print("\n📊 Database Statistics:")
                print("-" * 50)
                for table, count in sorted(stats.items()):
                    print(f"  {table:30} {count:>10,} records")
        else:
            print("Unknown command. Available commands:")
            print("  optimize  - Create indexes and optimize database")
            print("  backup    - Create database backup")
            print("  list      - List all backups")
            print("  restore   - Restore from backup")
            print("  cleanup   - Delete old backups")
            print("  stats     - Show database statistics")
    else:
        print("Usage: python db_optimizer.py <command>")
        print("\nAvailable commands:")
        print("  optimize  - Create indexes and optimize database")
        print("  backup    - Create database backup")
        print("  list      - List all backups")
        print("  restore <filename> - Restore from backup")
        print("  cleanup [keep_count] - Delete old backups (default: keep 10)")
        print("  stats     - Show database statistics")

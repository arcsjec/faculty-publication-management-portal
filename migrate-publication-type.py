"""
Migration: Add publication type, ISBN, and edition fields to publications table
Date: December 3, 2025
Purpose: Support different publication types (Journal, Book, Book Chapter) with dynamic forms
"""

from app import app, db
from models import Publication
from sqlalchemy import text

def migrate():
    """Add new columns to publications table"""
    with app.app_context():
        try:
            # Add publication_type column (Journal, Book, Book Chapter)
            db.session.execute(text("""
                ALTER TABLE publications 
                ADD COLUMN publication_type VARCHAR(50) DEFAULT 'Journal'
            """))
            print("✅ Added publication_type column")
            
            # Add ISBN column for books
            db.session.execute(text("""
                ALTER TABLE publications 
                ADD COLUMN isbn VARCHAR(50)
            """))
            print("✅ Added isbn column")
            
            # Add edition column for books
            db.session.execute(text("""
                ALTER TABLE publications 
                ADD COLUMN edition VARCHAR(50)
            """))
            print("✅ Added edition column")
            
            # Add last_citation_update timestamp for auto-update tracking
            db.session.execute(text("""
                ALTER TABLE publications 
                ADD COLUMN last_citation_update DATETIME
            """))
            print("✅ Added last_citation_update column")
            
            db.session.commit()
            print("\n✅ Migration completed successfully!")
            print("\nNew columns added:")
            print("  - publication_type: To distinguish Journal/Book/Book Chapter")
            print("  - isbn: For book publications")
            print("  - edition: For book editions")
            print("  - last_citation_update: Track when citations were last auto-updated")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Migration failed: {str(e)}")
            raise

if __name__ == '__main__':
    print("Starting publication type migration...")
    print("=" * 60)
    migrate()

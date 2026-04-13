"""
Citation Auto-Update System
Fetches and updates citation counts for journal publications from Google Scholar and Crossref
"""

import time
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fetch_citation_count(title, doi=None, authors=None):
    """
    Fetch current citation count from Crossref (if DOI available) or Google Scholar
    
    Args:
        title: Publication title
        doi: Digital Object Identifier (optional but preferred)
        authors: Author names (optional, for better Google Scholar matching)
    
    Returns:
        Integer citation count or None if not found
    """
    try:
        # Option 1: Try Crossref first if DOI is available (more reliable)
        if doi:
            try:
                from habanero import Crossref
                cr = Crossref()
                work = cr.works(ids=doi)
                citation_count = work['message'].get('is-referenced-by-count', 0)
                logger.info(f"Crossref: Found {citation_count} citations for DOI: {doi}")
                return citation_count
            except Exception as e:
                logger.warning(f"Crossref lookup failed for DOI {doi}: {str(e)}")
        
        # Option 2: Fallback to Google Scholar (requires title)
        if title:
            try:
                from scholarly import scholarly
                
                # Search for publication by title
                search_query = scholarly.search_pubs(title)
                time.sleep(2)  # Rate limiting - important!
                
                first_result = next(search_query, None)
                if first_result:
                    citation_count = int(first_result.get('num_citations', 0))
                    logger.info(f"Google Scholar: Found {citation_count} citations for '{title[:50]}...'")
                    return citation_count
                else:
                    logger.warning(f"No Google Scholar results for '{title[:50]}...'")
                    return None
            except Exception as e:
                logger.error(f"Google Scholar lookup failed for '{title[:50]}...': {str(e)}")
                return None
        
        return None
        
    except Exception as e:
        logger.error(f"Citation fetch error: {str(e)}")
        return None


def update_publication_citations(app, update_all=False, publication_id=None):
    """
    Update citation counts for publications
    
    Args:
        app: Flask app instance (for app context)
        update_all: If True, update all publications (ignore 3-month window)
        publication_id: If provided, update only this specific publication
    
    Returns:
        Dictionary with update statistics
    """
    with app.app_context():
        from models import Publication, db
        from app import create_notification
        
        # Build query for publications to update
        query = Publication.query.filter(
            Publication.publication_type == 'Journal'  # Only journals have citations
        )
        
        if publication_id:
            # Update specific publication
            query = query.filter(Publication.id == publication_id)
        elif not update_all:
            # Only update publications older than 3 months
            three_months_ago = datetime.utcnow() - timedelta(days=90)
            query = query.filter(
                db.or_(
                    Publication.last_citation_update == None,
                    Publication.last_citation_update < three_months_ago
                )
            )
        
        publications = query.all()
        
        stats = {
            'total_checked': 0,
            'successfully_updated': 0,
            'failed': 0,
            'no_change': 0,
            'updates': []
        }
        
        for pub in publications:
            stats['total_checked'] += 1
            
            try:
                # Fetch new citation count
                new_citations = fetch_citation_count(
                    title=pub.title,
                    doi=pub.doi,
                    authors=pub.authors_names
                )
                
                if new_citations is not None:
                    old_count = pub.citation_count or 0
                    
                    if new_citations != old_count:
                        # Update publication
                        pub.citation_count = new_citations
                        pub.last_citation_update = datetime.utcnow()
                        
                        # Create in-app notification for significant changes (>5 new citations)
                        if new_citations - old_count >= 5:
                            try:
                                create_notification(
                                    pub.user_id,
                                    "📚 Citation Update",
                                    f"'{pub.title[:60]}...' has {new_citations} citations (was {old_count}). "
                                    f"+{new_citations - old_count} new citations!",
                                    'info',
                                    send_email=False  # In-app only
                                )
                            except:
                                pass  # Don't fail update if notification fails
                        
                        stats['successfully_updated'] += 1
                        stats['updates'].append({
                            'id': pub.id,
                            'title': pub.title[:50],
                            'old': old_count,
                            'new': new_citations,
                            'change': new_citations - old_count
                        })
                        
                        logger.info(f"Updated pub {pub.id}: {old_count} → {new_citations} citations")
                    else:
                        stats['no_change'] += 1
                        # Still update timestamp to avoid checking again soon
                        pub.last_citation_update = datetime.utcnow()
                else:
                    stats['failed'] += 1
                    logger.warning(f"Could not fetch citations for pub {pub.id}")
                
            except Exception as e:
                stats['failed'] += 1
                logger.error(f"Citation update failed for pub {pub.id}: {str(e)}")
                continue
        
        # Commit all changes
        db.session.commit()
        
        logger.info(f"""
Citation Update Complete:
- Total checked: {stats['total_checked']}
- Successfully updated: {stats['successfully_updated']}
- No change: {stats['no_change']}
- Failed: {stats['failed']}
        """)
        
        return stats


def manual_citation_update(app, publication_id):
    """
    Manually update citations for a specific publication (admin/user triggered)
    
    Args:
        app: Flask app instance
        publication_id: ID of publication to update
    
    Returns:
        Tuple of (success: bool, message: str, new_count: int or None)
    """
    with app.app_context():
        from models import Publication, db
        
        pub = Publication.query.get(publication_id)
        if not pub:
            return False, "Publication not found", None
        
        if pub.publication_type != 'Journal':
            return False, "Only journal publications have citations", None
        
        try:
            new_citations = fetch_citation_count(
                title=pub.title,
                doi=pub.doi,
                authors=pub.authors_names
            )
            
            if new_citations is not None:
                old_count = pub.citation_count or 0
                pub.citation_count = new_citations
                pub.last_citation_update = datetime.utcnow()
                db.session.commit()
                
                return True, f"Updated: {old_count} → {new_citations} citations", new_citations
            else:
                return False, "Could not fetch citation data from Google Scholar or Crossref", None
                
        except Exception as e:
            logger.error(f"Manual citation update failed: {str(e)}")
            return False, f"Error: {str(e)}", None


# Standalone script execution
if __name__ == '__main__':
    import sys
    sys.path.insert(0, '.')
    
    from app import app
    
    print("=" * 60)
    print("CITATION AUTO-UPDATE UTILITY")
    print("=" * 60)
    
    import argparse
    parser = argparse.ArgumentParser(description='Update publication citations')
    parser.add_argument('--all', action='store_true', help='Update all publications (ignore 3-month window)')
    parser.add_argument('--pub-id', type=int, help='Update specific publication by ID')
    
    args = parser.parse_args()
    
    if args.pub_id:
        print(f"\nUpdating publication ID: {args.pub_id}")
        success, message, count = manual_citation_update(app, args.pub_id)
        print(f"Result: {message}")
    else:
        print(f"\nUpdate mode: {'ALL publications' if args.all else 'Publications older than 3 months'}")
        print("Starting citation update...\n")
        
        stats = update_publication_citations(app, update_all=args.all)
        
        print("\n" + "=" * 60)
        print("UPDATE SUMMARY")
        print("=" * 60)
        print(f"Total publications checked: {stats['total_checked']}")
        print(f"Successfully updated: {stats['successfully_updated']}")
        print(f"No change: {stats['no_change']}")
        print(f"Failed: {stats['failed']}")
        
        if stats['updates']:
            print("\nUpdates:")
            for update in stats['updates']:
                print(f"  - {update['title']}: {update['old']} → {update['new']} ({update['change']:+d})")

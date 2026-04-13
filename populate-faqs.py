"""
Populate initial FAQ entries for the portal
Run this script once to add default FAQs
"""

from app import app, db
from models import FAQ

def populate_faqs():
    """Add initial FAQ entries"""
    
    with app.app_context():
        # Check if FAQs already exist
        existing_count = FAQ.query.count()
        if existing_count > 0:
            print(f"⚠️  {existing_count} FAQs already exist. Skipping...")
            return
        
        faqs_data = [
            # General FAQs
            {
                'category': 'General',
                'question': 'What is the SJEC Faculty Publication Portal?',
                'answer': 'The SJEC Faculty Publication Portal is a comprehensive system designed to manage faculty publications, research incentives, and approval workflows. It helps track publications, calculate EPP points, manage financial incentives, and streamline the approval process.',
                'display_order': 1
            },
            {
                'category': 'General',
                'question': 'How do I register for an account?',
                'answer': 'Click on "Register" in the top-right corner of the login page. Fill in your name, SJEC email address (@sjec.ac.in), department, and password. After submitting, you will receive a welcome email with your login credentials.',
                'display_order': 2
            },
            {
                'category': 'General',
                'question': 'I forgot my password. How can I reset it?',
                'answer': 'Currently, password reset is handled by the admin. Please contact your department HoD or email admin@sjec.ac.in with your request. Provide your registered email address for verification.',
                'display_order': 3
            },
            {
                'category': 'General',
                'question': 'Who can I contact for support?',
                'answer': 'For technical issues, submit feedback through the portal or email admin@sjec.ac.in. For publication-related queries, contact your department HoD. For research policy questions, reach out to the Dean R&D.',
                'display_order': 4
            },
            
            # Publications FAQs
            {
                'category': 'Publications',
                'question': 'What types of publications can I submit?',
                'answer': 'You can submit: Conference Papers (National/International), Journal Articles (SCI/Scopus/UGC/Others), Books (Textbooks, Edited Volumes), Book Chapters, and Patents (Filed/Granted).',
                'display_order': 1
            },
            {
                'category': 'Publications',
                'question': 'What is the approval workflow for publications?',
                'answer': 'The standard workflow is: Faculty Submission → HoD Review → Dean R&D Review → Principal/Director Final Approval. For ACM journals, an additional ACM panel review is included. Each approver receives email notifications when action is required.',
                'display_order': 2
            },
            {
                'category': 'Publications',
                'question': 'What are FA, CA, and ACM author types?',
                'answer': '<strong>FA (First Author):</strong> Principal investigator or lead researcher<br><strong>CA (Corresponding Author):</strong> Primary contact for the publication<br><strong>ACM (Additional Co-Member):</strong> Contributing authors from SJEC<br><br>You must mark yourself with the appropriate type when adding authors.',
                'display_order': 3
            },
            {
                'category': 'Publications',
                'question': 'Can I edit my publication after submission?',
                'answer': 'Once submitted, publications cannot be directly edited. You must request edit permission from your HoD through the "Request Edit Permission" button. After the first edit, a second edit requires admin approval. Always create necessary backups before editing.',
                'display_order': 4
            },
            {
                'category': 'Publications',
                'question': 'What documents do I need to upload?',
                'answer': 'Required: Publication PDF (full paper)<br>Optional but recommended: Acceptance letter, certificate of presentation, copyright transfer form, indexing proof (for journals). Upload all documents in the "Supporting Documents" section.',
                'display_order': 5
            },
            {
                'category': 'Publications',
                'question': 'Why was my publication rejected?',
                'answer': 'Check the rejection comments provided by the reviewer. Common reasons: Incomplete information, missing documents, incorrect classification, insufficient proof of publication, or policy non-compliance. You can resubmit after addressing the issues.',
                'display_order': 6
            },
            
            # Wallet & Incentives FAQs
            {
                'category': 'Wallet',
                'question': 'What are EPP points?',
                'answer': 'EPP (Excellence Performance Points) are awarded based on publication type and quality. Each EPP point equals ₹2,000. Points are earned after final approval and are used to calculate research incentives. Check the User Guide for complete EPP point table.',
                'display_order': 1
            },
            {
                'category': 'Wallet',
                'question': 'How do I check my wallet balance?',
                'answer': 'Login to your dashboard and click on "My Wallet" or view the wallet widget on your dashboard. You will see: EPP balance, RRF (Research Reserve Fund) balance, transaction history, and total incentives earned.',
                'display_order': 2
            },
            {
                'category': 'Wallet',
                'question': 'When will I receive my publication incentive?',
                'answer': 'Incentives are credited after final approval by the Principal/Director. The amount is calculated based on EPP points and publication category. You will receive an email notification when the incentive is credited to your wallet.',
                'display_order': 3
            },
            {
                'category': 'Wallet',
                'question': 'What is RRF (Research Reserve Fund)?',
                'answer': 'RRF is your annual research allocation of ₹10,000. It can be used for: Conference registration fees, Article Processing Charges (APC), Publication costs, Research materials. Submit applications through the portal to utilize your RRF.',
                'display_order': 4
            },
            
            # Applications FAQs
            {
                'category': 'Applications',
                'question': 'What types of applications can I submit?',
                'answer': '1. <strong>Conference Registration:</strong> For national/international conference participation<br>2. <strong>Publication Incentive:</strong> Claim incentive after publication approval<br>3. <strong>Journal Support:</strong> Request APC fee support for journal publications',
                'display_order': 1
            },
            {
                'category': 'Applications',
                'question': 'How do I track my application status?',
                'answer': 'Navigate to "My Applications" from your dashboard. Each application shows: Tracking ID, Current status (HoD Review, ACM Review, Dean Review, etc.), Comments from reviewers, and Date of last update. You also receive email notifications at each stage.',
                'display_order': 2
            },
            {
                'category': 'Applications',
                'question': 'What is ACM review and when is it required?',
                'answer': 'ACM (Assessment Committee Members) review is required for certain high-impact publications and journal support requests. The Dean assigns ACM members who provide technical validation. Two ACM approvals are required, with automatic forwarding after 48 hours if not all reviews are complete.',
                'display_order': 3
            },
            
            # Technical FAQs
            {
                'category': 'Technical',
                'question': 'Which browsers are supported?',
                'answer': 'The portal works best on: Google Chrome (recommended), Mozilla Firefox, Microsoft Edge, and Safari. Please use the latest version of your browser for optimal performance. Internet Explorer is not supported.',
                'display_order': 1
            },
            {
                'category': 'Technical',
                'question': 'My file upload is failing. What should I do?',
                'answer': 'Check: 1. File size is under 10 MB, 2. File format is PDF/JPG/PNG, 3. File name has no special characters, 4. Your internet connection is stable. If the issue persists, try a different browser or contact admin.',
                'display_order': 2
            },
            {
                'category': 'Technical',
                'question': 'I\'m not receiving email notifications. Why?',
                'answer': 'Check: 1. Your SJEC email inbox, 2. Spam/Junk folder, 3. Email filters/rules, 4. Inbox storage quota. Add noreply@sjec.ac.in to your contacts. If still not receiving, contact IT support or admin.',
                'display_order': 3
            },
            {
                'category': 'Technical',
                'question': 'What does the abbreviations button do?',
                'answer': 'Click the gold circular button at the bottom-right corner of any page to see a popup with common abbreviations used in the portal (FA, CA, ACM, HoD, HoR, RRF, EPP, etc.). This helps you understand terminology throughout the portal.',
                'display_order': 4
            }
        ]
        
        print("Adding initial FAQs...")
        
        for faq_data in faqs_data:
            faq = FAQ(**faq_data)
            db.session.add(faq)
        
        db.session.commit()
        
        print(f"✅ Successfully added {len(faqs_data)} FAQs!")
        print("\nFAQs by category:")
        
        # Display summary
        categories = {}
        for faq_data in faqs_data:
            cat = faq_data['category']
            categories[cat] = categories.get(cat, 0) + 1
        
        for cat, count in sorted(categories.items()):
            print(f"  {cat}: {count} FAQs")


if __name__ == '__main__':
    populate_faqs()

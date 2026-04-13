from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from zoneinfo import ZoneInfo

db = SQLAlchemy()

# IST timezone
IST = ZoneInfo('Asia/Kolkata')

def now_ist():
    """Get current time in Asia/Kolkata timezone"""
    return datetime.now(IST)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'faculty', 'hod', 'principal', 'vice_principal', 'dean', 'admin', 'dean_secretary', 'director'
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    profile_picture = db.Column(db.String(300), nullable=True)  # Filename for profile picture
    signature = db.Column(db.String(300), nullable=True)  # Filename for digital signature
    
    # Wallet System (RRF - Research Reserve Fund)
    wallet_balance = db.Column(db.Float, default=10000.0)  # Annual RRF allocation
    epp_balance = db.Column(db.Float, default=0.0)  # Earned Publication Points balance (each point = Rs 2,000)
    
    # Account status
    is_active = db.Column(db.Boolean, default=True)  # False = disabled account
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    department = db.relationship('Department', foreign_keys='User.department_id', backref='users')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.email}>'


class Department(db.Model):
    __tablename__ = 'departments'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    
    # Head of Research (HoR) fields
    head_of_research_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    hor_appointed_at = db.Column(db.DateTime)
    hor_appointed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    hor_term_end_date = db.Column(db.Date)
    
    # Relationships
    head_of_research = db.relationship('User', foreign_keys=[head_of_research_id], backref='dept_head_of_research')
    appointed_by_user = db.relationship('User', foreign_keys=[hor_appointed_by], backref='departments_appointed_hor')
    
    def __repr__(self):
        return f'<Department {self.name}>'


class Publication(db.Model):
    __tablename__ = 'publications'
    
    id = db.Column(db.Integer, primary_key=True)
    publication_type = db.Column(db.String(50), default='Journal')  # Journal, Book, Book Chapter
    title = db.Column(db.String(500), nullable=False)
    abstract = db.Column(db.Text)
    publisher_name = db.Column(db.String(200))
    authors_names = db.Column(db.Text, nullable=False)  # Comma-separated
    publication_details = db.Column(db.Text)  # Journal/Conference name, volume, issue, pages
    journal_conference_name = db.Column(db.String(300))
    volume = db.Column(db.String(50))
    issue = db.Column(db.String(50))
    pages = db.Column(db.String(50))
    indexing_status = db.Column(db.String(100))  # Scopus, Web of Science, etc.
    quartile = db.Column(db.String(10))  # Q1, Q2, Q3, Q4
    impact_factor = db.Column(db.Float)
    isbn = db.Column(db.String(50))  # For books
    edition = db.Column(db.String(50))  # For books
    doi = db.Column(db.String(200))
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer)  # 1-12
    citation_count = db.Column(db.Integer, default=0)
    last_citation_update = db.Column(db.DateTime)  # Track auto-update
    bibtex_entry = db.Column(db.Text)
    pdf_filename = db.Column(db.String(300))
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    
    # Save vs Confirm workflow
    status = db.Column(db.String(20), default='saved', nullable=False)  # 'saved' or 'confirmed'
    confirmed_at = db.Column(db.DateTime, nullable=True)
    can_edit = db.Column(db.Boolean, default=True)  # HoD can grant edit permission
    edit_count = db.Column(db.Integer, default=0)  # Track number of times edited after confirmation
    edit_granted_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    edit_granted_at = db.Column(db.DateTime, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    department = db.relationship('Department', backref='publications')
    author = db.relationship('User', foreign_keys=[user_id], backref=db.backref('publications', lazy='dynamic'))
    edit_granter = db.relationship('User', foreign_keys=[edit_granted_by], backref='edit_grants', overlaps="author,publications")
    
    def __repr__(self):
        return f'<Publication {self.title[:50]}>'


class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), default='info')  # 'info', 'warning', 'success', 'danger'
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Link to publication if related
    publication_id = db.Column(db.Integer, db.ForeignKey('publications.id'), nullable=True)
    
    # Relationships
    user = db.relationship('User', backref='notifications')
    publication = db.relationship('Publication', backref='notifications')
    
    def __repr__(self):
        return f'<Notification {self.title}>'


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(100), nullable=False)  # 'confirm', 'edit_granted', 'delete', etc.
    target_type = db.Column(db.String(50), nullable=False)  # 'publication', 'user', etc.
    target_id = db.Column(db.Integer, nullable=True)
    details = db.Column(db.Text)  # JSON string with additional details
    ip_address = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='audit_logs')
    
    def __repr__(self):
        return f'<AuditLog {self.action} by User {self.user_id}>'


class EditRequest(db.Model):
    __tablename__ = 'edit_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    publication_id = db.Column(db.Integer, db.ForeignKey('publications.id'), nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    hod_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # For second edit approval
    status = db.Column(db.String(20), default='pending', nullable=False)  # 'pending', 'approved', 'denied', 'pending_admin', 'admin_approved', 'admin_denied'
    edit_level = db.Column(db.Integer, default=1)  # 1 = first edit, 2 = second edit
    reason = db.Column(db.Text)  # Optional reason from faculty
    response = db.Column(db.Text)  # Optional response from HoD
    admin_response = db.Column(db.Text)  # Optional response from Admin for second edit
    requested_at = db.Column(db.DateTime, default=datetime.utcnow)
    responded_at = db.Column(db.DateTime, nullable=True)
    admin_responded_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    publication = db.relationship('Publication', backref='edit_requests')
    faculty = db.relationship('User', foreign_keys=[faculty_id], backref='my_edit_requests')
    hod = db.relationship('User', foreign_keys=[hod_id], backref='edit_requests_to_review')
    admin = db.relationship('User', foreign_keys=[admin_id], backref='admin_edit_requests_to_review')
    
    def __repr__(self):
        return f'<EditRequest {self.id} - Level {self.edit_level} - {self.status}>'


class Feedback(db.Model):
    __tablename__ = 'feedbacks'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)  # For HoD filtering
    recipient_role = db.Column(db.String(20), nullable=False)  # 'hod', 'principal', 'admin'
    category = db.Column(db.String(50), nullable=False)  # 'bug', 'feature', 'content', 'general'
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    screenshot_filename = db.Column(db.String(300), nullable=True)
    status = db.Column(db.String(20), default='pending', nullable=False)  # 'pending', 'resolved'
    resolved_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    resolved_at = db.Column(db.DateTime, nullable=True)
    resolution_comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='feedbacks_sent')
    department = db.relationship('Department', backref='feedbacks')
    resolver = db.relationship('User', foreign_keys=[resolved_by], backref='feedbacks_resolved')
    
    def __repr__(self):
        return f'<Feedback {self.subject}>'


class ACMPanel(db.Model):
    """Assessment Committee Members Panel managed by Dean"""
    __tablename__ = 'acm_panel'
    
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    appointed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Dean
    appointed_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    member = db.relationship('User', foreign_keys=[member_id], backref='acm_membership')
    appointer = db.relationship('User', foreign_keys=[appointed_by], backref='acm_appointments')
    
    def __repr__(self):
        return f'<ACMPanel Member: {self.member.name}>'


class ApplicationForm(db.Model):
    """Base model for all three application types"""
    __tablename__ = 'application_forms'
    
    id = db.Column(db.Integer, primary_key=True)
    tracking_id = db.Column(db.String(50), unique=True, nullable=False)  # e.g., CR2024001, PI2024001, JS2024001
    application_type = db.Column(db.String(50), nullable=False)  # 'conference_registration', 'publication_incentive', 'journal_support'
    
    # Applicant Details (pre-filled)
    applicant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    applicant_name = db.Column(db.String(100), nullable=False)
    
    # Common Fields
    title_of_paper = db.Column(db.String(500), nullable=False)
    type_of_publication = db.Column(db.String(50))  # 'National' / 'International'
    
    # NEW: Publication Category and Author Counts (as per SJEC Circular 2025/091)
    publication_category = db.Column(db.String(50))  # 'Journal' / 'Book' / 'Book Chapter' / 'Conference'
    is_national_international = db.Column(db.String(20))  # 'National' / 'International'
    
    # Author counts (only SJEC staff, including applicant)
    num_first_authors_sjec = db.Column(db.Integer, default=0)  # 0 or 1
    num_corresponding_authors_sjec = db.Column(db.Integer, default=0)  # 0 or 1
    num_coauthors_sjec = db.Column(db.Integer, default=0)  # 0 to 10
    
    # Conference Registration Specific
    type_of_conference = db.Column(db.String(50))  # 'National' / 'International'
    conference_name = db.Column(db.String(300))
    conference_organizer = db.Column(db.String(300))
    conference_place_date = db.Column(db.String(200))  # Legacy field (combined)
    conference_place = db.Column(db.String(200))  # Separate place field
    conference_date = db.Column(db.Date)  # Separate date field
    conference_fee = db.Column(db.Float)
    
    # Publication Incentive & Journal Support Common
    type_of_journal = db.Column(db.String(50))  # 'Peer-Reviewed' / 'Indexed' / 'Others'
    journal_name = db.Column(db.String(300))
    journal_quartile = db.Column(db.String(10))
    journal_impact_factor = db.Column(db.Float)
    indexing_type = db.Column(db.String(50))  # 'Scopus' / 'Web of Science' / 'Others'
    publisher_details = db.Column(db.String(300))
    publication_date = db.Column(db.Date)
    publication_pdf = db.Column(db.String(200))  # Path to uploaded PDF file (for publication incentive)
    
    # Publication Incentive Specific
    author_type = db.Column(db.String(50))  # 'Author' / 'Corresponding Author' / 'Co-Author'
    
    # Journal Support Specific
    apc_fees = db.Column(db.Float)  # Article Processing Charges (APC) fees in Rs
    expected_charges = db.Column(db.Float)  # Expected charges in Rs
    
    # Applicant Signature & Date
    applicant_signature_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Status
    status = db.Column(db.String(50), default='draft')  # 'draft', 'submitted', 'hod_review', 'hod_approved', 'acm_review', 'acm_approved', 'dean_review', 'dean_approved', 'principal_approved', 'director_approved', 'rejected'
    submitted_at = db.Column(db.DateTime)
    
    # HOD Approval (New Step)
    hod_approved = db.Column(db.Boolean)
    hod_comments = db.Column(db.Text)
    hod_reviewed_at = db.Column(db.DateTime)
    hod_reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # ACM Assessment
    acm_applicable = db.Column(db.String(10))  # 'Yes' / 'No'
    acm_comments = db.Column(db.Text)
    acm_review_date = db.Column(db.DateTime)
    acm_approvals_count = db.Column(db.Integer, default=0)
    acm_review_started_at = db.Column(db.DateTime)  # When ACM review started (for auto-forward logic)
    acm_second_approval_at = db.Column(db.DateTime)  # When 2nd approval received (starts 48-hour timer)
    acm_auto_forward_scheduled = db.Column(db.Boolean, default=False)  # Whether auto-forward is scheduled
    acm_auto_forwarded = db.Column(db.Boolean, default=False)  # Whether it was auto-forwarded by timer
    acm_approved_at = db.Column(db.DateTime)  # When application was forwarded to Dean (2nd or 3rd approval)
    
    # Dean Recommendation
    dean_recommended_amount = db.Column(db.Float)
    dean_first_author_amount = db.Column(db.Float)  # For Publication Incentive
    dean_corresponding_author_amount = db.Column(db.Float)  # For Publication Incentive
    dean_coauthor_amount = db.Column(db.Float)  # For Publication Incentive
    dean_signature_date = db.Column(db.DateTime)
    dean_comments = db.Column(db.Text)
    dean_approved = db.Column(db.Boolean)
    dean_reviewed_at = db.Column(db.DateTime)
    dean_reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    dean_signature_snapshot = db.Column(db.LargeBinary)  # Snapshot of dean's signature at approval time
    dean_name_snapshot = db.Column(db.String(200))  # Snapshot of dean's name at approval time
    
    # Final Approvals
    principal_approved = db.Column(db.Boolean, default=False)
    principal_signature_date = db.Column(db.DateTime)
    principal_approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))  # Who approved (Principal or Dean Secretary)
    principal_approved_at = db.Column(db.DateTime)
    principal_rejected = db.Column(db.Boolean, default=False)
    principal_rejection_reason = db.Column(db.Text)
    principal_rejected_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    principal_rejected_at = db.Column(db.DateTime)
    principal_signature_snapshot = db.Column(db.LargeBinary)  # Snapshot of principal's signature at approval time
    principal_name_snapshot = db.Column(db.String(200))  # Snapshot of principal's name at approval time
    
    director_approved = db.Column(db.Boolean, default=False)
    director_signature_date = db.Column(db.DateTime)
    director_approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))  # Who approved (Director or Dean Secretary)
    director_approved_at = db.Column(db.DateTime)
    director_rejected = db.Column(db.Boolean, default=False)
    director_rejection_reason = db.Column(db.Text)
    director_rejected_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    director_rejected_at = db.Column(db.DateTime)
    director_signature_snapshot = db.Column(db.LargeBinary)  # Snapshot of director's signature at approval time
    director_name_snapshot = db.Column(db.String(200))  # Snapshot of director's name at approval time
    
    # Dean Secretary Final Approval (Disperse Amount)
    dean_sec_approval_date = db.Column(db.Date)  # Date of final approval/disbursement
    dean_sec_principal_sign_attached = db.Column(db.Boolean, default=False)  # Optional: Principal signature attached
    dean_sec_director_sign_attached = db.Column(db.Boolean, default=False)  # Optional: Director signature attached
    dean_sec_comments = db.Column(db.Text)  # Comments for final approval/disbursement
    dean_sec_approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))  # Dean Secretary who processed final approval
    dean_sec_approved_at = db.Column(db.DateTime)  # When final approval was processed
    dean_sec_signature_snapshot = db.Column(db.LargeBinary)  # Snapshot of dean sec's signature at approval time
    dean_sec_name_snapshot = db.Column(db.String(200))  # Snapshot of dean sec's name at approval time
    
    # Wallet Transaction
    wallet_debited = db.Column(db.Boolean, default=False)
    wallet_transaction_id = db.Column(db.Integer, db.ForeignKey('wallet_transactions.id'))
    epp_awarded = db.Column(db.Float, default=0.0)  # EPP points awarded for this publication
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    applicant = db.relationship('User', foreign_keys=[applicant_id], backref='applications')
    
    def __repr__(self):
        return f'<Application {self.tracking_id} - {self.application_type}>'


class ACMReview(db.Model):
    """Individual ACM member reviews for each application"""
    __tablename__ = 'acm_reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('application_forms.id'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Review Decision
    decision = db.Column(db.String(20))  # 'approved', 'rejected', 'pending'
    comments = db.Column(db.Text)
    reviewed_at = db.Column(db.DateTime)
    
    # ACM Reviewer Snapshot - preserve signature and name at review time
    reviewer_signature_snapshot = db.Column(db.LargeBinary)
    reviewer_name_snapshot = db.Column(db.String(200))
    
    # Edited Fields (if ACM edits the application)
    edited_fields = db.Column(db.Text)  # JSON string of edited fields
    
    # Relationships
    application = db.relationship('ApplicationForm', backref='acm_reviews')
    reviewer = db.relationship('User', backref='acm_reviews_given')
    
    def __repr__(self):
        return f'<ACMReview by {self.reviewer.name} - {self.decision}>'


class ApplicationDocument(db.Model):
    """Supporting documents for applications (receipts, certificates, PDFs, etc.)"""
    __tablename__ = 'application_documents'
    
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('application_forms.id'), nullable=False)
    
    # File Details
    filename = db.Column(db.String(300), nullable=False)  # Original filename
    stored_filename = db.Column(db.String(300), nullable=False)  # Stored filename with timestamp
    file_type = db.Column(db.String(50), nullable=False)  # 'pdf', 'png', 'jpeg', 'docx', etc.
    file_size = db.Column(db.Integer)  # File size in bytes
    document_type = db.Column(db.String(100))  # 'receipt', 'certificate', 'publication', 'other'
    
    # Metadata
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    application = db.relationship('ApplicationForm', backref='documents')
    uploader = db.relationship('User', backref='uploaded_documents')
    
    def __repr__(self):
        return f'<ApplicationDocument {self.filename} for App {self.application_id}>'


class FacultyWallet(db.Model):
    """Wallet system for faculty to track grants and incentives"""
    __tablename__ = 'faculty_wallets'
    
    id = db.Column(db.Integer, primary_key=True)
    faculty_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    
    # Balance Tracking
    total_received = db.Column(db.Float, default=0.0)
    total_withdrawn = db.Column(db.Float, default=0.0)
    current_balance = db.Column(db.Float, default=0.0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    faculty = db.relationship('User', backref=db.backref('wallet', uselist=False))
    
    def __repr__(self):
        return f'<Wallet for {self.faculty.name} - Balance: {self.current_balance}>'


class IncentiveConfig(db.Model):
    """Configuration for publication incentives and cash awards - Editable by Dean"""
    __tablename__ = 'incentive_config'
    
    id = db.Column(db.Integer, primary_key=True)
    # Q1-Q4 Journal Quartile Amounts
    q1_base_amount = db.Column(db.Float, default=30000.0)
    q1_if_multiplier = db.Column(db.Float, default=2000.0)
    q1_max_amount = db.Column(db.Float, default=40000.0)
    
    q2_base_amount = db.Column(db.Float, default=20000.0)
    q2_if_multiplier = db.Column(db.Float, default=2000.0)
    q2_max_amount = db.Column(db.Float, default=30000.0)
    
    q3_base_amount = db.Column(db.Float, default=10000.0)
    q3_if_multiplier = db.Column(db.Float, default=2000.0)
    q3_max_amount = db.Column(db.Float, default=20000.0)
    
    q4_base_amount = db.Column(db.Float, default=5000.0)
    q4_if_multiplier = db.Column(db.Float, default=2000.0)
    q4_max_amount = db.Column(db.Float, default=10000.0)
    
    scopus_wos_amount = db.Column(db.Float, default=5000.0)
    conference_amount = db.Column(db.Float, default=5000.0)
    
    # EPP Points per quartile
    q1_epp_fa = db.Column(db.Integer, default=5)  # First Author
    q1_epp_ca = db.Column(db.Integer, default=5)  # Corresponding Author
    q1_epp_both = db.Column(db.Integer, default=10)  # Both FA and CA
    
    q2_epp_fa = db.Column(db.Integer, default=4)
    q2_epp_ca = db.Column(db.Integer, default=4)
    q2_epp_both = db.Column(db.Integer, default=8)
    
    q3_epp_fa = db.Column(db.Integer, default=3)
    q3_epp_ca = db.Column(db.Integer, default=3)
    q3_epp_both = db.Column(db.Integer, default=6)
    
    q4_epp_fa = db.Column(db.Integer, default=2)
    q4_epp_ca = db.Column(db.Integer, default=2)
    q4_epp_both = db.Column(db.Integer, default=4)
    
    scopus_wos_epp_fa = db.Column(db.Integer, default=1)
    scopus_wos_epp_ca = db.Column(db.Integer, default=1)
    scopus_wos_epp_both = db.Column(db.Integer, default=2)
    
    # Annual RRF allocation
    annual_rrf_amount = db.Column(db.Float, default=10000.0)
    
    # EPP conversion rate
    epp_to_inr_rate = db.Column(db.Float, default=2000.0)  # Each EPP = Rs 2,000
    
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    def __repr__(self):
        return f'<IncentiveConfig ID:{self.id}>'


class WalletTransaction(db.Model):
    """Track all wallet transactions for faculty"""
    __tablename__ = 'wallet_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    transaction_type = db.Column(db.String(50), nullable=False)  # 'credit', 'debit', 'annual_dispersal', 'epp_earned', 'application_approved'
    amount = db.Column(db.Float, nullable=False)
    balance_after = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    application_id = db.Column(db.Integer, db.ForeignKey('application_forms.id'), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='wallet_transactions_list')
    creator = db.relationship('User', foreign_keys=[created_by])
    application = db.relationship('ApplicationForm', foreign_keys=[application_id], backref='wallet_transactions_history')
    
    def __repr__(self):
        return f'<WalletTransaction {self.transaction_type} - Rs {self.amount}>'


class Circular(db.Model):
    """Circular/Announcements model"""
    __tablename__ = 'circulars'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    subject = db.Column(db.String(500), nullable=True)
    body = db.Column(db.Text, nullable=True)
    file_path = db.Column(db.String(500))
    file_type = db.Column(db.String(20))  # 'pdf', 'jpeg', 'png'
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=now_ist)
    updated_at = db.Column(db.DateTime, default=now_ist, onupdate=now_ist)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    uploader = db.relationship('User', backref='circulars')
    
    def __repr__(self):
        return f'<Circular {self.id} - {self.title}>'


class CircularRead(db.Model):
    """Track which users have read which circulars"""
    __tablename__ = 'circular_reads'
    
    id = db.Column(db.Integer, primary_key=True)
    circular_id = db.Column(db.Integer, db.ForeignKey('circulars.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    read_at = db.Column(db.DateTime, default=now_ist)
    
    # Relationships
    circular = db.relationship('Circular', backref='reads')
    user = db.relationship('User', backref='circular_reads')
    
    def __repr__(self):
        return f'<CircularRead {self.circular_id} by User {self.user_id}>'


class FAQ(db.Model):
    """Frequently Asked Questions model"""
    __tablename__ = 'faqs'
    
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100), nullable=False)  # 'General', 'Publications', 'Wallet', 'Applications', 'Technical'
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    display_order = db.Column(db.Integer, default=0)  # For custom ordering
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=now_ist)
    updated_at = db.Column(db.DateTime, default=now_ist, onupdate=now_ist)
    view_count = db.Column(db.Integer, default=0)  # Track popularity
    
    # Relationships
    creator = db.relationship('User', backref='faqs_created')
    
    def __repr__(self):
        return f'<FAQ {self.id} - {self.category}>'

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, TextAreaField, SelectField, IntegerField, FloatField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Optional, NumberRange, Length
from models import User
import re
from datetime import datetime
import pytz

# IST timezone
IST = pytz.timezone('Asia/Kolkata')

def validate_bibtex(form, field):
    """Custom validator for BibTeX format"""
    if field.data and field.data.strip():
        bibtex_text = field.data.strip()
        # Valid BibTeX entry types
        valid_types = ['article', 'book', 'inproceedings', 'conference', 'proceedings', 
                      'incollection', 'inbook', 'booklet', 'manual', 'techreport', 
                      'mastersthesis', 'phdthesis', 'misc', 'unpublished']
        
        # Check if it starts with @<valid_type>{ and ends with }}
        bibtex_pattern = r'^@(' + '|'.join(valid_types) + r')\s*\{[^,]+,[\s\S]+\}\s*\}$'
        if not re.match(bibtex_pattern, bibtex_text, re.IGNORECASE | re.MULTILINE):
            raise ValidationError('Please enter BibTeX in correct format. Must start with @article, @book, @inproceedings, etc. and end with }}')

def validate_year(form, field):
    """Custom validator for year - must be exactly 4 digits and not in future"""
    if field.data:
        # Get current date in IST
        now_ist = datetime.now(IST)
        current_year = now_ist.year
        current_month = now_ist.month
        
        year_str = str(field.data)
        if len(year_str) != 4:
            raise ValidationError('Year must be exactly 4 digits (e.g., 2024, not 24)')
        
        if field.data < 2002:
            raise ValidationError('Year must be 2002 or later')
        
        if field.data > current_year:
            raise ValidationError(f'Year cannot be in the future. Current year is {current_year}')
        
        # If year is current year, check month to prevent future dates
        if field.data == current_year and hasattr(form, 'month') and form.month.data:
            if form.month.data > current_month:
                raise ValidationError(f'Cannot select a future month. Current month is {current_month}')

class RegistrationForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    department = SelectField('Department', coerce=int, validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, message='Password must be at least 6 characters long.')])
    confirm_password = PasswordField('Confirm Password', 
                                    validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    
    def validate_email(self, email):
        if not email.data.endswith('@sjec.ac.in'):
            raise ValidationError('Only @sjec.ac.in email addresses are allowed.')
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired()])
    confirm_new_password = PasswordField('Confirm New Password', 
                                         validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Change Password')


class PublicationForm(FlaskForm):
    # Publication Type Selector (NEW)
    publication_type = SelectField('Publication Type',
                                  choices=[('', 'Select Type'), 
                                          ('Journal', 'Journal Article'),
                                          ('Book', 'Book'),
                                          ('Book Chapter', 'Book Chapter')],
                                  validators=[DataRequired()])
    
    title = StringField('Title', validators=[DataRequired()])
    abstract = TextAreaField('Abstract')
    publisher_name = StringField('Publisher Name')
    authors_names = TextAreaField('Authors Names (comma-separated)', validators=[DataRequired()])
    
    # Journal-specific fields
    journal_conference_name = StringField('Journal/Conference Name')
    volume = StringField('Volume')
    issue = StringField('Issue')
    pages = StringField('Pages')
    indexing_status = SelectField('Indexing Status', 
                                  choices=[('', 'Select'), ('Scopus', 'Scopus'), 
                                          ('Web of Science', 'Web of Science'), 
                                          ('SCI', 'SCI'), ('SCIE', 'SCIE'),
                                          ('ESCI', 'ESCI'), ('Other', 'Other')])
    quartile = SelectField('Quartile', 
                          choices=[('', 'Select'), ('Q1', 'Q1'), ('Q2', 'Q2'), 
                                  ('Q3', 'Q3'), ('Q4', 'Q4'), ('Non-Quartile', 'Non-Quartile')])
    impact_factor = FloatField('Impact Factor', validators=[Optional()])
    
    # Book-specific fields (NEW)
    isbn = StringField('ISBN Number')
    edition = StringField('Edition')
    
    # Common fields
    doi = StringField('DOI')
    year = IntegerField('Year', validators=[DataRequired(), NumberRange(min=2002, max=2100), validate_year])
    month = SelectField('Month', coerce=int,
                       choices=[(0, 'Select')] + [(i, str(i)) for i in range(1, 13)])
    citation_count = IntegerField('Citation Count (Optional - will auto-update quarterly)', validators=[Optional()], default=0)
    bibtex_entry = TextAreaField('BibTeX Entry', validators=[Optional(), validate_bibtex])
    pdf_file = FileField('PDF File (Max 25MB)', 
                        validators=[FileAllowed(['pdf'], 'Only PDF files are allowed!')])
    submit = SubmitField('Submit Publication')

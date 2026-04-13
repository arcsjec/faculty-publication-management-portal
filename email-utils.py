"""
Email utilities for the Faculty Publication Portal
Handles email validation and sending notifications
"""

import smtplib
import socket
import dns.resolver
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app
import threading


def validate_email_exists(email, allow_sjec_dummy=False):
    """
    Validate if an email address actually exists by checking:
    1. Email format
    2. Must be @sjec.ac.in domain
    3. Domain MX records
    
    Args:
        email: Email address to validate
        allow_sjec_dummy: If True, allow dummy @sjec.ac.in emails (for admin user creation)
    
    Returns:
        dict: {'valid': bool, 'message': str, 'is_dummy': bool}
    """
    import re
    
    # Basic format validation
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        return {'valid': False, 'message': 'Invalid email format', 'is_dummy': False}
    
    # Extract domain
    domain = email.split('@')[1]
    
    # STRICT: Must be @sjec.ac.in domain
    if domain != 'sjec.ac.in':
        return {
            'valid': False, 
            'message': 'Only @sjec.ac.in email addresses are allowed',
            'is_dummy': False
        }
    
    # If admin is creating user, allow dummy emails
    if allow_sjec_dummy:
        # Check if it's a known dummy email pattern
        dummy_patterns = ['test@', 'dummy@', 'demo@', 'temp@']
        is_dummy = any(email.startswith(pattern) for pattern in dummy_patterns)
        
        return {
            'valid': True,
            'message': 'SJEC email accepted (dummy email - notifications will be skipped)' if is_dummy else 'SJEC email domain validated',
            'is_dummy': is_dummy
        }
    
    # For faculty registration: validate that sjec.ac.in domain is reachable
    try:
        # Check if domain has MX records
        mx_records = dns.resolver.resolve(domain, 'MX')
        if not mx_records:
            return {'valid': False, 'message': f'No mail server found for domain {domain}', 'is_dummy': False}
        
        # Domain is valid - accept the email
        # Note: We can't verify individual mailboxes for sjec.ac.in (servers block it)
        return {
            'valid': True,
            'message': 'SJEC email address accepted',
            'is_dummy': False
        }
        
    except dns.resolver.NXDOMAIN:
        return {'valid': False, 'message': f'Domain {domain} does not exist', 'is_dummy': False}
    except dns.resolver.NoAnswer:
        return {'valid': False, 'message': f'No MX records found for {domain}', 'is_dummy': False}
    except dns.resolver.Timeout:
        return {'valid': False, 'message': 'DNS lookup timeout - please try again', 'is_dummy': False}
    except Exception as e:
        # If DNS check fails, still allow it (SJEC domain might have temporary issues)
        return {
            'valid': True,
            'message': 'SJEC email accepted (DNS verification skipped)',
            'is_dummy': False
        }


def send_email(to_email, subject, body_html, body_text=None, skip_validation=False):
    """
    Send email to a recipient
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        body_html: HTML body content
        body_text: Plain text body (optional, will extract from HTML if not provided)
        skip_validation: If True, skip email validation (for admin-created users)
    
    Returns:
        dict: {'success': bool, 'message': str, 'skipped': bool}
    """
    
    # Check if it's a dummy email - don't send
    dummy_patterns = ['test@', 'dummy@', 'demo@', 'temp@']
    if any(to_email.startswith(pattern) for pattern in dummy_patterns):
        return {
            'success': True,
            'message': 'Email skipped (dummy address)',
            'skipped': True
        }
    
    # Validate email first (unless skipped)
    if not skip_validation:
        validation = validate_email_exists(to_email, allow_sjec_dummy=False)
        if not validation['valid']:
            return {
                'success': False,
                'message': f'Email validation failed: {validation["message"]}',
                'skipped': False
            }
    
    # Check if email is configured
    if not current_app.config.get('MAIL_USERNAME') or not current_app.config.get('MAIL_PASSWORD'):
        return {
            'success': False,
            'message': 'Email not configured (MAIL_USERNAME/MAIL_PASSWORD not set)',
            'skipped': False
        }
    
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = current_app.config['MAIL_DEFAULT_SENDER']
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Attach plain text version
        if body_text:
            part1 = MIMEText(body_text, 'plain')
            msg.attach(part1)
        
        # Attach HTML version
        part2 = MIMEText(body_html, 'html')
        msg.attach(part2)
        
        # Send email
        with smtplib.SMTP(current_app.config['MAIL_SERVER'], current_app.config['MAIL_PORT']) as server:
            server.starttls()
            server.login(
                current_app.config['MAIL_USERNAME'],
                current_app.config['MAIL_PASSWORD']
            )
            server.send_message(msg)
        
        return {'success': True, 'message': 'Email sent successfully', 'skipped': False}
        
    except Exception as e:
        return {
            'success': False,
            'message': f'Failed to send email: {str(e)}',
            'skipped': False
        }


def send_email_async(app, to_email, subject, body_html, body_text=None, skip_validation=False):
    """
    Send email asynchronously in a background thread
    """
    def send_async():
        with app.app_context():
            send_email(to_email, subject, body_html, body_text, skip_validation)
    
    thread = threading.Thread(target=send_async)
    thread.start()


def send_welcome_email(user, skip_validation=False):
    """
    Send welcome email to newly registered user
    
    Args:
        user: User object
        skip_validation: If True, skip email validation
    
    Returns:
        dict: {'success': bool, 'message': str}
    """
    subject = "Welcome to SJEC Faculty Publication Portal"
    
    body_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Welcome to SJEC Portal</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 20px;
            }}
            .email-wrapper {{
                max-width: 650px;
                margin: 0 auto;
                background: #ffffff;
                border-radius: 20px;
                overflow: hidden;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            }}
            .header {{
                background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                color: white;
                padding: 40px 30px;
                text-align: center;
                position: relative;
            }}
            .header::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 4px;
                background: linear-gradient(90deg, #f6d365 0%, #fda085 100%);
            }}
            .header h1 {{
                font-size: 28px;
                margin: 10px 0;
                font-weight: 700;
            }}
            .header-icon {{
                font-size: 60px;
                margin-bottom: 10px;
            }}
            .content {{
                padding: 40px 30px;
                background: #ffffff;
            }}
            .greeting {{
                font-size: 24px;
                color: #1e3c72;
                margin-bottom: 20px;
                font-weight: 600;
            }}
            .intro-text {{
                font-size: 16px;
                color: #555;
                margin-bottom: 30px;
                line-height: 1.8;
            }}
            .info-card {{
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                border-left: 4px solid #2a5298;
                padding: 20px;
                margin: 25px 0;
                border-radius: 10px;
            }}
            .info-card h3 {{
                color: #1e3c72;
                margin-bottom: 15px;
                font-size: 18px;
            }}
            .info-item {{
                padding: 8px 0;
                border-bottom: 1px solid #ddd;
            }}
            .info-item:last-child {{
                border-bottom: none;
            }}
            .info-label {{
                font-weight: 600;
                color: #2a5298;
                display: inline-block;
                width: 120px;
            }}
            .features-section {{
                margin: 30px 0;
            }}
            .features-title {{
                color: #1e3c72;
                font-size: 20px;
                margin-bottom: 20px;
                font-weight: 600;
            }}
            .feature-grid {{
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 15px;
                margin-bottom: 25px;
            }}
            .feature-item {{
                background: #f8f9fa;
                padding: 15px;
                border-radius: 10px;
                border: 2px solid #e9ecef;
                transition: all 0.3s ease;
            }}
            .feature-icon {{
                font-size: 24px;
                margin-bottom: 8px;
                display: block;
            }}
            .feature-text {{
                color: #555;
                font-size: 14px;
                font-weight: 500;
            }}
            .cta-button {{
                display: inline-block;
                padding: 15px 40px;
                background: linear-gradient(135deg, #f6d365 0%, #fda085 100%);
                color: #1e3c72;
                text-decoration: none;
                border-radius: 50px;
                font-weight: 700;
                font-size: 16px;
                margin: 25px 0;
                text-align: center;
                box-shadow: 0 8px 20px rgba(253, 160, 133, 0.4);
                transition: all 0.3s ease;
            }}
            .help-section {{
                background: #fff3cd;
                border-left: 4px solid #ffc107;
                padding: 15px;
                border-radius: 8px;
                margin: 25px 0;
            }}
            .help-text {{
                color: #856404;
                font-size: 14px;
            }}
            .footer {{
                background: #f8f9fa;
                padding: 30px;
                text-align: center;
                border-top: 3px solid #e9ecef;
            }}
            .footer-text {{
                color: #6c757d;
                font-size: 13px;
                margin: 5px 0;
            }}
            .footer-logo {{
                font-weight: 700;
                color: #1e3c72;
                font-size: 16px;
                margin-bottom: 10px;
            }}
            @media only screen and (max-width: 600px) {{
                .feature-grid {{
                    grid-template-columns: 1fr;
                }}
                .header h1 {{
                    font-size: 22px;
                }}
                .content {{
                    padding: 25px 20px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="email-wrapper">
            <!-- Header -->
            <div class="header">
                <div class="header-icon">🎓</div>
                <h1>Welcome to SJEC Publication Portal!</h1>
                <p style="margin-top: 10px; font-size: 14px; opacity: 0.9;">Your Gateway to Research Excellence</p>
            </div>
            
            <!-- Content -->
            <div class="content">
                <div class="greeting">Hello {user.name}! 👋</div>
                
                <p class="intro-text">
                    We're thrilled to have you on board! Your account has been successfully created, and you're now part of 
                    the <strong>St Joseph Engineering College Faculty Publication Portal</strong> — a comprehensive platform 
                    designed to streamline your research journey.
                </p>
                
                <!-- Account Information Card -->
                <div class="info-card">
                    <h3>📋 Your Account Details</h3>
                    <div class="info-item">
                        <span class="info-label">Name:</span>
                        <span>{user.name}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Email:</span>
                        <span>{user.email}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Department:</span>
                        <span>{user.department.name if user.department else 'Not assigned'}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Role:</span>
                        <span>{user.role.title()}</span>
                    </div>
                </div>
                
                <!-- Features Section -->
                <div class="features-section">
                    <div class="features-title">🚀 What You Can Do Now</div>
                    <div class="feature-grid">
                        <div class="feature-item">
                            <span class="feature-icon">📚</span>
                            <div class="feature-text">Add & Manage Publications</div>
                        </div>
                        <div class="feature-item">
                            <span class="feature-icon">💰</span>
                            <div class="feature-text">Apply for Incentives</div>
                        </div>
                        <div class="feature-item">
                            <span class="feature-icon">📊</span>
                            <div class="feature-text">Track Research Stats</div>
                        </div>
                        <div class="feature-item">
                            <span class="feature-icon">🎯</span>
                            <div class="feature-text">Monitor Fund Wallet</div>
                        </div>
                    </div>
                </div>
                
                <!-- CTA Button -->
                <center>
                    <a href="http://localhost:5000/login" class="cta-button">🔐 Login to Portal</a>
                </center>
                
                <!-- Help Section -->
                <div class="help-section">
                    <div class="help-text">
                        <strong>💡 Need Help?</strong><br>
                        If you have any questions or need assistance getting started, please contact the administrator or refer to the User Guide in the portal.
                    </div>
                </div>
                
                <p style="margin-top: 30px; color: #555; font-size: 15px;">
                    Best regards,<br>
                    <strong style="color: #1e3c72;">SJEC Publication Portal Team</strong>
                </p>
            </div>
            
            <!-- Footer -->
            <div class="footer">
                <div class="footer-logo">St Joseph Engineering College, Mangaluru</div>
                <p class="footer-text">This is an automated message from SJEC Faculty Publication Portal</p>
                <p class="footer-text">&copy; 2025 SJEC. All Rights Reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    body_text = f"""
    Welcome to SJEC Faculty Publication Portal!
    
    Hello {user.name},
    
    Your account has been successfully created.
    
    Username: {user.name}
    Email: {user.email}
    Department: {user.department.name if user.department else 'Not assigned'}
    Role: {user.role.title()}
    
    Login at: http://localhost:5000/login
    
    Best regards,
    SJEC Publication Portal Team
    """
    
    return send_email(user.email, subject, body_html, body_text, skip_validation)


def send_notification_email(user, notification_title, notification_message, skip_validation=False):
    """
    Send notification email to user
    
    Args:
        user: User object
        notification_title: Notification title
        notification_message: Notification message
        skip_validation: If True, skip email validation
    
    Returns:
        dict: {'success': bool, 'message': str}
    """
    subject = f"SJEC Portal: {notification_title}"
    
    body_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f9f9f9;
            }}
            .header {{
                background-color: #0d47a1;
                color: white;
                padding: 15px;
                text-align: center;
            }}
            .content {{
                background-color: white;
                padding: 25px;
                margin-top: 20px;
            }}
            .notification-box {{
                background-color: #e3f2fd;
                border-left: 4px solid #2196f3;
                padding: 15px;
                margin: 15px 0;
            }}
            .footer {{
                text-align: center;
                margin-top: 20px;
                font-size: 12px;
                color: #666;
            }}
            .button {{
                display: inline-block;
                padding: 10px 20px;
                background-color: #0d47a1;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                margin-top: 15px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>📬 SJEC Publication Portal</h2>
            </div>
            <div class="content">
                <h3>Hello {user.name},</h3>
                
                <div class="notification-box">
                    <h4>{notification_title}</h4>
                    <p>{notification_message}</p>
                </div>
                
                <p>
                    <a href="http://localhost:5000/notifications" class="button">View All Notifications</a>
                </p>
                
                <p style="margin-top: 20px;">
                    <small>This notification was sent to you as part of your activities on the SJEC Faculty Publication Portal.</small>
                </p>
            </div>
            <div class="footer">
                <p>This is an automated notification from SJEC Faculty Publication Portal</p>
                <p>&copy; 2025 St Joseph Engineering College</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    body_text = f"""
    SJEC Faculty Publication Portal
    
    Hello {user.name},
    
    {notification_title}
    
    {notification_message}
    
    View all notifications: http://localhost:5000/notifications
    
    This is an automated notification.
    """
    
    return send_email(user.email, subject, body_html, body_text, skip_validation)

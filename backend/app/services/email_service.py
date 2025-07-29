import os
import logging
from typing import Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

# Email configuration from environment variables
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@specsharp.com")
APP_URL = os.getenv("APP_URL", "http://localhost:5173")


async def send_team_invitation_email(
    recipient_email: str,
    team_name: str,
    inviter_name: str,
    invitation_token: str
) -> bool:
    """Send team invitation email"""
    try:
        subject = f"{inviter_name} invited you to join {team_name} on SpecSharp"
        
        # Create invitation URL
        invitation_url = f"{APP_URL}/accept-invitation/{invitation_token}"
        
        # HTML email body
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #667eea;">You're invited to join {team_name}!</h2>
                    
                    <p>Hi there,</p>
                    
                    <p>{inviter_name} has invited you to join their team on SpecSharp, 
                    the professional construction cost estimation platform.</p>
                    
                    <p>As a team member, you'll be able to:</p>
                    <ul>
                        <li>Create unlimited construction estimates</li>
                        <li>Access all team projects and estimates</li>
                        <li>Collaborate with your team in real-time</li>
                        <li>Export professional PDFs and Excel reports</li>
                    </ul>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{invitation_url}" 
                           style="background-color: #667eea; color: white; padding: 12px 30px; 
                                  text-decoration: none; border-radius: 5px; display: inline-block;">
                            Accept Invitation
                        </a>
                    </div>
                    
                    <p style="color: #666; font-size: 14px;">
                        This invitation will expire in 7 days. If you have any questions, 
                        please contact {inviter_name} or reply to this email.
                    </p>
                    
                    <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                    
                    <p style="color: #999; font-size: 12px;">
                        If you didn't expect this invitation, you can safely ignore this email.
                    </p>
                </div>
            </body>
        </html>
        """
        
        # Plain text version
        text_body = f"""
You're invited to join {team_name}!

Hi there,

{inviter_name} has invited you to join their team on SpecSharp, 
the professional construction cost estimation platform.

As a team member, you'll be able to:
- Create unlimited construction estimates
- Access all team projects and estimates
- Collaborate with your team in real-time
- Export professional PDFs and Excel reports

Accept the invitation here: {invitation_url}

This invitation will expire in 7 days. If you have any questions, 
please contact {inviter_name} or reply to this email.

If you didn't expect this invitation, you can safely ignore this email.
        """
        
        # For development, just log the email
        if not SMTP_USERNAME or not SMTP_PASSWORD:
            logger.info(f"[EMAIL] Would send to: {recipient_email}")
            logger.info(f"[EMAIL] Invitation URL: {invitation_url}")
            return True
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = FROM_EMAIL
        msg['To'] = recipient_email
        
        # Attach parts
        msg.attach(MIMEText(text_body, 'plain'))
        msg.attach(MIMEText(html_body, 'html'))
        
        # Send email
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"Successfully sent invitation email to {recipient_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send invitation email: {str(e)}")
        return False
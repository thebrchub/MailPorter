# app/email/sender.py
from email.utils import formataddr
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader
from app.config import SMTPConfig

# Configure logging.
logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s - %(levelname)s - %(message)s")

class AbstractEmailSender:
    def send_email(self, recipient: str, subject: str, context: dict):
        raise NotImplementedError("Subclasses must implement send_email method.")

class SMTPSender(AbstractEmailSender):
    def __init__(self, config: SMTPConfig):
        self.config = config
        # Set up Jinja2 to load templates from the "app/email" directory
        self.template_env = Environment(loader=FileSystemLoader(searchpath="./app/email"))
        self.template = self.template_env.get_template(config.template)

    def send_email(self, recipient: str, subject: str, context: dict):
        html_content = self.template.render(**context)
        message = MIMEMultipart("alternative")
        message["Subject"] = subject

        # Decide From address + display name
        if self.config.host == "smtp.hostinger.com" and self.config.template == "legalvala_template.html":
            # Existing Hostinger + legalvala special case
            from_email = "info@legalvala.com"
            from_name = "Legalvala"
        elif self.config.host == "smtp.gmail.com" and self.config.template in {"brchub_v2.html", "brchub_template.html"}:
            # NEW: Gmail + brchub should send as info@thebrchub.tech
            from_email = "info@thebrchub.tech"
            from_name = "BRC Hub LLP"
        elif self.config.host == "smtp.gmail.com" and self.config.template == "powerbird_template.html":
            # Gmail + powerbird should send as alias info@thebrchub.tech
            from_email = "info@thebrchub.tech"
            from_name = "PowerBird Elevators"
        elif self.config.host == "smtp.gmail.com" and self.config.template == "zquab_template.html":
            # Gmail + zquab should send as info@zquab.com
            from_email = "info@zquab.com"
            from_name = "zQuab"
        elif self.config.host == "smtp.gmail.com" and self.config.template == "irb_technology_template.html":
            from_email = self.config.username
            from_name = "IRB Technology Pvt Ltd"
        else:
            # Default: use SMTP username
            from_email = self.config.username
            from_name = ""

        message["From"] = formataddr((from_name, from_email))
        message["To"] = recipient

        bcc = self.config.bcc_list if self.config.bcc_list else []
        all_recipients = [recipient] + bcc

        message.attach(MIMEText(html_content, "html"))  # Use "plain" or "html" as needed

        try:
            logging.debug("Connecting to SMTP server %s:%s", self.config.host, self.config.port)
            server = smtplib.SMTP(self.config.host, self.config.port)
            server.set_debuglevel(1)  # SMTP internal debug output

            logging.debug("Starting TLS...")
            if self.config.starttls:
                server.starttls()

            logging.debug("Logging in as: %s", self.config.username)
            if self.config.auth:
                server.login(self.config.username, self.config.password)

            logging.debug(
                "Sending email FROM: %s (envelope) TO: %s; BCC: %s",
                from_email,
                recipient,
                self.config.bcc_list,
            )
            # Use from_email as the envelope sender as well
            server.sendmail(from_email, all_recipients, message.as_string())
            server.quit()

            logging.info("Email sent successfully to %s", recipient)
            return {"status": "success", "message": "Email sent successfully."}
        except Exception as e:
            logging.error("Error sending email: %s", str(e))
            return {"status": "error", "message": str(e)}

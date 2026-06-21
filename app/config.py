# app/config.py
import os
from pydantic_settings import BaseSettings
from pydantic import EmailStr
from typing import Dict, List
from dotenv import load_dotenv
load_dotenv()  # This will populate os.environ from your .env file


class SMTPConfig(BaseSettings):
    host: str
    port: int = 587
    username: str
    password: str
    auth: bool = True
    starttls: bool = True
    bcc_list: List[EmailStr] = []       # Unique BCC list for the configuration
    template: str                       # Template file name for the email

class Settings(BaseSettings):
    api_key: str
    # Each provider maps to a dict whose keys are brand names (or "default")
    smtp_servers: Dict[str, Dict[str, SMTPConfig]]
    cors_allowed_origins: List[str]
    server_port: int

    class Config:
        env_file = ".env"
        extra = "allow"  # Allow extra keys not explicitly defined

# Hostinger configuration: two brands (legalvala and brchub)
hostinger_configs = {
    "legalvala": SMTPConfig(
        host="smtp.hostinger.com",
        port=587,
        username=os.getenv("HOSTINGER_LEGALVALA_USERNAME", "default_legalvala"),
        password=os.getenv("HOSTINGER_LEGALVALA_PASSWORD", "default_password"),
        bcc_list=["thebrcexplorers@gmail.com","info@legalvala.com"],
        template="legalvala_template.html"
    ),
    "startfinity": SMTPConfig(
        host="smtp.hostinger.com",
        port=587,
        username=os.getenv("HOSTINGER_STARTFINITY_USERNAME", "default_startfinity"),
        password=os.getenv("HOSTINGER_STARTFINITY_PASSWORD", "default_password"),
        bcc_list=["thebrcexplorers@gmail.com"],
        template="startfinity_template.html"
    )
}

# Gmail configuration (single account, using key "default")
gmail_configs = {
    "default": SMTPConfig(
        host="smtp.gmail.com",
        port=587,
        username=os.getenv("GMAIL_USERNAME", "default_gmail"),
        password=os.getenv("GMAIL_PASSWORD", "default_password"),
        bcc_list=["bcc1@gmail.com"],
        template="gmail_template.html"
    ),
    "brchub": SMTPConfig(
        host="smtp.gmail.com",
        port=587,
        username=os.getenv("GMAIL_BRCHUB_USERNAME", "default_gmail"),
        password=os.getenv("GMAIL_BRCHUB_PASSWORD", "default_password"),
        bcc_list=["info@thebrchub.tech"],
        template="brchub_v2.html"
    ),
    "powerbird": SMTPConfig(
        host="smtp.gmail.com",
        port=587,
        username=os.getenv("GMAIL_BRCHUB_USERNAME", "default_gmail"),
        password=os.getenv("GMAIL_BRCHUB_PASSWORD", "default_password"),
        bcc_list=[],
        template="powerbird_template.html"
    ),
    "digivaala": SMTPConfig(
        host="smtp.gmail.com",
        port=587,
        username=os.getenv("GMAIL_DIGIVAALA_USERNAME", "default_gmail"),
        password=os.getenv("GMAIL_DIGIVAALA_PASSWORD", "default_password"),
        bcc_list=["thebrcexplorers@gmail.com","digivaala@gmail.com"],
        template="digivaala_template.html"
    ),
    "zquab": SMTPConfig(
        host="smtp.gmail.com",
        port=587,
        username=os.getenv("GMAIL_ZQUAB_USERNAME", "default_gmail"),
        password=os.getenv("GMAIL_ZQUAB_PASSWORD", "default_password"),
        bcc_list=["info@zquab.com"],
        template="zquab_template.html"
    ),
    "irb_technology": SMTPConfig(
        host="smtp.gmail.com",
        port=587,
        username=os.getenv("GMAIL_IRB_TECHNOLOGY_USERNAME", "default_gmail"),
        password=os.getenv("GMAIL_IRB_TECHNOLOGY_PASSWORD", "default_password"),
        bcc_list=["irbtechnology25@gmail.com"],
        template="irb_technology_template.html"
    )
}

privateemail_configs = {
    "default": SMTPConfig(
        host="smtp.privateemail.com",
        port=587,
        username=os.getenv("PRIVATEEMAIL_USERNAME", "default_privateemail"),
        password=os.getenv("PRIVATEEMAIL_PASSWORD", "default_password"),
        bcc_list=["bcc1@privateemail.com"],    # adjust as needed
        template="privateemail_template.html"   # your Jinja template
    ),
    "brchub": SMTPConfig(
        host="smtp.privateemail.com",
        port=587,
        username=os.getenv("PRIVATEEMAIL_BRCHUB_USERNAME", "default_privateemail"),
        password=os.getenv("PRIVATEEMAIL_BRCHUB_PASSWORD", "default_password"),
        bcc_list=["thebrcexplorers@gmail.com"],
        template="brchub_v2.html"         # your Jinja template
    )
}

# New Provider configuration (example)
newprovider_configs = {
    "default": SMTPConfig(
        host="smtp.newprovider.com",
        port=587,
        username=os.getenv("NEWPROVIDER_USERNAME", "default_newprovider"),
        password=os.getenv("NEWPROVIDER_PASSWORD", "default_password"),
        bcc_list=["bcc1@newprovider.com"],
        template="newprovider_template.html"
    )
}

settings = Settings(
    api_key=os.getenv("API_KEY", "default_api_key"),
    smtp_servers={
        "hostinger": hostinger_configs,
        "gmail": gmail_configs,
        "privateemail": privateemail_configs,
        "newprovider": newprovider_configs
    },
    cors_allowed_origins=[
        "https://digivala.in",
        "https://www.brchub.me",
        "https://legalvala.com",
        "legalvala.com",
        "startfinity.com",
        "https://startfinity.com",
        "mailporter.vercel.app",
        "https://brchub.vercel.app",
        "http://localhost:3000",
        "https://thrbrchub.tech",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "https://www.thebrchub.tech",
        "www.thebrchub.tech/:1",
        "https://powerbird-elevators.brchub.me",
        "https://irbtechnology.com",
        "https://www.irbtechnology.com"
    ],
    server_port=8000  # Updated port number
)

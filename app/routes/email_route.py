# app/routes/email_route.py
from typing import List, Optional, Union
from fastapi import APIRouter, HTTPException, Depends, Header, Body
from pydantic import BaseModel, EmailStr, constr
from app.config import settings
from app.email.sender import SMTPSender

router = APIRouter()

class EmailPayload(BaseModel):
    name: constr(min_length=1, max_length=50)
    email: EmailStr
    message: constr(min_length=1, max_length=5000)
    mobile: Optional[constr(min_length=10, max_length=15)] = None
    brand: constr(min_length=1)  # e.g., "legalvala" or "brchub"
    services: Optional[Union[List[constr(min_length=1, max_length=100)], constr(min_length=1, max_length=500)]] = None

    def services_text(self) -> Optional[str]:
        if self.services is None:
            return None
        if isinstance(self.services, list):
            return ", ".join(service.strip() for service in self.services if service.strip()) or None
        value = self.services.strip()
        return value or None

    class Config:
        extra = "allow"  # allow additional fields for dynamic templates

def get_api_key(x_api_key: str = Header(...)):
    if x_api_key != settings.api_key:
        raise HTTPException(status_code=403, detail="Could not validate API key")
    return x_api_key

@router.post("/send-email/{smtp_provider}")
async def send_email(
    smtp_provider: str,
    payload: EmailPayload = Body(...),
    api_key: str = Depends(get_api_key)
):
    provider_configs = settings.smtp_servers.get(smtp_provider)
    if not provider_configs:
        raise HTTPException(
            status_code=400,
            detail=f"SMTP configuration for provider '{smtp_provider}' not found."
        )
    smtp_config = provider_configs.get(payload.brand.lower())
    if not smtp_config:
        smtp_config = provider_configs.get("default")
        if not smtp_config:
            raise HTTPException(
                status_code=400,
                detail=f"No SMTP configuration found for brand '{payload.brand}' under provider '{smtp_provider}'."
            )

    sender = SMTPSender(smtp_config)
    payload_dict = payload.dict()
    extra_fields = {
        key: value
        for key, value in payload_dict.items()
        if key not in {"name", "email", "message", "mobile", "brand", "services"}
    }
    reserved_field_names = {
        "full_name",
        "phone_number",
        "email_address",
        "requirement_type",
        "building_type",
        "message_remarks",
        "contact_name",
        "city_location",
        "no_of_lifts",
        "lifts_count",
        "current_status"
    }
    extra_fields_filtered = {
        key: value
        for key, value in extra_fields.items()
        if key not in reserved_field_names
    }
    user_email = (payload_dict.get("user_email") or payload.email or "").strip() or None
    lead_email = user_email or payload.email
    company = extra_fields.get("company") or extra_fields.get("company_name") or "Not provided"
    service = extra_fields.get("service") or payload.services_text() or "Not specified"
    context = {
        "name": payload.name,
        "message": payload.message,
        "mobile": payload.mobile,
        "email": payload.email,
        "user_email": user_email,
        "lead_email": lead_email,
        "company": company,
        "service": service,
        "services": payload.services_text(),
        "fields": extra_fields,
        "fields_extra": extra_fields_filtered,
        "payload": payload_dict
    }
    default_subject = "Thank you for contacting our business"
    # powerbird_template
    if payload.brand.lower() == "powerbird" or smtp_config.template == "powerbird_template.html":
        default_subject = "New Inquiry from PowerBird Elevators Website"
    elif payload.brand.lower() == "zquab" or smtp_config.template == "zquab_template.html":
        default_subject = "Welcome to zQuab - We are opening soon"
    elif payload.brand.lower() == "irb_technology" or smtp_config.template == "irb_technology_template.html":
        default_subject = "New Lead - IRB Technology"
    subject = (payload_dict.get("subject") or "").strip() or default_subject
    result = sender.send_email(recipient=payload.email, subject=subject, context=context)
    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("message"))
    return result

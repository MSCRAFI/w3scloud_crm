import json
import os
import requests
from datetime import timedelta
from django.shortcuts import redirect
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from .models import ZohoToken


def zoho_login(request):
    params = {
        "scope": "ZohoCRM.modules.leads.ALL,ZohoCRM.modules.contacts.READ",
        "client_id": os.environ["ZOHO_CLIENT_ID"],
        "response_type": "code",
        "access_type": "offline",
        "redirect_uri": os.environ["ZOHO_REDIRECT_URI"],
        "prompt": "consent",
    }
    url = "https://accounts.zoho.com/oauth/v2/auth?" + "&".join(f"{k}={v}" for k, v in params.items())
    return redirect(url)


def zoho_callback(request):
    code = request.GET.get("code")
    resp = requests.post("https://accounts.zoho.com/oauth/v2/token", data={
        "grant_type": "authorization_code",
        "client_id": os.environ["ZOHO_CLIENT_ID"],
        "client_secret": os.environ["ZOHO_CLIENT_SECRET"],
        "redirect_uri": os.environ["ZOHO_REDIRECT_URI"],
        "code": code,
    })
    data = resp.json()
    if "access_token" not in data:
        return JsonResponse({"error": "OAuth exchange failed", "detail": data}, status=400)

    ZohoToken.objects.update_or_create(
        user_identifier="default",
        defaults={
            "access_token": data["access_token"],
            "refresh_token": data["refresh_token"],
            "expires_at": timezone.now() + timedelta(seconds=data["expires_in"]),
        }
    )
    return redirect("zoho_leads")


def get_valid_access_token():
    token = ZohoToken.objects.get(user_identifier="default")
    if timezone.now() >= token.expires_at:
        resp = requests.post("https://accounts.zoho.com/oauth/v2/token", data={
            "grant_type": "refresh_token",
            "client_id": os.environ["ZOHO_CLIENT_ID"],
            "client_secret": os.environ["ZOHO_CLIENT_SECRET"],
            "refresh_token": token.refresh_token,
        })
        data = resp.json()
        token.access_token = data["access_token"]
        token.expires_at = timezone.now() + timedelta(seconds=data["expires_in"])
        token.save()
    return token.access_token


def handle_zoho_error(resp):
    try:
        body = resp.json()
    except ValueError:
        body = {}
    code = body.get("code") or (body.get("data", [{}])[0].get("code") if isinstance(body.get("data"), list) and len(body.get("data")) > 0 else "")
    if resp.status_code == 401:
        return JsonResponse({"error": "Token invalid/expired", "detail": body}, status=401)
    if code == "MANDATORY_NOT_FOUND":
        return JsonResponse({"error": "Missing required field", "detail": body}, status=400)
    if code == "INVALID_MODULE":
        return JsonResponse({"error": "Invalid module name", "detail": body}, status=400)
    return JsonResponse({"error": "Zoho API error", "detail": body}, status=resp.status_code)


def list_leads(request):
    token = get_valid_access_token()
    resp = requests.get(
        "https://www.zohoapis.com/crm/v3/Leads",
        headers={"Authorization": f"Zoho-oauthtoken {token}"},
        params={"fields": "id,Last_Name,Email,Phone"}
    )
    if resp.status_code != 200:
        return handle_zoho_error(resp)
    return JsonResponse({"leads": resp.json().get("data", [])})


@csrf_exempt
def create_lead(request):
    token = get_valid_access_token()
    lead_data = {
        "First_Name": "Salman",
        "Last_Name": "Chowdhury",
        "Company": "ABC Ltd",
        "Email": "john@example.com",
        "Phone": "+8801XXXXXXXXX"
    }

    if request.body:
        try:
            body = json.loads(request.body)
            if isinstance(body, dict):
                if "data" in body and isinstance(body["data"], list) and len(body["data"]) > 0:
                    lead_data.update(body["data"][0])
                else:
                    lead_data.update(body)
        except Exception:
            pass

    payload = {"data": [lead_data]}
    resp = requests.post(
        "https://www.zohoapis.com/crm/v3/Leads",
        headers={"Authorization": f"Zoho-oauthtoken {token}", "Content-Type": "application/json"},
        json=payload
    )
    if resp.status_code not in (200, 201):
        return handle_zoho_error(resp)
    record_id = resp.json()["data"][0]["details"]["id"]
    return JsonResponse({"created_id": record_id})


def get_lead(request, record_id):
    token = get_valid_access_token()
    resp = requests.get(
        f"https://www.zohoapis.com/crm/v3/Leads/{record_id}",
        headers={"Authorization": f"Zoho-oauthtoken {token}"},
        params={"fields": "id,First_Name,Last_Name,Company,Email,Phone,Created_Time"}
    )
    if resp.status_code != 200:
        return handle_zoho_error(resp)
    return JsonResponse(resp.json())
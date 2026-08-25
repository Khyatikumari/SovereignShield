import re


# --------------------------------------------------
# SCAM KEYWORDS
# --------------------------------------------------

SCAM_PATTERNS = {

    "urgency": [
        "immediately",
        "urgent",
        "urgent action",
        "act now",
        "within 24 hours",
        "today",
        "expires today",
        "last chance",
        "account will be blocked",
        "account will be closed"
    ],

    "financial": [
        "send money",
        "transfer money",
        "payment",
        "pay now",
        "upi",
        "upi payment",
        "refund",
        "cashback",
        "prize money",
        "lottery",
        "winner",
        "reward"
    ],

    "credential_request": [
        "password",
        "otp",
        "pin",
        "upi pin",
        "cvv",
        "card number",
        "bank details",
        "login",
        "verify your account",
        "verify account"
    ],

    "kyc": [
        "kyc",
        "kyc update",
        "kyc verification",
        "aadhaar",
        "pan card",
        "pan",
        "identity verification"
    ],

    "impersonation": [
        "sbi",
        "hdfc",
        "icici",
        "axis bank",
        "paytm",
        "phonepe",
        "google pay",
        "amazon",
        "flipkart",
        "income tax",
        "epfo",
        "uidai",
        "government"
    ],

    "job_scam": [
        "work from home",
        "part time job",
        "earn money",
        "daily income",
        "registration fee",
        "job offer",
        "selected for job",
        "pay registration"
    ],

    "threat": [
        "legal action",
        "police complaint",
        "arrest",
        "penalty",
        "fine",
        "account blocked",
        "account suspended"
    ]
}


# --------------------------------------------------
# KEYWORD MATCHING
# Prevent accidental substring matches
# --------------------------------------------------

def find_keywords(text: str, keywords: list):

    found = []

    for keyword in keywords:

        pattern = r"\b" + re.escape(keyword) + r"\b"

        if re.search(pattern, text, re.IGNORECASE):
            found.append(keyword)

    return found


# --------------------------------------------------
# MESSAGE ANALYZER
# --------------------------------------------------

def analyze_message(message: str):

    text = message.lower()

    score = 0
    indicators = []
    categories = set()

    # --------------------------------------------------
    # CHECK PATTERNS
    # --------------------------------------------------

    detected = {}

    for category, keywords in SCAM_PATTERNS.items():

        found = find_keywords(text, keywords)

        if found:
            detected[category] = found

    # --------------------------------------------------
    # DETERMINE SUSPICIOUS CONTEXT
    # --------------------------------------------------

    suspicious_categories = {
        "urgency",
        "financial",
        "credential_request",
        "kyc",
        "job_scam",
        "threat"
    }

    has_suspicious_context = any(
        category in detected
        for category in suspicious_categories
    )

    # --------------------------------------------------
    # SCORE NORMAL SCAM CATEGORIES
    # --------------------------------------------------

    for category, found in detected.items():

        # ----------------------------------------------
        # BRAND IMPERSONATION
        # Only count a brand as suspicious when there
        # is another scam signal around it.
        # ----------------------------------------------

        if category == "impersonation":

            if not has_suspicious_context:
                continue

            points = min(len(found) * 8, 20)

        elif category == "credential_request":

            points = min(len(found) * 10, 30)

        elif category == "threat":

            points = min(len(found) * 8, 20)

        elif category == "financial":

            points = min(len(found) * 7, 20)

        elif category == "kyc":

            points = min(len(found) * 7, 20)

        elif category == "job_scam":

            points = min(len(found) * 7, 20)

        else:

            points = min(len(found) * 5, 15)

        # Add category only after it passes the
        # contextual validation above.

        categories.add(category)

        score += points

        indicators.append({
            "category": category,
            "keywords_found": found,
            "points": points
        })

    # --------------------------------------------------
    # URL DETECTION
    # --------------------------------------------------

    urls = re.findall(
        r'https?://[^\s]+|www\.[^\s]+',
        message
    )

    if urls:

        score += 10

        indicators.append({
            "category": "url_present",
            "keywords_found": urls,
            "points": 10
        })

    # --------------------------------------------------
    # FINAL SCORE
    # --------------------------------------------------

    score = min(score, 100)

    if score >= 70:
        risk_level = "CRITICAL"

    elif score >= 40:
        risk_level = "HIGH"

    elif score >= 20:
        risk_level = "MEDIUM"

    else:
        risk_level = "LOW"

    # --------------------------------------------------
    # DETERMINE THREAT TYPE
    # --------------------------------------------------

    threat_type = "No Significant Threat"

    if "credential_request" in categories:

        threat_type = "Credential Phishing"

    elif "kyc" in categories:

        threat_type = "KYC Scam"

    elif "job_scam" in categories:

        threat_type = "Job Scam"

    elif "financial" in categories:

        threat_type = "Financial Fraud"

    elif "impersonation" in categories:

        threat_type = "Brand Impersonation"

    elif "threat" in categories:

        threat_type = "Threat-Based Scam"

    return {
        "risk_score": score,
        "risk_level": risk_level,
        "threat_type": threat_type,
        "categories": list(categories),
        "indicators": indicators,
        "urls_found": urls
    }
import re
import ipaddress
from urllib.parse import urlparse
import tldextract


# Common URL shorteners
SHORTENERS = {
    "bit.ly",
    "tinyurl.com",
    "t.co",
    "goo.gl",
    "is.gd",
    "cutt.ly",
    "rb.gy",
    "shorturl.at"
}


# Suspicious high-risk TLDs
SUSPICIOUS_TLDS = {
    "xyz",
    "top",
    "click",
    "loan",
    "work",
    "gq",
    "tk",
    "ml",
    "cf"
}


# Indian brands commonly impersonated in scams
INDIAN_BRANDS = {
    "sbi",
    "hdfc",
    "icici",
    "axis",
    "paytm",
    "phonepe",
    "googlepay",
    "amazon",
    "flipkart",
    "uidai",
    "incometax",
    "epfindia",
    "irctc"
}


def analyze_url(url: str):

    # Add scheme if missing
    if not url.startswith(("http://", "https://")):
        url = "http://" + url

    parsed = urlparse(url)
    hostname = parsed.hostname or ""

    score = 0
    indicators = []

    # --------------------------------------------------
    # 1. HTTPS CHECK
    # --------------------------------------------------

    if parsed.scheme != "https":
        score += 10

        indicators.append({
            "name": "No HTTPS",
            "severity": "medium",
            "points": 10,
            "description": "The URL does not use HTTPS encryption."
        })

    # --------------------------------------------------
    # 2. IP ADDRESS CHECK
    # --------------------------------------------------

    try:
        ipaddress.ip_address(hostname)

        score += 25

        indicators.append({
            "name": "IP-based URL",
            "severity": "high",
            "points": 25,
            "description": "The link uses an IP address instead of a normal domain."
        })

    except ValueError:
        pass

    # --------------------------------------------------
    # 3. @ SYMBOL
    # --------------------------------------------------

    if "@" in url:

        score += 20

        indicators.append({
            "name": "URL @ redirect trick",
            "severity": "high",
            "points": 20,
            "description": "The URL contains @ which can hide the actual destination."
        })

    # --------------------------------------------------
    # 4. URL LENGTH
    # --------------------------------------------------

    if len(url) > 100:

        score += 10

        indicators.append({
            "name": "Very long URL",
            "severity": "medium",
            "points": 10,
            "description": "The URL is unusually long and may contain obfuscation."
        })

    # --------------------------------------------------
    # 5. SUBDOMAIN DEPTH
    # --------------------------------------------------

    subdomain_parts = parsed.hostname.split(".") if parsed.hostname else []

    if len(subdomain_parts) >= 5:

        score += 10

        indicators.append({
            "name": "Excessive subdomains",
            "severity": "medium",
            "points": 10,
            "description": "The domain contains an unusually large number of subdomains."
        })

    # --------------------------------------------------
    # 6. SHORTENER CHECK
    # --------------------------------------------------

    domain = hostname.lower()

    if domain in SHORTENERS:

        score += 20

        indicators.append({
            "name": "URL shortener",
            "severity": "high",
            "points": 20,
            "description": "The URL uses a shortening service that hides the destination."
        })

    # --------------------------------------------------
    # 7. SUSPICIOUS TLD
    # --------------------------------------------------

    extracted = tldextract.extract(hostname)

    suffix = extracted.suffix.lower()

    if suffix in SUSPICIOUS_TLDS:

        score += 15

        indicators.append({
            "name": "Suspicious domain extension",
            "severity": "medium",
            "points": 15,
            "description": f"The domain uses the suspicious .{suffix} extension."
        })

    # --------------------------------------------------
    # 8. BRAND IMPERSONATION
    # --------------------------------------------------

    domain_text = hostname.lower()

    for brand in INDIAN_BRANDS:

        if brand in domain_text:

            legitimate_domains = [
                f"{brand}.com",
                f"{brand}.in",
                f"{brand}.co.in"
            ]

            if not any(
                domain_text == legitimate or
                domain_text.endswith("." + legitimate)
                for legitimate in legitimate_domains
            ):

                score += 25

                indicators.append({
                    "name": "Possible brand impersonation",
                    "severity": "high",
                    "points": 25,
                    "description": f"The domain contains '{brand}', which may indicate brand impersonation."
                })

            break

    # --------------------------------------------------
    # 9. SUSPICIOUS KEYWORDS
    # --------------------------------------------------

    suspicious_words = [
        "login",
        "verify",
        "verification",
        "secure",
        "update",
        "kyc",
        "account",
        "password",
        "otp",
        "payment",
        "wallet",
        "bank"
    ]

    found_words = []

    for word in suspicious_words:

        if word in url.lower():
            found_words.append(word)

    if found_words:

        score += min(len(found_words) * 5, 20)

        indicators.append({
            "name": "Suspicious URL keywords",
            "severity": "medium",
            "points": min(len(found_words) * 5, 20),
            "description": "The URL contains security or payment-related keywords.",
            "keywords": found_words
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

    return {
        "url": url,
        "domain": hostname,
        "risk_score": score,
        "risk_level": risk_level,
        "is_suspicious": score >= 40,
        "indicators": indicators
    }
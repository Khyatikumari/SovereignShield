import re

from services.message_detector import analyze_message
from services.url_detector import analyze_url


def extract_urls(message: str):

    urls = re.findall(
        r'https?://[^\s]+|www\.[^\s]+',
        message
    )

    return urls


def calculate_final_score(message_score, url_scores):

    # Message analysis has 45% weight
    message_component = message_score * 0.45

    # URL analysis has 55% weight
    if url_scores:
        highest_url_score = max(url_scores)
        url_component = highest_url_score * 0.55
    else:
        url_component = 0

    final_score = message_component + url_component

    return round(min(final_score, 100))


def determine_risk_level(score):

    if score >= 80:
        return "CRITICAL"

    elif score >= 60:
        return "HIGH"

    elif score >= 35:
        return "MEDIUM"

    elif score >= 15:
        return "LOW"

    return "SAFE"


def generate_recommendations(
    final_score,
    message_analysis,
    url_analyses
):

    recommendations = []

    if final_score >= 60:

        recommendations.append(
            "Do not click the link."
        )

        recommendations.append(
            "Do not share OTP, PIN, CVV or passwords."
        )

        recommendations.append(
            "Do not make any payment requested by this message."
        )

        recommendations.append(
            "Verify the communication through the organization's official website or app."
        )

    elif final_score >= 35:

        recommendations.append(
            "Treat this message with caution."
        )

        recommendations.append(
            "Verify the sender before taking any action."
        )

    else:

        recommendations.append(
            "No major threat indicators were detected."
        )

    # Specific recommendations

    if "credential_request" in message_analysis["categories"]:

        recommendations.append(
            "Never share OTP, UPI PIN, CVV or banking passwords through messages."
        )

    if "kyc" in message_analysis["categories"]:

        recommendations.append(
            "Complete KYC only through the official bank or government portal."
        )

    if "impersonation" in message_analysis["categories"]:

        recommendations.append(
            "Do not trust links simply because they contain a familiar brand name."
        )

    return list(dict.fromkeys(recommendations))


def scan_threat(message: str):

    # ---------------------------------------------
    # STEP 1: ANALYZE MESSAGE
    # ---------------------------------------------

    message_analysis = analyze_message(message)

    # ---------------------------------------------
    # STEP 2: EXTRACT URLs
    # ---------------------------------------------

    urls = extract_urls(message)

    # ---------------------------------------------
    # STEP 3: ANALYZE EVERY URL
    # ---------------------------------------------

    url_analyses = []

    for url in urls:

        analysis = analyze_url(url)

        url_analyses.append(analysis)

    # ---------------------------------------------
    # STEP 4: CALCULATE FINAL SCORE
    # ---------------------------------------------

    url_scores = [
        analysis["risk_score"]
        for analysis in url_analyses
    ]

    final_score = calculate_final_score(
        message_analysis["risk_score"],
        url_scores
    )

    # ---------------------------------------------
    # STEP 5: FINAL RISK LEVEL
    # ---------------------------------------------

    risk_level = determine_risk_level(final_score)

    # ---------------------------------------------
    # STEP 6: GENERATE RECOMMENDATIONS
    # ---------------------------------------------

    recommendations = generate_recommendations(
        final_score,
        message_analysis,
        url_analyses
    )

    # ---------------------------------------------
    # STEP 7: THREAT SUMMARY
    # ---------------------------------------------

    threat_types = []

    if message_analysis["threat_type"] != "No Significant Threat":

        threat_types.append(
            message_analysis["threat_type"]
        )

    for analysis in url_analyses:

        for indicator in analysis["indicators"]:

            name = indicator["name"]

            if name not in threat_types:
                threat_types.append(name)

    # ---------------------------------------------
    # FINAL RESULT
    # ---------------------------------------------

    return {

        "final_risk_score": final_score,

        "risk_level": risk_level,

        "threat_type": message_analysis["threat_type"],

        "threat_summary": threat_types,

        "message_analysis": message_analysis,

        "url_analysis": url_analyses,

        "recommendations": recommendations,

        "analysis_engine": {
            "message_detection": "Rule-based behavioral analysis",
            "url_detection": "Rule-based URL feature analysis",
            "fusion": "Weighted risk aggregation"
        }
    }
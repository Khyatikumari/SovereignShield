const API_URL = "/scan";


const examples = {

    sbi:
        "Your SBI account will be blocked today. Complete KYC verification immediately to avoid account suspension. Verify your account using the link below and enter your OTP and UPI PIN: http://sbi-kyc-verify.xyz/login",

    upi:
        "Congratulations! You have received a cashback of Rs 5,000. Click here to claim your UPI reward immediately: http://paytm-reward.xyz/claim",

    job:
        "Congratulations! You have been selected for a work from home job. Earn Rs 5,000 per day. Pay a registration fee of Rs 499 to confirm your position.",

    safe:
        "Your SBI account statement for August is now available in the official SBI mobile application. Please open the SBI app to view it."
};


function loadExample(type) {

    document.getElementById("messageInput").value =
        examples[type];

}


async function scanThreat() {

    const message =
        document
            .getElementById("messageInput")
            .value
            .trim();


    if (!message) {

        alert(
            "Please paste a message to analyze."
        );

        return;

    }


    document
        .getElementById("results")
        .classList
        .add("hidden");


    document
        .getElementById("loading")
        .classList
        .remove("hidden");


    try {

        const response =
            await fetch(API_URL, {

                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body:
                    JSON.stringify({
                        message: message
                    })

            });


        if (!response.ok) {

            throw new Error(
                "Server returned " +
                response.status
            );

        }


        const data =
            await response.json();


        displayResults(data);


    } catch (error) {

        console.error(error);

        alert(
            "Unable to connect to SovereignShield backend."
        );

    }


    document
        .getElementById("loading")
        .classList
        .add("hidden");

}


function displayResults(data) {

    document
        .getElementById("results")
        .classList
        .remove("hidden");


    document
        .getElementById("score")
        .textContent =
            data.final_risk_score;


    document
        .getElementById("riskLevel")
        .textContent =
            data.risk_level;


    document
        .getElementById("threatType")
        .textContent =
            data.threat_type;


    displayIndicators(data);

    displayURLs(data);

    displayRecommendations(
        data.recommendations
    );


    document
        .getElementById("results")
        .scrollIntoView({
            behavior: "smooth"
        });

}


function displayIndicators(data) {

    const container =
        document.getElementById(
            "indicators"
        );


    container.innerHTML = "";


    const indicators =
        data.message_analysis
            .indicators;


    if (!indicators.length) {

        container.innerHTML =
            "<p>No major message indicators detected.</p>";

        return;

    }


    indicators.forEach(item => {

        const div =
            document.createElement("div");

        div.className =
            "indicator";


        const name =
            document.createElement("div");

        name.className =
            "indicator-name";

        name.textContent =
            formatCategory(
                item.category
            );


        const details =
            document.createElement("div");

        details.className =
            "indicator-details";

        details.textContent =
            `${item.keywords_found.join(", ")} • +${item.points} points`;


        div.appendChild(name);

        div.appendChild(details);

        container.appendChild(div);

    });

}


function displayURLs(data) {

    const container =
        document.getElementById(
            "urlAnalysis"
        );


    container.innerHTML = "";


    if (!data.url_analysis.length) {

        container.innerHTML =
            "<p>No URL detected in this message.</p>";

        return;

    }


    data.url_analysis.forEach(url => {

        const box =
            document.createElement("div");

        box.className =
            "url-box";


        box.innerHTML = `
            <div class="url-domain">
                ${escapeHtml(url.domain)}
            </div>

            <div class="url-score">
                ${url.risk_level}
                • ${url.risk_score}/100
            </div>
        `;


        container.appendChild(box);

    });

}


function displayRecommendations(
    recommendations
) {

    const list =
        document.getElementById(
            "recommendations"
        );


    list.innerHTML = "";


    recommendations.forEach(item => {

        const li =
            document.createElement("li");

        li.textContent =
            item;

        list.appendChild(li);

    });

}


function formatCategory(category) {

    return category
        .replaceAll("_", " ")
        .replace(
            /\b\w/g,
            char => char.toUpperCase()
        );

}


function escapeHtml(text) {

    const div =
        document.createElement("div");

    div.textContent =
        text;

    return div.innerHTML;

}
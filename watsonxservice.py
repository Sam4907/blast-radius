import os
import json
from dotenv import load_dotenv

load_dotenv()


def generate_risk_report(blast_radius_json: dict) -> str:
    """
    Generate an AI risk report from blast-radius data.

    Uses Watsonx when credentials are available.
    Falls back to a local mock response when they are not.
    """

    api_key = os.getenv("WATSONX_APIKEY")
    project_id = os.getenv("WATSONX_PROJECT_ID")
    watsonx_url = os.getenv(
        "WATSONX_URL",
        "https://us-south.ml.cloud.ibm.com"
    )

    # Mock mode when credentials are unavailable
    if not api_key or not project_id:
        direct = blast_radius_json.get("direct", [])
        indirect = blast_radius_json.get("indirect", [])

        return (
            "MOCK RISK REPORT\n\n"
            f"Direct Impact: {len(direct)} function(s)\n"
            f"Indirect Impact: {len(indirect)} function(s)\n"
            "Risk Level: Medium\n\n"
            "Recommended Action:\n"
            "Run tests covering the modified function and its callers."
        )

    # Real Watsonx mode
    from ibm_watsonx_ai import Credentials
    from ibm_watsonx_ai.foundation_models import ModelInference

    credentials = Credentials(
        url=watsonx_url,
        api_key=api_key
    )

    model = ModelInference(
        model_id="ibm/granite-13b-chat-v2",
        credentials=credentials,
        project_id=project_id
    )

    prompt = f"""
You are a software engineering risk analysis assistant.

Analyze this blast-radius information:

{json.dumps(blast_radius_json, indent=2)}

Return:
1. Overall Risk Score: Low, Medium, High, or Critical
2. Impact Breakdown
3. Specific unit tests that MUST be run before merging

Keep the response concise and developer-focused.
"""

    response = model.generate_text(prompt=prompt)

    return response


if __name__ == "__main__":
    dummy_data = {
        "target": "billing.charge_card",
        "direct": ["checkout.complete_order"],
        "indirect": ["main.process_payment"],
        "nodes": [],
        "edges": []
    }

    print(generate_risk_report(dummy_data))
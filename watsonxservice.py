import os
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

try:
    from ibm_watsonx_ai.foundation_models import Model
    from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
    HAS_WATSONX_SDK = True
except ImportError:
    HAS_WATSONX_SDK = False


def generate_risk_report(blast_radius_json: dict) -> str:
    """
    Sends the blast radius JSON payload to IBM watsonx (Granite model)
    and returns a structured Markdown risk report and test recommendation list.
    """
    target = blast_radius_json.get("target", "Unknown Function")
    direct = blast_radius_json.get("blast_radius", {}).get("direct", [])
    indirect = blast_radius_json.get("blast_radius", {}).get("indirect", [])

    api_key = os.getenv("WATSONX_APIKEY")
    project_id = os.getenv("WATSONX_PROJECT_ID")
    url = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")

    # If SDK or credentials are missing, deliver a clean structured mock response
    if not HAS_WATSONX_SDK or not api_key or not project_id:
        direct_str = ", ".join(f"`{d}`" for d in direct) if direct else "None"
        indirect_str = ", ".join(f"`{i}`" for i in indirect) if indirect else "None"
        
        return f"""### ⚠️ Blast Radius Risk Assessment (IBM watsonx - Granite)

**Modified Target:** `{target}`  
**Risk Severity:** {"HIGH 🔴" if len(direct) + len(indirect) > 2 else "MEDIUM 🟠" if direct else "LOW 🟢"}

---

#### 📊 Impact Breakdown
* **Direct Callers (1-hop):** {len(direct)} function(s) ({direct_str})
* **Indirect Callers (2+ hops):** {len(indirect)} function(s) ({indirect_str})

#### 🧪 Required Test Suites
1. **Target Unit Test:** Run tests specifically targeting `{target}`.
2. **Integration Test:** Execute downstream test paths for {direct_str}.

> *Note: Running in fallback mode. Add `WATSONX_APIKEY` and `WATSONX_PROJECT_ID` to your `.env` file to trigger live Granite inference.*
"""

    prompt = f"""You are an expert AI Code Reliability Engineer analyzing code dependency graphs.
A developer modified the function `{target}`.

Blast Radius Data:
- Target Modified: `{target}`
- Directly Impacted Functions (1-hop): {direct}
- Indirectly Impacted Functions (2+ hops): {indirect}

Provide a concise, professional risk report in Markdown:
1. **Risk Assessment**: Level (LOW, MEDIUM, HIGH, CRITICAL) with justification.
2. **Impact Summary**: Concise breakdown of affected upstream features.
3. **Recommended Test Suite**: Exact functions or integration flows that MUST be tested before merging.
4. **Safety Recommendations**: Short advice to avoid breaking changes.
"""

    credentials = {
        "url": url,
        "apikey": api_key
    }

    parameters = {
        GenParams.DECODING_METHOD: "greedy",
        GenParams.MAX_NEW_TOKENS: 450,
        GenParams.MIN_NEW_TOKENS: 40,
    }

    try:
        model = Model(
            model_id="ibm/granite-13b-chat-v2",
            params=parameters,
            credentials=credentials,
            project_id=project_id
        )
        return model.generate_text(prompt=prompt)
    except Exception as e:
        return f"### ⚠️ watsonx API Error\nFailed to invoke Granite model: `{str(e)}`"


if __name__ == "__main__":
    # Test script standalone
    sample_data = {
        "target": "billing.charge_card",
        "blast_radius": {
            "direct": ["checkout.complete_order"],
            "indirect": ["cart.checkout_flow"]
        }
    }
    print(generate_risk_report(sample_data))
"""Extract and validate a single JSON proposal from an OpenAI Responses API result."""
import json


def extract_proposal(answer):
    if not isinstance(answer, dict):
        raise ValueError("Response must be a JSON object")
    if answer.get("status") not in (None, "completed"):
        raise ValueError("Model response was not completed")
    texts = []
    for item in answer.get("output", []):
        if item.get("type") != "message":
            continue
        for part in item.get("content", []):
            if part.get("type") == "output_text":
                texts.append(part.get("text", ""))
    if not texts:
        raise ValueError("Model returned no output text")
    try:
        proposal = json.loads("".join(texts))
    except json.JSONDecodeError as exc:
        raise ValueError("Model output is not valid JSON") from exc
    if not isinstance(proposal, dict) or set(proposal) != {"path", "content"}:
        raise ValueError("Model output must contain exactly path and content")
    return proposal

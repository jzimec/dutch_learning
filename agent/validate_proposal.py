"""Validate model-proposed code before creating a review patch."""
import ast
import fnmatch
import subprocess


def validate_proposal(proposal, sources, config):
    if not isinstance(proposal, dict):
        raise ValueError("Model response must be an object")
    name = proposal.get("path")
    content = proposal.get("content")
    if not isinstance(name, str) or name not in sources:
        raise ValueError("Proposed path is not an existing supplied source")
    if any(fnmatch.fnmatch(name, pattern) for pattern in config["protected_paths"]):
        raise ValueError("Protected file cannot be changed")
    if not any(fnmatch.fnmatch(name, pattern) for pattern in config["allowed_paths"]):
        raise ValueError("Proposed path is not allowed")
    if not isinstance(content, str) or not content.strip():
        raise ValueError("Proposed content is empty")
    if content == sources[name]:
        raise ValueError("No changes proposed")
    if len(content.encode("utf-8")) > 60000:
        raise ValueError("Proposed file exceeds size limit")
    if name.endswith(".py"):
        ast.parse(content, filename=name)
    elif name.endswith(".js"):
        result = subprocess.run(
            ["node", "--check", "--input-type=commonjs"],
            input=content, text=True, capture_output=True, timeout=15,
        )
        if result.returncode:
            raise ValueError("Invalid JavaScript syntax: " + result.stderr[:500])
    return name, content

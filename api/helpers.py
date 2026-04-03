"""
Hermes Web UI -- HTTP helper functions.
"""
import json as _json
from pathlib import Path
from api.config import IMAGE_EXTS, MD_EXTS


def require(body: dict, *fields):
    """Phase D: Validate required fields. Raises ValueError with clean message."""
    missing = [f for f in fields if not body.get(f) and body.get(f) != 0]
    if missing:
        raise ValueError(f"Missing required field(s): {', '.join(missing)}")


def bad(handler, msg, status=400):
    """Return a clean JSON error response."""
    return j(handler, {'error': msg}, status=status)


def safe_resolve(root: Path, requested: str) -> Path:
    """Resolve a relative path inside root, raising ValueError on traversal."""
    resolved = (root / requested).resolve()
    resolved.relative_to(root.resolve())  # raises ValueError if outside root
    return resolved


def _security_headers(handler):
    """Add security headers to every response."""
    handler.send_header('X-Content-Type-Options', 'nosniff')
    handler.send_header('X-Frame-Options', 'DENY')
    handler.send_header('Referrer-Policy', 'same-origin')


def j(handler, payload, status=200):
    """Send a JSON response."""
    body = _json.dumps(payload, ensure_ascii=False, indent=2).encode('utf-8')
    handler.send_response(status)
    handler.send_header('Content-Type', 'application/json; charset=utf-8')
    handler.send_header('Content-Length', str(len(body)))
    handler.send_header('Cache-Control', 'no-store')
    _security_headers(handler)
    handler.end_headers()
    handler.wfile.write(body)


def t(handler, payload, status=200, content_type='text/plain; charset=utf-8'):
    """Send a plain text or HTML response."""
    body = payload if isinstance(payload, bytes) else str(payload).encode('utf-8')
    handler.send_response(status)
    handler.send_header('Content-Type', content_type)
    handler.send_header('Content-Length', str(len(body)))
    handler.send_header('Cache-Control', 'no-store')
    _security_headers(handler)
    handler.end_headers()
    handler.wfile.write(body)


MAX_BODY_BYTES = 20 * 1024 * 1024  # 20MB limit for non-upload POST bodies


def read_body(handler):
    """Read and JSON-parse a POST request body (capped at 20MB)."""
    length = int(handler.headers.get('Content-Length', 0))
    if length > MAX_BODY_BYTES:
        raise ValueError(f'Request body too large ({length} bytes, max {MAX_BODY_BYTES})')
    raw = handler.rfile.read(length) if length else b'{}'
    try:
        return _json.loads(raw)
    except Exception:
        return {}

import json

DATA_FIELD = b"data:"


def _parse_sse_event(text):
    """Parses an SSE event."""
    if text.startswith(b":"):
        # SSE comment, discard.
        return None

    if not text.startswith(DATA_FIELD):
        # We only handle data: elements.
        return None

    try:
        return json.loads(text[len(DATA_FIELD) :])
    except Exception as e:
        return None


def stream_sse_events(source):
    """Parses SSE events out of `source`.

    `source` should be an incoming stream of byte chunks.

    NOTE: This only handles the subset of SSE used by the matroid API, it is not
    a general purpose parser.
    """
    buffer = b""
    for chunk in source:
        buffer += chunk
        parts = buffer.split(b"\n\n")
        for part in parts[:-1]:
            event = _parse_sse_event(part)
            if event is None:
                continue
            yield event

        buffer = parts[-1]

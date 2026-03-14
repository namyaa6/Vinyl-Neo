"""Shared Vinyl Neo styling."""

def get_vinyl_css() -> str:
    """Return the vintage vinyl theme CSS wrapped in style tags."""
    try:
        with open("assets/style.css", "r") as f:
            css = f.read()
    except FileNotFoundError:
        css = _fallback_css()
    return f"<style>\n{css}\n</style>"


def _fallback_css() -> str:
    return """
    .stApp { background-color: #0a0a0a; color: #f5e6d3; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    .feature-card { background: #141010; border: 1px solid #2c1810; }
    .rec-card { background: #141010; border: 1px solid #2c1810; }
    .why-badge { background: #2c1810; color: #c4a574; padding: 4px 12px; border-radius: 20px; }
    """

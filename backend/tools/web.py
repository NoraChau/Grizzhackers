"""Web search with Exa. OPTIONAL: only used if Exa credits arrive.

Owner: Nora

Must no-op cleanly when EXA_API_KEY is empty: return an "error: ..." string, never crash.
exa-py is not in requirements.txt until we have credits, so import it inside the function,
not at the top of this file.

Docs: https://docs.exa.ai/
"""


def web_search(query: str) -> str:
    """Search the web and return a few short results (title, one line, URL) for the model.

    TODO(Nora): if os.environ.get("EXA_API_KEY") is empty, return
    "error: web search is off (no EXA_API_KEY)". Otherwise call Exa and keep the result
    short: it all goes back into the model's context.
    """
    return "error: web search is off"

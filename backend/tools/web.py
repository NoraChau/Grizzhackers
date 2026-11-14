"""Tools: web search with Exa. Used by hero task 3 ("look up the Hack the Nest schedule...").

Owner: Intermediate
Docs: https://docs.exa.ai/ (Python SDK: exa-py)
"""


def web_search(query: str, num_results: int = 5) -> str:
    """Search the web and return results as short text: title, URL, and the useful page text.

    TODO(intermediate):
    - Read EXA_API_KEY from the environment; never print it.
    - Include page text, not just links, so the model can pull out facts (e.g. times).
    - Cut each result to a few hundred characters so you don't flood the model's context.
    """
    raise NotImplementedError("TODO(intermediate): web_search")

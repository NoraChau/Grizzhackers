"""Tools the agent can call. Each tool is one small function that returns a short string.

Rule: tools never raise into the agent loop. On failure, return "error: <what went wrong>"
so the model can read it and try something else.
"""

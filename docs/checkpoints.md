# Checkpoints

## Steps taken since the last checkpoint:

1.  Added "Protected" to the select source options in `projects/mcp-server-oauth2.0/services/streamlit/app/pages/1_Tools.py`.
2.  Added "protected/protected.csv" to the default files list in `projects/mcp-server-oauth2.0/services/streamlit/app/pages/1_Tools.py`.
3.  Modified the `projects/mcp-server-oauth2.0/services/streamlit/app/pages/1_Tools.py` file to include the owner in the payload for the OPA policy evaluation.
4.  Improved the error handling in `projects/mcp-server-oauth2.0/services/streamlit/app/pages/1_Tools.py` to display a more specific error message when a user tries to access a protected file.
5.  Rebuilt and restarted the server multiple times using `docker compose` commands.

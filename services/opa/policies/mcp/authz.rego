package mcp.authz

default allow = false

# Admins allowed all actions
allow {
  input.subject.role == "admin"
}

# Users can read CSVs only in public directory
allow {
  input.subject.role == "user"
  input.action == "excel.read"
  startswith(input.resource.path, "/data/public/")
}

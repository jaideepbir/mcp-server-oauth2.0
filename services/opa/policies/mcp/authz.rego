package mcp.authz

default allow = false

# Admins allowed all actions
allow {
  input.subject.role == "admin"
}

# Allow users to read resources they own
allow {
  input.subject.role == "user"
  input.action == "excel.read"
  input.resource.owner == input.subject.sub
}

# Allow all users to read public files
allow {
  input.action == "excel.read"
  startswith(input.resource.path, "/data/public/")
}

# Allow users to upload/write files to the uploads directory
allow {
  input.subject.role == "user"
  input.action == "excel.write"
  startswith(input.resource.path, "/data/uploads/")
}

# Allow admins to upload/write files (general rule, covers uploads too)
allow {
  input.subject.role == "admin"
  input.action == "excel.write"
}

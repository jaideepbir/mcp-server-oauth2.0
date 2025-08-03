package mcp.authz

default allow = false
rights := rights_calc

rights_calc := "rw" {
  input.subject.role == "admin"
}
rights_calc := "r" {
  input.subject.role == "user"
}

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

# Example future rules for DB/table actions
# allow {
#   input.subject.role == "admin"
#   startswith(input.action, "db.")
# }
# allow {
#   input.subject.role == "user"
#   input.action == "db.read"
#   input.resource.schema == "public"
# }

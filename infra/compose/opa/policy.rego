package eduassist.authz

default allow := false

allow if {
  input.action == "health.read"
}

allow if {
  input.subject.role == "platform_admin"
}


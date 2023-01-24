# cloud deploy notifier

A terraform module, to create and manage all infra belonging to a single
notifier. If a notifier doesn't need role memberships or additional resources
beyond what's packaged here, then this module can be used directly as a root
module. If additional resources are required, this module can be called as an
embedded component module to establish baseline resources.

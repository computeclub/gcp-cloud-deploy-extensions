# cloud deploy extension

A terraform module, to create and manage all infra belonging to a single
extension. If a extension doesn't need role memberships or additional resources
beyond what's packaged here, then this module can be used directly as a root
module. If additional resources are required, this module can be called as an
embedded component module to establish baseline resources.

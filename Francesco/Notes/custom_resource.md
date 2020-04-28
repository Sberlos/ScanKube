## Custom Resources ##

You can create you custom resource that can be later manipulated with [kubectl](kubectl.md).

To make a new, custom resource part of a declarative API there needs to be a controller to retrieve the structured data continually and act to meet and maintain the declared state.
This controller, or operator, is an agent to create and mange one or more instances of a specific stateful application.

Two ways to create one:
* Add a `Custom Resource Definition` (easy but not flexible)
* Use `Aggregated APIs` (requires a new API server to be written and added)

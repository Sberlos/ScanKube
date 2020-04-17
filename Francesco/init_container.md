## Init Containers ##

It's a [container](container.md) that is started before the app containers starts.
If it fail to start it is restated and all the app containers must wait until it complete.

It can be used to run utilities not in app that needs to be present before the running the main app container.
Another advantage is that the Init Container can have differents settings regarding both storage and security.
This means that you can make it run commands that the main application cannot run.

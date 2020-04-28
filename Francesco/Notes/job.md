## Job ##

A job is a way of doing batch processing on kubernetes.
You can specify a pod to be run until completed.
You can parametrize in order to set the number of jobs to be completed (via `completitions` in the `spec` parameter) the number of concurrent jobs of this type (via `parallelism` als in the `spec` parameter) and the time limit for it to run before being killed (via `activeDeadlineSeconds` also in spec).

You can also do CronJobs.

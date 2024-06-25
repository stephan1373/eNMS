# Workers

A worker is created or updated whenever a job starts running. By default, the worker's name is set to "Server Name - Process ID" to ensure uniqueness across servers.

<h4>Workers Details</h4> 
![Worker Details](../_static/administration/worker.png)

* **Name**: Name of the worker - defaults to "Server Name - Process ID"
* **Process ID**: Unix Process ID (obtained with os.getpid)
* **Description**: Text field for storing notes 
* **Subtype**: Specifies the application that spawned the worker. The subtype is determined by the "_" environment variable, which varies based on the deployment method. Common values include "python3" "gunicorn" or "dramatiq".
* **Last Update**: The last time the worker was updated

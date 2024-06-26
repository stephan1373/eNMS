"Secrets" allow users to link a secret value to a key, enabling its use in a workflow without revealing the value to those viewing the workflow.

<br/>
<h4>Main Properties</h4> 

![Main Properties](../_static/administration/secret_property.png)

* **Name**: Unique identification for secret name
* **Description**: Text field for storing notes  
* **Value**: Secret value (never shown in the UI)

<br/>
<h4>RBAC properties</h4> 
Fine control of actions a team can take.

![Menu and Endpoint Access](../_static/administration/secret_rbac.png)

* **Owners**: Users allowed to configure RBAC
* **Admin Only**: If selected, only admin users can access the secret
* **Read Access**: Groups of users allowed to read the secret
* **Edit Access**: Groups of users allowed to edit the secret
* **Use Access**: Groups of users allowed to use the secret in a workflow

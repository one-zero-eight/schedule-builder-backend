## Deployment view
![](https://github.com/SWP2025/schedule-builder-backend/blob/main/docs/architecture/deployment-view/deploymentDiagram.png)

We chose the following deployment structure, specifically `Docker` tool,
because of the availability of swift servers change without `Docker Hub` deploy
structure alterations. Moreover, such setup is simplistic to deploy on the
customer's side:
- if the customer is **not** interested in project privacy, then a server
has to be bought for the customer, and `Docker` has to be set up with one
script on the server; after that, the product is ready for deployment on
the customer's server,
- if the customer is **indeed** interested in project privacy, then a separate
account is registered for the customer, a private `GitHub` repository is created
for the customer, and deployment is conducted in a private manner with steps provided
for the previous case. 

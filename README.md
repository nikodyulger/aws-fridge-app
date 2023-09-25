# Fridge App

 **Fridge App** is built with the objective to illustrate how a CICD pipeline works and how one can take control and monitor the resources that is using. It is just an quick and straighforward example of how to deploy a simple web app on AWS cloud.

## Architecture

The core AWS services used for this project are:

- **AppRunner**: the simplest way to deploy an app, you only need to provide the code, everything else is done for you.
- **CodePipeline** and **CodeBuild**: there are part of the *"Code"* family dedicated to create continuous integration and deployment pipelines.
- **EventBridge**: the serverless way of capturing data from your applications and services.
- **Lambda**: everybody talks about it nowadays. It is not only useful to build apps, it is also very powerful to control, monitor or take certain actions on your infrastructure.

![Arquitectura AWS](architecture-diagram.png)
# Fridge App

**Fridge App** is built with the objective to illustrate how a CICD pipeline works and how one can take control and monitor the resources that is using. It is just an quick and straighforward example of how to deploy a simple web app on AWS cloud.

It is available on this URL https://fridge-app.dev-niko.com and this a quick demo
 
![DEMO](demo.gif)

## Architecture

The core AWS services used for this project are:

- **AppRunner**: the simplest way to deploy an app, you only need to provide the code, everything else is done for you.
- **CodePipeline** and **CodeBuild**: there are part of the *"Code"* family dedicated to create continuous integration and deployment pipelines.
- **EventBridge**: the serverless way of capturing data from your applications and services.
- **Lambda**: everybody talks about it nowadays. It is not only useful to build apps, it is also very powerful to control, monitor or take certain actions on your infrastructure.

![AWS Architecture](architecture-diagram.png)

The diagram illustrates the entire architecture of the web app. All resources are deployed via **CloudFormation** except for Lambdas, which are deployed using **Serverless Framework** because it is more simple. Let’s explain everything by parts:

1. **CICD pipeline**: every time there is a change on *master* branch of the code repository, the CodePipeline is triggered. It source the code from **GitHub**, then it runs the test in CodeBuild and after there are passed an ECR image is created. The Lambda *deploy-action* starts a new *“manual”* deployment for the App Runner service with the already created image.
2. **App Runner**: it is a containeraized web app, static HTML templates are sent to the client with the data from a DynamoDB. 
3. **Events**: as AppRunner can get quite expensive, there are 
*cron* events that triggers a Lambda which *starts* or *resumes* its execution based on the received parameters. On the other hand, there is an EventBridge rule that listens the *success* or *failure* of these controlling actions and also of the launched deployments over the service. This way a message is sent to an **SNS** topic and the subscriptors are notified of these changes.
4. **Custom Domain**: registered and linked alias *DNS record* created with **Route53**, so users can find the web with a more readable URL.
5. **Roles, Policies and Logs**: the invisible part, but one of the most critical in the design of every infrastructure.

## Frameworks/Tools

The infrastructure is not the only relevant part of this project, it is also important to know how to create it. With that purpose, several frameworks and tools are used:

- [**FastApi**](https://fastapi.tiangolo.com/): it helps to create self-documented APIs in a very simple and fast way
- [**Serverless**](https://www.serverless.com/): it boost the deployment of serverless resources to the cloud by simplifying your templates
- [**Handlebars**](https://handlebarsjs.com/): it is used to create modularized HTML templates
- [**Jinja**](https://jinja.palletsprojects.com/en/3.1.x/): it helps to create dynamic templates with Python
- [**Pytest**](https://docs.pytest.org/en/7.4.x/): it is used to automate testing of your code
- [**Moto**](https://docs.getmoto.org/en/latest/): it mocks some cloud services for testing purposes
- [**Docker**](https://docs.docker.com/): it created the containers for your app, so it can be runned everywhere


## Deployment process

The deployment of the app is done in several steps that must be followed in this order:

Previous manual steps:
- Create a [connection](https://docs.aws.amazon.com/codepipeline/latest/userguide/connections-github.html) with your GitHub. It is necessary for CodePipeline to source the code and later on build the artefacts
- Register a [domain](https://aws.amazon.com/es/getting-started/hands-on/get-a-domain/) on Route53. Find a domain you like and pay for it, the hosted zone is created automatically for you

Stack order:
1. Serverless. Deploy all lambdas as we already know how we are going to name our service. The command to execute inside the `infrastructure/lambdas` is `serverless deploy`. For that, you need to install serverless previously on your local machine with `npm install -g serverless`
2. `ci_cd.yml` is the first stack to deploy. Remember to introduce the already created **GitHub connection ID** as parameter. The first execution of the pipeline will fail, because the App Runner service won’t exist yet. However, an image will be build and be available at the ECR repository
3. `app_runner` template will deploy the service and a dynamo table to which the queries are made. It takes a while, be patient. Remember it is provisioning all the infrastructure for you.
4. Last but not least, `eventbridge` will create the listeners for the AppRunner service with the SNS topic and subscription. Remember to confirm the subscription, if not you will not be monitoring nothign at all. Check the spam folder of your email just in case!

## Costs

To save costs the action have been taken:
- AppRunner with manual deployments, to save that `1` *extra dollar* from the bill for automatic deployments.
- Pause/Resume the AppRunner service to avoid traffic and instance cost per hour. Run it only when you need it.
- Provision the smallest instance possible
- Free Tier for CodePipeline, CodeBuild, Lambda, Eventbridge and SNS

The highest cost is to a register a domain (nearly 15 USD).  AppRunner is the only one that calculations can get very messy and unpredictable. Everything else is at cost zero if there is low traffic and there are not unnecessary builds.

**NOTE** Try to use the [AWS Pricing Calculator](https://calculator.aws/#/) to understand for what are you going to be billed and forecast your expenses.

## Future Work

There is always work to be done. Here is a wishlist that I have thought about for this project:

- Integrate the SNS topics with some alert/monitor tool. Not just sending raw events to a e-mail
- Create dynamic tags for the ECR image
- Add more functionality to the app, for example, send message if there are expired items

## References

- [Controlling and monitoring AWS App Runner applications with Amazon EventBridge](https://aws.amazon.com/es/blogs/containers/controlling-and-monitoring-aws-app-runner-applications-with-amazon-eventbridge/)
- [AWS CodePipeline: Build & Test with CodeBuild](https://community.ops.io/jatin/aws-codepipeline-build-test-with-codebuild-1bdh)
- [Deploy Python Application using AWS App Runner](https://aws.amazon.com/es/blogs/containers/deploy-python-application-using-aws-app-runner/)
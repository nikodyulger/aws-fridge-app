import os
import json
import boto3

APP_NAME = os.getenv('APP_NAME')

codepipeline = boto3.client('codepipeline')
app_runner = boto3.client('apprunner')

def handler(event, context):

    # Retrieve the Job ID from the Lambda action and UserParameters
    job_id = event['CodePipeline.job']['id']
    pipeline_service = event["CodePipeline.job"]["data"]["actionConfiguration"]["configuration"]["UserParameters"]

    if not pipeline_service or APP_NAME not in pipeline_service:
        put_job_failure('The UserParameters field must contain a valid reference to the AppRunner service')
        return
    
    service_arn = get_service_arn(pipeline_service, job_id, context)
    start_deployment(service_arn, job_id, context)

# Notify CodePipeline of a successful job
def put_job_success(job_id):
    print("JOB SUCCESS")
    codepipeline.put_job_success_result(jobId=job_id)
    return

# Notify CodePipeline of a failed job
def put_job_failure(job_id, message, context):
    print("JOB FAILURE")
    print(message)
    params = {
        'jobId': job_id,
        'failureDetails': {
            'message': json.dumps(message),
            'type': 'JobFailed',
            'externalExecutionId': context.aws_request_id
        }
    }
    codepipeline.put_job_failure_result(jobId=job_id, failureDetails=params['failureDetails'])
    return 

def get_service_arn(service_name, job_id, context):
    try:
        response = app_runner.list_services()
        service_arn = [s['ServiceArn'] for s in response['ServiceSummaryList'] if s['ServiceName'] == service_name][0]
        print(service_arn)
        return service_arn
    except Exception as error:
        put_job_failure(job_id,str(error), context)

def start_deployment(service_arn, job_id, context):
    try:
        response = app_runner.describe_service(ServiceArn=service_arn)

        if response['Service']['Status'] == 'RUNNING':
            response = app_runner.start_deployment(ServiceArn=service_arn)
            operation_id = response['OperationId']

            response = app_runner.list_operations(ServiceArn=service_arn)
            status = [o['Status'] for o in response['OperationSummaryList'] if o['Id'] == operation_id][0]
            print(f"Deployment operation_id {operation_id} with status {status}")

            put_job_success(job_id)
        else:
            print(f"Service {service_arn} not running, deployment cannot be performed")
            put_job_failure()
    except Exception as error:
        put_job_failure(job_id, str(error), context)


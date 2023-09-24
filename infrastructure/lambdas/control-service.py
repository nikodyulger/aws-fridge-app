import boto3

app_runner = boto3.client('apprunner')

def handler(event, context):

    service_name = event['service_name']
    action = event['action']
    service_arn = get_service_arn(service_name)

    if action == 'pause':
        print(f'Pausing App Runner Service: {service_arn}')
        response = app_runner.pause_service(ServiceArn=service_arn)
    elif action == 'resume':
        print(f'Resuming App Runner Service: {service_arn}')
        response = app_runner.resume_service(ServiceArn=service_arn)

    return response

def get_service_arn(service_name):

    response = app_runner.list_services()
    service_arn = [s['ServiceArn'] for s in response['ServiceSummaryList'] if s['ServiceName'] == service_name][0]
    print(f"Found service_arn {service_arn}")

    return service_arn

from chalice import Chalice, Response
import time
import boto3
from botocore.exceptions import ClientError

app = Chalice(app_name='timercheck')
home_url = 'https://alestic.com/2015/07/timercheck-scheduled-events-monitoring/'
table_name = 'timer'

def error(status, message):
    return Response(
        status_code=status,
        body={'errorMessage': message},
    )

def redirect(url):
    return Response(
        status_code=301,
        headers={'Location': url},
        body='',
    )

def timer_table(table_name):
    dynamodb = boto3.resource('dynamodb')
    try:
        response = dynamodb.create_table(
            TableName=table_name,
            AttributeDefinitions=[
                {
                    'AttributeName': 'timer',
                    'AttributeType': 'S'
                },
            ],
            KeySchema=[
                {
                    'AttributeName': 'timer',
                    'KeyType': 'HASH'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        print("Created DynamoDB table: ", table_name)
    except Exception as e:
        if e.__class__.__name__ != 'ResourceInUseException':
            print('ERROR creating table "%s": %s' % (table_name, e))
    return dynamodb.Table(table_name)

def process(timer, count):
    try:
        now = int(time.time())
        results = {
            'timer': timer,
            'request_id': app.current_request.context['requestId'],
            'status': 'ok',
            'now': now,
            'message': 'Timer still running',
        }
        get_response = table.get_item(Key={'timer': timer})
        if (not 'Item' in get_response or
                not 'start_time' in get_response['Item']):
            if count is None:
                return error(404, '404: timer has never been set')
        else:
            item = get_response['Item']
            results['start_time'] = item['start_time']
            results['start_seconds'] = item['start_seconds']
            results['seconds_elapsed'] = now - item['start_time']
            results['seconds_remaining'] = (item['start_seconds'] -
                                            (now - item['start_time']))
        if count is None:
            if results['seconds_remaining'] <= 0:
                return error(504, 'timer timed out')
        else:
            put_response = table.put_item(
                Item={
                    'timer': timer,
                    "start_time": now,
                    "start_seconds": int(count)
                }
            )
            results['message'] = "Timer countdown updated"
            results['new_start_time'] = now
            results['new_start_seconds'] = int(count)
        return results
    except Exception as e:
        print("Unexpected Error: %s" % e)
        return error(500, '500: server error')

@app.route('/')
def index():
    return redirect(home_url)

@app.route('/{timer}')
def get_timer(timer):
    return process(timer, None)

@app.route('/{timer}/{count}')
def set_timer(timer, count):
    return process(timer, count)

@app.route('/introspect')
def introspect():
    return app.current_request.to_dict()

table = timer_table(table_name)

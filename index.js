var doc = require('dynamodb-doc');
var dynamo = new doc.DynamoDB();
exports.handler = function(event, context) {
    var response = {
        "timer": event.timer,
        "request_id": context.awsRequestId,
        "status": "ok",
        "now": Math.round(Date.now() / 1000)
    };
    dynamo.getItem({
        "TableName": "timer",
        "Key": {
            "timer": event.timer
        }
    }, function(error, timer_result) {
        if (error) {
            context.fail("500: error retrieving timer");
            return;
        }
        if (timer_result.Item) {
            response.start_time = timer_result.Item.start_time;
            response.start_seconds = timer_result.Item.start_seconds;
            response.seconds_elapsed = response.now - response.start_time;
            response.seconds_remaining = response.start_seconds - response.seconds_elapsed;
        }
        if (event.countdown !== undefined) {
            var new_start_seconds = parseInt(event.countdown, 10);
            dynamo.putItem({
                "TableName": "timer",
                "Item": {
                    "timer": event.timer,
                    "start_time": response.now,
                    "start_seconds": new_start_seconds
                }
            }, function (error, result) {
                if (error) {
                    context.fail("500: error setting timer");
                    return;
                }
                response.message = "Timer countdown updated";
                response.new_start_time = response.now;
                response.new_start_seconds = new_start_seconds;
                context.succeed(response);
            });
        } else {
            if (!timer_result.Item) {
                context.fail("404: timer has never been set");
                return;
            } 
            if (response.seconds_remaining <= 0) {
                context.fail("504: timer timed out");
                return;
            }
            response.message = "Timer still running";
            context.succeed(response);
        }
    });
};

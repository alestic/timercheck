# TimerCheck.io

This repository contains an AWS Lambda function that powers the web
service API behind TimerCheck.io

For more information about what the service does and how to use it,
please read the following article:

> TimerCheck.io - Countdown Timer Microservice

> https://alestic.com/2015/07/timercheck-scheduled-events-monitoring/

The following commands work on Ubuntu 17.04 Zesty:

Install prerequisites:

    make setup

Deploy to AWS account:

    make deploy

Show AWS Lambda function logs

    make logs

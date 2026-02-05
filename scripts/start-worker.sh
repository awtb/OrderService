#!/bin/sh

export PYTHONPATH=$(pwd)/src:$PYTHONPATH
taskiq worker order_worker.taskiq_app:broker

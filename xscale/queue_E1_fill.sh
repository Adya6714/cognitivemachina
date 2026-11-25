#!/bin/bash
# Re-run the resumable queues once both finish, to fill any cell lost to an OOM kill / restart.
cd "$(dirname "$0")/.."
while pgrep -f "queue_E1_v2|queue_E1_A8" >/dev/null; do sleep 60; done
./xscale/queue_E1_v2.sh; ./xscale/queue_E1_A8.sh
echo FILL_DONE >> logs/E1_queue.log

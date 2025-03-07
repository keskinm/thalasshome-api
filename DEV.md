## Check logs

`gcloud app logs tail -s default`


## Cleaning deployments 

`gcloud app versions list`

`gcloud app versions delete 20250302t153056`

Or don't even bother and delete all previous ones (with 0 traffic) directly:

`gcloud app versions list --format="value(VERSION.ID,TRAFFIC_SPLIT)" | awk '$2 == "0.00" {print $1}' | xargs gcloud app versions delete -q`


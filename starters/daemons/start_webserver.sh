#!/bin/bash

cd ../..&&\
sudo -s &&\
source env.sh&&\
source local_env.sh&&\
gunicorn -b 0.0.0.0:8000 dashboard.main:app --daemon
#!/bin/bash
# Set environment variables
export COMET_API_KEY=""  # Your actual Comet API key
export NEPTNUNE_API_TOKEN=""
export NEPTUNE_PROJECT="byyoung3/testing"
export MLFLOW_TRACKING_URI="http://34.143.244.32:5000"

# wandb good 
# mlflow omit 
# Function to read profiles from profiles.json
read_profiles_from_json() {
    jq -r '.profiles | keys[]' profiles.json
}

# Default profiles if no arguments are provided
default_profiles=("v1-empty" "v1-scalars" "v1-tables" "v1-images")

# Initialize profiles variable
profiles=()

# Parse command line arguments
clear_results=false

while [[ "$#" -gt 0 ]]; do
    case $1 in
        --all) profiles=$(read_profiles_from_json); shift ;;
        --clear_results) clear_results=true; shift ;;
        *) profiles+=("$1"); shift ;;
    esac
done

if [ -z "$profiles" ]; then
    profiles=("${default_profiles[@]}")
fi

# Clear results if flag is set
if $clear_results; then
    echo "Clearing all files in ./results"
    rm -rf ./results/*
fi

# Run benchmark scripts for each profile
for p in ${profiles[@]}
do
    python ./bench_comet.py --test_profile "$p"
done


for p in ${profiles[@]}
do
    python ./bench_neptune.py --test_profile "$p"
done

for p in ${profiles[@]}
do
    python ./bench_mlflow.py --test_profile "$p"
done

for p in ${profiles[@]}
do
    python ./bench_wandb.py --test_profile "$p"
done

for p in ${profiles[@]}
do
    python ./bench_wandb_core.py --test_profile "$p"
done

python aggregate_and_log_res.py


# for p in ${profiles[@]}
# do
#     python ./bench_wandb_core_no_cntx_mng.py --test_profile "$p"
# done


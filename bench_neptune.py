#!/usr/bin/env python

import argparse
import multiprocessing
import os
from typing import List, Tuple
import pandas as pd
import numpy as np
import neptune
from neptune.types import File
import _load_profiles
import _timing

project = os.getenv('NEPTUNE_PROJECT')

if project is None:
    raise ValueError("Environment variable NEPTUNE_PROJECT is not set")

VERSION: str = "v1-2024-04-11-0"
BENCH_OUTFILE: str = "./results/bench_neptune.csv"
BENCH_FIELDS: Tuple[str] = (
    "test_name",
    "test_profile",
    "test_variant",
    "client_version",
    "client_type",
    "server_version",
    "server_type",
)
TIMING_DATA: List = []




def run_one(args, n=0, m=0):
    global project
    if args.mode == "online":
        run = neptune.init_run(project=project)
    else:
        run = neptune.init_run(project="offlineProject", mode='offline')

    metrics = {}
    params = {}
    tables = {}
    images = {}

    for e in range(args.num_history):
        for i in range(args.history_floats):
            metrics[f"f_{i}"] = float(n + m + e + i)
        for i in range(args.history_ints):
            metrics[f"n_{i}"] = n + m + e + i
        for i in range(args.history_strings):
            params[f"s_{i}"] = str(n + m + e + i)
        for i in range(args.history_tables):
            table_data = pd.DataFrame([[n + m, e, i, i + 1]], columns=["a", "b", "c", "d"])
            tables[f"t_{i}"] = table_data
        for i in range(args.history_images):
            image_data = np.random.randint(
                255,
                size=(args.history_images_dim, args.history_images_dim, 3),
                dtype=np.uint8,
            )
            images[f"i_{i}"] = image_data

        # Log all accumulated data at the end
        for key, value in metrics.items():
            run[key].log(value)
        for key, value in params.items():
            run[key].log(value)
        for key, value in tables.items():
            run[key].upload(File.as_html(value))
        for key, value in images.items():
            run[key].upload(File.as_image(value))

    run.stop()

def run_sequential(args, m=0):
    for n in range(args.num_sequential):
        run_one(args, n, m)

def run_parallel(args):
    procs = []
    for n in range(args.num_parallel):
        p = multiprocessing.Process(
            target=run_sequential, args=(args, n * args.num_parallel)
        )
        procs.append(p)
    for p in procs:
        p.start()
    for p in procs:
        p.join()

def setup(args):
    pass

def teardown(args):
    pass

@_timing.timeit(TIMING_DATA)
def time_load(args):
    if args.num_parallel > 1:
        run_parallel(args)
    else:
        run_sequential(args)

def run_load(args):
    setup(args)
    time_load(args)
    teardown(args)

def main():
    parser = argparse.ArgumentParser(description="benchmark neptune performance")
    parser.add_argument("--test_name", type=str, default="")
    parser.add_argument(
        "--mode", type=str, choices=("online", "offline"), default="offline"
    )
    parser.add_argument(
        "--test_profile", type=str, default="", choices=list(_load_profiles.PROFILES)
    )
    parser.add_argument("--test_variant", type=str, default="")
    parser.add_argument("--server_version", type=str, default="")
    parser.add_argument("--server_type", type=str, default="")
    parser.add_argument("--client_version", type=str, default=neptune.__version__)
    parser.add_argument("--client_type", type=str, default="")
    parser.add_argument("--num_sequential", type=int, default=1)
    parser.add_argument("--num_parallel", type=int, default=1)
    parser.add_argument("--num_history", type=int, default=1)
    parser.add_argument("--history_floats", type=int, default=0)
    parser.add_argument("--history_ints", type=int, default=0)
    parser.add_argument("--history_strings", type=int, default=0)
    parser.add_argument("--history_tables", type=int, default=0)
    parser.add_argument("--history_images", type=int, default=0)
    parser.add_argument("--history_images_dim", type=int, default=16)
    parser.add_argument("--core", type=str, default="", choices=("true", "false"))
    parser.add_argument("--use-spawn", action="store_true")

    args = parser.parse_args()
    # required by golang experimental client when testing multiprocessing workloads
    if args.use_spawn:
        multiprocessing.set_start_method("spawn")

    args_list = []
    if args.test_profile:
        print("%"*100)
        print(args.mode)
        args_list = _load_profiles.parse_profile(parser, args, copy_fields=BENCH_FIELDS)
    else:
        args_list.append(args)

    for args in args_list:
        print(f"Parsed arguments: {args}")  # Debugging statement
        run_load(args)
        prefix_list = [VERSION]
        for field in BENCH_FIELDS:
            prefix_list.append(getattr(args, field))



        # Include additional test parameters
        additional_params = [
            "num_sequential",
            "num_parallel",
            "num_history",
            "history_floats",
            "history_ints",
            "history_strings",
            "history_tables",
            "history_images",
            "history_images_dim",
        ]
        for param in additional_params:
            prefix_list.append(f"{param}={getattr(args, param)}")

        _timing.write(BENCH_OUTFILE, TIMING_DATA, prefix_list=prefix_list)

if __name__ == "__main__":
    main()


# #!/usr/bin/env python

# import argparse
# import multiprocessing
# import os
# import subprocess
# from typing import List, Tuple

# import _load_profiles
# import _timing
# import numpy
# import comet_ml

# VERSION: str = "v1-2024-04-11-0"
# BENCH_OUTFILE: str = "./results/bench_comet.csv"
# BENCH_FIELDS: Tuple[str] = (
#     "test_name",
#     "test_profile",
#     "test_variant",
#     "client_version",
#     "client_type",
#     "server_version",
#     "server_type",
# )
# TIMING_DATA: List = []

# def get_comet_ml_version():
#     try:
#         result = subprocess.run(
#             ["pip", "show", "comet_ml"],
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#             text=True,
#             check=True
#         )
#         for line in result.stdout.split('\n'):
#             if line.startswith("Version:"):
#                 return line.split(":")[1].strip()
#         return "Version not found"
#     except subprocess.CalledProcessError as e:
#         print(f"An error occurred while trying to get comet_ml version: {e}")
#         return "Error"

# def run_one(args, n=0, m=0):
#     print(f"Running with mode: {args.mode}")  # Debugging statement
#     if args.mode == "online":
#         experiment = comet_ml.Experiment(project_name=args.project_name, workspace=args.workspace)
#     else:
#         experiment = comet_ml.OfflineExperiment(project_name=args.project_name, workspace=args.workspace)

#     for e in range(args.num_history):
#         d = {}
#         for i in range(args.history_floats):
#             d[f"f_{i}"] = float(n + m + e + i)
#         for i in range(args.history_ints):
#             d[f"n_{i}"] = n + m + e + i
#         for i in range(args.history_strings):
#             d[f"s_{i}"] = str(n + m + e + i)
#         for i in range(args.history_tables):
#             d[f"t_{i}"] = [[n + m, e, i, i + 1]]
#         for i in range(args.history_images):
#             d[f"i_{i}"] = numpy.random.randint(
#                 255,
#                 size=(args.history_images_dim, args.history_images_dim, 3),
#                 dtype=numpy.uint8,
#             )
#         experiment.log_metrics(d)

#     experiment.end()

# def run_sequential(args, m=0):
#     for n in range(args.num_sequential):
#         run_one(args, n, m)

# def run_parallel(args):
#     procs = []
#     for n in range(args.num_parallel):
#         p = multiprocessing.Process(
#             target=run_sequential, args=(args, n * args.num_parallel)
#         )
#         procs.append(p)
#     for p in procs:
#         p.start()
#     for p in procs:
#         p.join()

# def setup(args):
#     pass

# def teardown(args):
#     pass

# @_timing.timeit(TIMING_DATA)
# def time_load(args):
#     if args.num_parallel > 1:
#         run_parallel(args)
#     else:
#         run_sequential(args)

# def run_load(args):
#     setup(args)
#     time_load(args)
#     teardown(args)

# def main():
#     parser = argparse.ArgumentParser(description="benchmark comet performance")
#     parser.add_argument("--test_name", type=str, default="")
#     parser.add_argument(
#         "--mode", type=str, choices=("online", "offline"), default="offline"
#     )
#     parser.add_argument(
#         "--test_profile", type=str, default="", choices=list(_load_profiles.PROFILES)
#     )
#     parser.add_argument("--test_variant", type=str, default="")
#     parser.add_argument("--server_version", type=str, default="")
#     parser.add_argument("--server_type", type=str, default="")
#     parser.add_argument("--client_version", type=str, default=get_comet_ml_version())
#     parser.add_argument("--client_type", type=str, default="")
#     parser.add_argument("--num_sequential", type=int, default=1)
#     parser.add_argument("--num_parallel", type=int, default=1)
#     parser.add_argument("--num_history", type=int, default=1)
#     parser.add_argument("--history_floats", type=int, default=0)
#     parser.add_argument("--history_ints", type=int, default=0)
#     parser.add_argument("--history_strings", type=int, default=0)
#     parser.add_argument("--history_tables", type=int, default=0)
#     parser.add_argument("--history_images", type=int, default=0)
#     parser.add_argument("--history_images_dim", type=int, default=16)
#     parser.add_argument("--project_name", type=str, default="default_project")
#     parser.add_argument("--workspace", type=str, default="default_workspace")
#     parser.add_argument("--use-spawn", action="store_true")

#     args = parser.parse_args()
#     # required by golang experimental client when testing multiprocessing workloads
#     if args.use_spawn:
#         multiprocessing.set_start_method("spawn")

#     args_list = []
#     if args.test_profile:
#         args_list = _load_profiles.parse_profile(parser, args, copy_fields=BENCH_FIELDS)
#     else:
#         args_list.append(args)

#     for args in args_list:
#         print(f"Parsed arguments: {args}")  # Debugging statement
#         run_load(args)
#         prefix_list = [VERSION]
#         for field in BENCH_FIELDS:
#             prefix_list.append(getattr(args, field))


#         # Include additional test parameters
#         additional_params = [
#             "num_sequential",
#             "num_parallel",
#             "num_history",
#             "history_floats",
#             "history_ints",
#             "history_strings",
#             "history_tables",
#             "history_images",
#             "history_images_dim",
#         ]
#         for param in additional_params:
#             prefix_list.append(f"{param}={getattr(args, param)}")

#         _timing.write(BENCH_OUTFILE, TIMING_DATA, prefix_list=prefix_list)

# if __name__ == "__main__":
#     main()


#!/usr/bin/env python

import argparse
import multiprocessing
import os
import subprocess
from typing import List, Tuple

import _load_profiles
import _timing
import numpy as np
import pandas as pd
import comet_ml

VERSION: str = "v1-2024-04-11-0"
BENCH_OUTFILE: str = "./results/bench_comet.csv"
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


comet_ml.login()

def get_comet_ml_version():
    try:
        result = subprocess.run(
            ["pip", "show", "comet_ml"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        for line in result.stdout.split('\n'):
            if line.startswith("Version:"):
                return line.split(":")[1].strip()
        return "Version not found"
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while trying to get comet_ml version: {e}")
        return "Error"

def run_one(args, n=0, m=0):
    print(f"Running with mode: {args.mode}")  # Debugging statement

    if args.mode == "online":
        experiment = comet_ml.Experiment(project_name=args.project_name, workspace=args.workspace)
    else:
        experiment = comet_ml.OfflineExperiment(project_name=args.project_name, workspace=args.workspace)

    metrics_list = []
    tables_list = []
    images_list = []

    for e in range(args.num_history):
        metrics = {}
        for i in range(args.history_floats):
            metrics[f"f_{i}"] = float(n + m + e + i)
        for i in range(args.history_ints):
            metrics[f"n_{i}"] = n + m + e + i
        for i in range(args.history_strings):
            metrics[f"s_{i}"] = str(n + m + e + i)
        
        metrics_list.append(metrics)

        for i in range(args.history_tables):
            table_data = pd.DataFrame([[n + m, e, i, i + 1]], columns=["a", "b", "c", "d"])
            tables_list.append((f"table_{i}.csv", table_data))
        
        for i in range(args.history_images):
            image_data = np.random.randint(
                255,
                size=(args.history_images_dim, args.history_images_dim, 3),
                dtype=np.uint8,
            )
            images_list.append((f"image_{i}.png", image_data))

    # Log all collected data at the end
    for metrics in metrics_list:
        experiment.log_metrics(metrics)

    for table_name, table_data in tables_list:
        experiment.log_table(table_name, table_data)
        
    for image_name, image_data in images_list:
        experiment.log_image(
            image_data=image_data,
            name=image_name,
            image_format="png"
        )

    experiment.end()

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
    parser = argparse.ArgumentParser(description="benchmark comet performance")
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
    parser.add_argument("--client_version", type=str, default=get_comet_ml_version())
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
    parser.add_argument("--project_name", type=str, default="default_project")
    parser.add_argument("--workspace", type=str, default="default_workspace")
    parser.add_argument("--use-spawn", action="store_true")

    args = parser.parse_args()
    # required by golang experimental client when testing multiprocessing workloads
    if args.use_spawn:
        multiprocessing.set_start_method("spawn")

    args_list = []
    if args.test_profile:
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

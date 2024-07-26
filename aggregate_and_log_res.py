
# #!/usr/bin/env python

# import os
# import pandas as pd
# import wandb
# import matplotlib.pyplot as plt

# # Initialize WandB
# wandb.init(project="benchmark-comparisons")

# # Directory containing the benchmark CSV files
# csv_directory = "./results/"

# # List to hold dataframes for aggregation
# dataframes = []

# # Read all CSV files and concatenate into a single dataframe
# for filename in os.listdir(csv_directory):
#     if filename.startswith("bench_") and filename.endswith(".csv"):
#         framework_name = filename[len("bench_"):-len(".csv")]
#         filepath = os.path.join(csv_directory, filename)
        
#         # Read the entire CSV to ensure we can access the third and last columns
#         df = pd.read_csv(filepath, header=None)
        
#         # Extract the third and last columns
#         df = df.iloc[:, [2, -1]]
        
#         # Rename the columns for consistency
#         df.columns = ["test_profile", "duration"]
        
#         # Add the framework name as a column
#         df["framework"] = framework_name
        
#         dataframes.append(df)

# # Concatenate all dataframes
# all_data = pd.concat(dataframes, ignore_index=True)

# # Ensure the duration column is numeric
# all_data["duration"] = pd.to_numeric(all_data["duration"], errors='coerce')

# # Debugging: Print the first few rows to check the data
# print("Filtered data head:\n", all_data.head())

# # Group by test profile and framework
# grouped_data = all_data.groupby(['test_profile', 'framework'])['duration'].mean().unstack()

# # Plotting bar charts for each profile
# for profile in grouped_data.index:
#     plt.figure()
#     ax = grouped_data.loc[profile].plot(kind='bar', title=f"Profile: {profile}")
#     ax.set_xlabel("Framework")
#     ax.set_ylabel("Average Duration")
#     plt.xticks(rotation=45)
#     plt.tight_layout()

#     # Save the plot to a file
#     plot_filename = f"{profile}_benchmark.png"
#     plt.savefig(plot_filename)
#     plt.close()

#     # Log the plot to WandB
#     wandb.log({f"Benchmark: {profile}": wandb.Image(plot_filename)})

# print("Bar charts created and logged to WandB successfully.")


# #!/usr/bin/env python

# import os
# import pandas as pd
# import wandb
# import matplotlib.pyplot as plt

# # Initialize WandB
# wandb.init(project="benchmark-comparisons")

# # Directory containing the benchmark CSV files
# csv_directory = "./results/"

# # List to hold dataframes for aggregation
# dataframes = []

# # Read all CSV files and concatenate into a single dataframe
# for filename in os.listdir(csv_directory):
#     if filename.startswith("bench_") and filename.endswith(".csv"):
#         framework_name = filename[len("bench_"):-len(".csv")]
#         filepath = os.path.join(csv_directory, filename)
        
#         # Read the entire CSV to ensure we can access the third and last columns
#         df = pd.read_csv(filepath, header=None)
        
#         # Extract the third and last columns
#         df = df.iloc[:, [2, -1]]
        
#         # Rename the columns for consistency
#         df.columns = ["test_profile", "duration"]
        
#         # Add the framework name as a column
#         df["framework"] = framework_name
        
#         dataframes.append(df)

# # Concatenate all dataframes
# all_data = pd.concat(dataframes, ignore_index=True)

# # Ensure the duration column is numeric
# all_data["duration"] = pd.to_numeric(all_data["duration"], errors='coerce')

# # Debugging: Print the first few rows to check the data
# print("Filtered data head:\n", all_data.head())

# # Group by test profile and framework
# grouped_data = all_data.groupby(['test_profile', 'framework'])['duration'].mean().unstack()

# # Determine the appropriate unit for time
# if grouped_data.max().max() > 1:
#     time_unit = 's'
#     grouped_data = grouped_data
# else:
#     time_unit = 'ms'
#     grouped_data = grouped_data * 1000

# # Plotting bar charts for each profile
# for profile in grouped_data.index:
#     plt.figure()
#     ax = grouped_data.loc[profile].plot(kind='bar', title=f"Profile: {profile}")
#     ax.set_xlabel("Framework")
#     ax.set_ylabel(f"Average Duration ({time_unit})")
#     plt.xticks(rotation=45)
#     plt.tight_layout()

#     # Add the exact values on the bars
#     for i in ax.patches:
#         ax.annotate(f'{i.get_height():.2f}',
#                     (i.get_x() + i.get_width() / 2, i.get_height()),
#                     ha='center', va='baseline')

#     # Save the plot to a file
#     plot_filename = f"{profile}_benchmark.png"
#     plt.savefig(plot_filename)
#     plt.close()

#     # Log the plot to WandB
#     wandb.log({f"Benchmark: {profile}": wandb.Image(plot_filename)})

# print("Bar charts created and logged to WandB successfully.")


#!/usr/bin/env python

import os
import pandas as pd
import wandb
import matplotlib.pyplot as plt

# Initialize WandB
wandb.init(project="benchmark-comparisons")

# Directory containing the benchmark CSV files
csv_directory = "./results/"

# List to hold dataframes for aggregation
dataframes = []

# Read all CSV files and concatenate into a single dataframe
for filename in os.listdir(csv_directory):
    if filename.startswith("bench_") and filename.endswith(".csv"):
        framework_name = filename[len("bench_"):-len(".csv")]
        filepath = os.path.join(csv_directory, filename)
        
        # Read the entire CSV to ensure we can access the third and last columns
        df = pd.read_csv(filepath, header=None)
        
        # Extract the third and last columns
        df = df.iloc[:, [2, -1]]
        
        # Rename the columns for consistency
        df.columns = ["test_profile", "duration"]
        
        # Add the framework name as a column
        df["framework"] = framework_name
        
        dataframes.append(df)

# Concatenate all dataframes
all_data = pd.concat(dataframes, ignore_index=True)

# Ensure the duration column is numeric
all_data["duration"] = pd.to_numeric(all_data["duration"], errors='coerce')

# Debugging: Print the first few rows to check the data
print("Filtered data head:\n", all_data.head())

# Group by test profile and framework
grouped_data = all_data.groupby(['test_profile', 'framework'])['duration'].mean().unstack()

# Determine the appropriate unit for time
if grouped_data.max().max() > 1:
    time_unit = 's'
    grouped_data = grouped_data
else:
    time_unit = 'ms'
    grouped_data = grouped_data * 1000

# Get the 'v1-empty' times for each framework
empty_times = grouped_data.loc['v1-empty']

# Plotting bar charts for each profile
for profile in grouped_data.index:
    plt.figure()
    ax = grouped_data.loc[profile].plot(kind='bar', title=f"Profile: {profile}")
    ax.set_xlabel("Framework")
    ax.set_ylabel(f"Average Duration ({time_unit})")
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Add the exact values on the bars
    for i in ax.patches:
        ax.annotate(f'{i.get_height():.2f}',
                    (i.get_x() + i.get_width() / 2, i.get_height()),
                    ha='center', va='baseline')

    # Save the plot to a file
    plot_filename = f"{profile}_benchmark.png"
    plt.savefig(plot_filename)
    plt.close()

    # Log the plot to WandB
    wandb.log({f"Benchmark: {profile}": wandb.Image(plot_filename)})

    # Plot normalized chart
    normalized_data = grouped_data.loc[profile] - empty_times

    plt.figure()
    ax = normalized_data.plot(kind='bar', title=f"Profile: {profile} (Normalized)")
    ax.set_xlabel("Framework")
    ax.set_ylabel(f"Normalized Duration ({time_unit})")
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Add the exact values on the bars
    for i in ax.patches:
        ax.annotate(f'{i.get_height():.2f}',
                    (i.get_x() + i.get_width() / 2, i.get_height()),
                    ha='center', va='baseline')

    # Save the normalized plot to a file
    normalized_plot_filename = f"{profile}_benchmark_normalized.png"
    plt.savefig(normalized_plot_filename)
    plt.close()

    # Log the normalized plot to WandB
    wandb.log({f"Benchmark Normalized: {profile}": wandb.Image(normalized_plot_filename)})

print("Bar charts created and logged to WandB successfully.")

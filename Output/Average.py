import statistics
from os import path


text_output = "singularity_YoloOut.txt"



file_path = path.dirname(__file__) + "\\" + text_output
#file_path = "Docker_FaceOut.txt"  # Replace with the path to your text file

# Initialize dictionaries to store the field values
wait_times = []
recive_times = []
process_times = []
memory_values = []
cpu_values = []

try:
    with open(file_path, "r") as file:
        for line in file:
            #line = line.strip()  # Remove leading/trailing whitespace
            parts = line.split("-")  # Split the line by " - " delimiter

            # Extract the field values from the parts list
            wait_time = float(parts[1].strip().split()[1])
            recive_time  = float(parts[2].strip().split()[1])
            process_time = float(parts[3].strip().split()[1])
            memory = float(parts[5].strip().split()[1])
            cpu = float(parts[6].strip().split()[1])

            # Add the field values to the respective lists
            wait_times.append(wait_time)
            recive_times.append(recive_time)
            process_times.append(process_time)
            memory_values.append(memory)
            cpu_values.append(cpu)
except:
    print(f"{parts}")


# Calculate average, maximum, minimum, median, and mode for each field
averages = {
    "Wait Time": statistics.mean(wait_times),
    "Recive Time": statistics.mean(recive_times),
    "Process Time": statistics.mean(process_times),
    "Memory": statistics.mean(memory_values),
    "CPU": statistics.mean(cpu_values)
}

maximums = {
    "Wait Time": max(wait_times),
    "Recive Time": max(recive_times),
    "Process Time": max(process_times),
    "Memory": max(memory_values),
    "CPU": max(cpu_values)
}

minimums = {
    "Wait Time": min(wait_times),
    "Recive Time": min(recive_times),
    "Process Time": min(process_times),
    "Memory": min(memory_values),
    "CPU": min(cpu_values)
}

medians = {
    "Wait Time": statistics.median(wait_times),
    "Recive Time": statistics.median(recive_times),
    "Process Time": statistics.median(process_times),
    "Memory": statistics.median(memory_values),
    "CPU": statistics.median(cpu_values)
}

modes = {
    "Wait Time": statistics.mode(wait_times),
    "Recive Time": statistics.mode(recive_times),
    "Process Time": statistics.mode(process_times),
    "Memory": statistics.mode(memory_values),
    "CPU": statistics.mode(cpu_values)
}

standard_deviations = {
    "Wait Time": statistics.stdev(wait_times),
    "Recive Time": statistics.stdev(recive_times),
    "Process Time": statistics.stdev(process_times),
    "Memory": statistics.stdev(memory_values),
    "CPU": statistics.stdev(cpu_values)
}

# Print the results
print("Average Values:")
for field, value in averages.items():
    print(field + ":", value)

print("\nMedian Values:")
for field, value in medians.items():
    print(field + ":", value)

print("\nMode Values:")
for field, value in modes.items():
    print(field + ":", value)

print("\nMaximum Values:")
for field, value in maximums.items():
    print(field + ":", value)

print("\nMinimum Values:")
for field, value in minimums.items():
    print(field + ":", value)

print("\nStandard Deviation Values:")
for field, value in standard_deviations.items():
    print(field + ":", value)



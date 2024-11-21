# Sort and display the profiling data stored in vs.profiling

# The data can be sorted by:
# - "count": how many times a function was called
# - "average_time": how much time does the function take on average
# - "combined_time": how much time did the function take in total
SORT_BY = "count"

# The data can be filtered by origin:
# - If the origin is "", all the data is displayed
# - Possible origins include: "Environment", "Controller",
# "Runner", "CustomApp", "RestApi"
ORIGIN = ""

sorted_data = sorted(
    vs.profiling.items(), key=lambda item: item[1][SORT_BY], reverse=True
)

print(
    "\n\n".join(
        f"Function '{name}':\n {vs.dict_to_string(data, depth=2)}"
        for name, data in sorted_data
     	if data["class"].startswith(ORIGIN)
    )
)

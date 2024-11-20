# Sort and display the profiling data stored in vs.profiling

sorted_data = sorted(
    vs.profiling.items(),
    key=lambda x: x[1]['count'],
    reverse=True
)

print("\n\n".join(
	f"Function '{name}':\n"
    f"{vs.dict_to_string(data, depth=2)}"
  for name, data in sorted_data
))

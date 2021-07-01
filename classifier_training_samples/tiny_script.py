#!/usr/bin/env python3
import json

filenames = [
	"512D_ability_uses_sample.json",
	"512D_item_uses_sample.json",
	"512D_kills_log_sample.json",
	"512D_purchase_log_sample.json",
	"512D_runes_log_sample.json"
]

final_filename = "512D_all_sample.json"

total_rows = []

for filename in filenames:
	print(f"Reading {filename}...")
	with open(filename,'r') as f:
		rows = json.load(f)
		total_rows += rows
		
		
print(f"Saving to {final_filename}...")
with open(final_filename,'w') as f:
	json.dump(total_rows,f)
	

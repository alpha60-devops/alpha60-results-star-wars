#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import json
import sys
import os
from datetime import datetime, timedelta

# setup
inputdir = sys.argv[1];
if os.path.exists(inputdir):
    print(f"input data file '{inputdir}' found")
else:
    print(f"Error: input json file '{inputdir}' not found")
    sys.exit(1)

# Function to parse ISO week date
def iso_to_date(year, week, day=1):
    return datetime.strptime(f"{year}-W{week}-1", "%Y-W%W-%w")

# Load all files and extract 2024 data
media_objects_2024 = []

for file in os.listdir(inputdir):
    if file.endswith('.json'):
        with open(os.path.join(inputdir, file)) as f:
            data = json.load(f)

            # Extract metadata
            collection_name = data.get('collection-name')
            collection_id = data.get('collection-id')
            media_object_base = collection_name + " " + collection_id
            media_object = media_object_base.lower().replace(" ", "_").replace("the_", "")

            start_year = data.get('sample-year-start')
            start_day = data.get('sample-day-year-start')

            # Only process if it's in 2024
            if start_year == 2024:
                # Convert start day to date
                try:
                    start_date_p = datetime.strptime(f"{start_year} {start_day}", "%Y %j").date()
                    start_date = str(start_date_p)
                    print(f"{media_object} on {start_date}")
                except:
                    continue

                # Extract weekly data
                week_data = {}
                for week in data["collection-week"]:
                    week_num_raw = week['number']
                    week_nums = week_num_raw.replace("unique-btiha-week", "")
                    if week_nums:
                        week_num = int(week_nums.replace("-", ""))
                    else:
                        week_num = 0

                    upeers_total = week['upeers-total']
                    if upeers_total is not None:
                        week_date = start_date_p + timedelta(weeks=week_num)
                        week_data[week_num] = {
                            'date': week_date,
                            'upeers_total': upeers_total,
                            'media_object': media_object
                        }

                media_objects_2024.append({
                    'media_object': media_object,
                    'start_date': start_date,
                    'week_data': week_data
                })

print(media_objects_2024)


# Create a combined DataFrame for 2024
weekly_2024_data = []
for media in media_objects_2024:
    for week_num, week_info in media['week_data'].items():
        weekly_2024_data.append({
            'Collection': media['media_object'],
            'Week': week_num,
            'Date': week_info['date'],
            'UPeers Total': week_info['upeers_total'],
            'Year-Week': f"{week_info['date'].year}-W{week_info['date'].isocalendar().week:02d}"
        })

df_2024 = pd.DataFrame(weekly_2024_data)
print(df_2024)

# Plot 2024 data
plt.figure(figsize=(15, 8))

# Get unique collections for color coding
collections = df_2024['Collection'].unique()
colors = plt.cm.tab20(np.linspace(0, 1, len(collections)))

for collection, color in zip(collections, colors):
    collection_data = df_2024[df_2024['Collection'] == collection]
    plt.plot(collection_data['Date'],
             collection_data['UPeers Total'],
             label=collection,
             color=color,
             marker='o',
             linewidth=2)

plt.title('4. Year-by-Year Deep Dive: 2024 Weekly UPeers Total by Media Object', pad=20)
plt.xlabel('Week')
plt.ylabel('UPeers Total')
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(True, which='both', linestyle='--', linewidth=0.5)
plt.xticks(rotation=45)

# Highlight quarter boundaries
for quarter in range(1, 5):
    quarter_start = datetime(2024, (quarter-1)*3 + 1, 1)
    plt.axvline(x=quarter_start, color='gray', linestyle=':', alpha=0.5)
    plt.text(quarter_start, plt.ylim()[1]*0.95, f'Q{quarter}',
             ha='left', va='top', backgroundcolor='white')

plt.tight_layout()
plt.show()

# Additional analysis
print("\nAdditional 2024 Statistics:")
print(f"Number of media objects in 2024: {len(media_objects_2024)}")
print("\nPeak weeks for each collection:")
peak_weeks = df_2024.loc[df_2024.groupby('Collection')['UPeers Total'].idxmax()]
print(peak_weeks[['Collection', 'Year-Week', 'UPeers Total']].sort_values('UPeers Total', ascending=False))

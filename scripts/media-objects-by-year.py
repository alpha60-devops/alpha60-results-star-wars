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
    print(f"input data directory '{inputdir}' found")
else:
    print(f"Error: input json directory '{inputdir}' not found")
    sys.exit(1)

inputyear = sys.argv[2];
print(f"input year {inputyear}")


# Function to parse ISO week date
def iso_to_date(year, week, day=1):
    return datetime.strptime(f"{year}-W{week}-1", "%Y-W%W-%w")

# Load all files and extract year data
media_objects_year = []

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

            # Only process if it's in the right year
            if int(start_year) == int(inputyear):
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
                            'upeers_total': upeers_total
                        }

                media_objects_year.append({
                    'media_object': media_object,
                    'start_date': start_date,
                    'week_data': week_data
                })


# Create a combined DataFrame for year
weekly_data = []
for media in media_objects_year:
    for week_num, week_info in media['week_data'].items():
        if int(week_info['date'].year) == int(inputyear):
            weekly_data.append({
                'Collection': media['media_object'],
                'Week': week_num,
                'Date': week_info['date'],
                'Downloaders': week_info['upeers_total'],
                'Year-Week': f"{week_info['date'].year}-W{week_info['date'].isocalendar().week:02d}"
            })

df_year = pd.DataFrame(weekly_data)
print(df_year)

# Plot year data
plt.figure(figsize=(15, 8))

# Get unique collections for color coding
collections = df_year['Collection'].unique()
colors = plt.cm.tab20(np.linspace(0, 1, len(collections)))

for collection, color in zip(collections, colors):
    collection_data = df_year[df_year['Collection'] == collection]
    plt.plot(collection_data['Date'],
             collection_data['Downloaders'],
             label=collection,
             color=color,
             marker='o',
             linewidth=2)

gtitle = "Year " + inputyear + " Weekly Downloads by Media Object"    
plt.title(gtitle, pad=20)
plt.xlabel('Week')
plt.ylabel('Downloaders Total')
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(True, which='both', linestyle='--', linewidth=0.5)
plt.xticks(rotation=45)

# Highlight quarter boundaries
#for quarter in range(1, 5):
#    quarter_start = datetime(int(inputyear), (quarter-1)*3 + 1, 1)
#    plt.axvline(x=quarter_start, color='gray', linestyle=':', alpha=0.5)
#    plt.text(quarter_start, plt.ylim()[1]*0.95, f'Q{quarter}',
#             ha='left', va='top', backgroundcolor='white')

plt.tight_layout()
plt.show()

# Additional analysis
print("\nAdditional 2024 Statistics:")
print(f"Number of media objects in {inputyear}: {len(media_objects_year)}")
print("\nPeak weeks for each collection:")
peak_weeks = df_year.loc[df_year.groupby('Collection')['Downloaders'].idxmax()]
print(peak_weeks[['Collection', 'Year-Week', 'Downloaders']].sort_values('Downloaders', ascending=False))

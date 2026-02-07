"""
Memory-efficient preprocessing: process each ZIP file individually,
aggregate incrementally, and write compact JSON.

Usage:
    python scripts/preprocess.py --data-dir ./data/
"""
import pandas as pd
import zipfile
import os
import json
import glob
import argparse
from collections import defaultdict
import traceback
import gc

parser = argparse.ArgumentParser(description='Preprocess Bay Wheels trip data')
parser.add_argument('--data-dir', default='./data/', help='Directory containing ZIP/CSV files')
parser.add_argument('--output', default='./dashboard_data.json', help='Output JSON path')
args = parser.parse_args()

DATA_DIR = args.data_dir
WORK_DIR = os.path.dirname(args.output) or '.'

zip_files = sorted(glob.glob(os.path.join(DATA_DIR, "*.zip")))
print(f"Found {len(zip_files)} zip files")

# Incremental aggregators
monthly_agg = defaultdict(lambda: {'trips': 0, 'dur_sum': 0, 'sub': 0, 'cust': 0,
                                    'classic': 0, 'electric': 0, 'docked': 0, 'other': 0})
hourly_agg = defaultdict(lambda: {'trips': 0, 'dur_sum': 0, 'sub': 0, 'cust': 0})
dow_agg = defaultdict(lambda: {'trips': 0, 'dur_sum': 0, 'sub': 0, 'cust': 0})
station_depart = defaultdict(lambda: {'trips': 0, 'dur_sum': 0, 'sub': 0, 'cust': 0,
                                        'lat_sum': 0, 'lng_sum': 0, 'coord_count': 0})
station_arrive = defaultdict(int)
route_agg = defaultdict(lambda: {'trips': 0, 'dur_sum': 0})
station_monthly_agg = defaultdict(int)
yearly_agg = defaultdict(lambda: {'trips': 0, 'dur_sum': 0, 'start_stations': set(), 'end_stations': set()})
bike_type_agg = defaultdict(lambda: {'trips': 0, 'dur_sum': 0})
total_trips = 0
min_date = None
max_date = None

for idx, zf_path in enumerate(zip_files):
    try:
        with zipfile.ZipFile(zf_path, 'r') as z:
            csv_files = [f for f in z.namelist() if f.endswith('.csv') and '__MACOSX' not in f]
            for csv_name in csv_files:
                with z.open(csv_name) as f:
                    df = pd.read_csv(f, low_memory=False)

                    # Normalize columns
                    if 'started_at' in df.columns:
                        df = df.rename(columns={
                            'started_at': 'start_time', 'ended_at': 'end_time',
                            'start_lat': 'start_station_latitude', 'start_lng': 'start_station_longitude',
                            'end_lat': 'end_station_latitude', 'end_lng': 'end_station_longitude',
                            'member_casual': 'user_type',
                        })
                        df['user_type'] = df['user_type'].map({'member': 'Subscriber', 'casual': 'Customer'}).fillna('Unknown')
                        df['start_time'] = pd.to_datetime(df['start_time'], errors='coerce')
                        df['end_time'] = pd.to_datetime(df['end_time'], errors='coerce')
                        df['duration_sec'] = (df['end_time'] - df['start_time']).dt.total_seconds()
                        if 'rideable_type' not in df.columns:
                            df['rideable_type'] = 'unknown'
                    else:
                        df['start_time'] = pd.to_datetime(df['start_time'], errors='coerce')
                        df['end_time'] = pd.to_datetime(df['end_time'], errors='coerce')
                        df['rideable_type'] = 'classic_bike'

                    # Filter
                    df = df.dropna(subset=['start_time', 'start_station_latitude', 'start_station_longitude'])
                    df = df[(df['duration_sec'] > 0) & (df['duration_sec'] < 86400)]

                    n = len(df)
                    total_trips += n

                    # Date range
                    d_min = df['start_time'].min()
                    d_max = df['start_time'].max()
                    if min_date is None or d_min < min_date:
                        min_date = d_min
                    if max_date is None or d_max > max_date:
                        max_date = d_max

                    # Extract features
                    df['year_month'] = df['start_time'].dt.to_period('M').astype(str)
                    df['hour'] = df['start_time'].dt.hour
                    df['dow'] = df['start_time'].dt.dayofweek
                    df['year'] = df['start_time'].dt.year
                    df['is_sub'] = (df['user_type'] == 'Subscriber').astype(int)
                    df['is_cust'] = (df['user_type'] == 'Customer').astype(int)

                    # Monthly
                    for ym, grp in df.groupby('year_month'):
                        a = monthly_agg[ym]
                        a['trips'] += len(grp)
                        a['dur_sum'] += grp['duration_sec'].sum()
                        a['sub'] += grp['is_sub'].sum()
                        a['cust'] += grp['is_cust'].sum()
                        for bt in ['classic_bike', 'electric_bike', 'docked_bike']:
                            a[bt.split('_')[0]] += (grp['rideable_type'] == bt).sum()

                    # Hourly
                    for h, grp in df.groupby('hour'):
                        a = hourly_agg[h]
                        a['trips'] += len(grp)
                        a['dur_sum'] += grp['duration_sec'].sum()
                        a['sub'] += grp['is_sub'].sum()
                        a['cust'] += grp['is_cust'].sum()

                    # Day of week
                    for d, grp in df.groupby('dow'):
                        a = dow_agg[d]
                        a['trips'] += len(grp)
                        a['dur_sum'] += grp['duration_sec'].sum()
                        a['sub'] += grp['is_sub'].sum()
                        a['cust'] += grp['is_cust'].sum()

                    # Station departures
                    valid_start = df.dropna(subset=['start_station_name'])
                    for sname, grp in valid_start.groupby('start_station_name'):
                        a = station_depart[sname]
                        a['trips'] += len(grp)
                        a['dur_sum'] += grp['duration_sec'].sum()
                        a['sub'] += grp['is_sub'].sum()
                        a['cust'] += grp['is_cust'].sum()
                        a['lat_sum'] += grp['start_station_latitude'].sum()
                        a['lng_sum'] += grp['start_station_longitude'].sum()
                        a['coord_count'] += len(grp)

                    # Station arrivals
                    valid_end = df.dropna(subset=['end_station_name'])
                    for ename, cnt in valid_end['end_station_name'].value_counts().items():
                        station_arrive[ename] += cnt

                    # Top routes (only count, save memory)
                    valid_both = df.dropna(subset=['start_station_name', 'end_station_name'])
                    for (s, e), grp in valid_both.groupby(['start_station_name', 'end_station_name']):
                        r = route_agg[(s, e)]
                        r['trips'] += len(grp)
                        r['dur_sum'] += grp['duration_sec'].sum()

                    # Station monthly (all stations)
                    for (sname, ym), grp in valid_start.groupby(['start_station_name', 'year_month']):
                        station_monthly_agg[(sname, ym)] += len(grp)

                    # Yearly
                    for y, grp in df.groupby('year'):
                        a = yearly_agg[y]
                        a['trips'] += len(grp)
                        a['dur_sum'] += grp['duration_sec'].sum()
                        sn = grp['start_station_name'].dropna().unique()
                        en = grp['end_station_name'].dropna().unique() if 'end_station_name' in grp.columns else []
                        a['start_stations'].update(sn)
                        a['end_stations'].update(en)

                    # Bike type
                    for bt, grp in df.groupby('rideable_type'):
                        a = bike_type_agg[bt]
                        a['trips'] += len(grp)
                        a['dur_sum'] += grp['duration_sec'].sum()

                    print(f"  [{idx+1}/{len(zip_files)}] {csv_name}: {n:,} rows (total: {total_trips:,})")

                    del df
                    gc.collect()

    except Exception as e:
        print(f"  ERROR with {os.path.basename(zf_path)}: {e}")
        traceback.print_exc()

print(f"\nTotal trips processed: {total_trips:,}")

# ============================================================
# Build output dicts
# ============================================================
print("Building output...")

# Monthly
monthly_list = []
for ym in sorted(monthly_agg.keys()):
    a = monthly_agg[ym]
    monthly_list.append({
        'year_month': ym, 'total_trips': a['trips'],
        'avg_duration': round(a['dur_sum'] / a['trips'], 1) if a['trips'] > 0 else 0,
        'trips_Subscriber': a['sub'], 'trips_Customer': a['cust'],
        'bike_classic': a['classic'], 'bike_electric': a['electric'], 'bike_docked': a['docked'],
    })

# Hourly
hourly_list = []
for h in range(24):
    a = hourly_agg.get(h, {'trips': 0, 'dur_sum': 0, 'sub': 0, 'cust': 0})
    hourly_list.append({
        'hour': h, 'total_trips': a['trips'],
        'avg_duration': round(a['dur_sum'] / a['trips'], 1) if a['trips'] > 0 else 0,
        'trips_Subscriber': a['sub'], 'trips_Customer': a['cust'],
    })

# Day of week
dow_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
dow_list = []
for d in range(7):
    a = dow_agg.get(d, {'trips': 0, 'dur_sum': 0, 'sub': 0, 'cust': 0})
    dow_list.append({
        'day_of_week': d, 'day_name': dow_names[d], 'total_trips': a['trips'],
        'avg_duration': round(a['dur_sum'] / a['trips'], 1) if a['trips'] > 0 else 0,
        'trips_Subscriber': a['sub'], 'trips_Customer': a['cust'],
    })

# Stations
station_list = []
for sname, a in station_depart.items():
    if a['trips'] < 10:
        continue
    lat = a['lat_sum'] / a['coord_count']
    lng = a['lng_sum'] / a['coord_count']
    arrivals = station_arrive.get(sname, 0)
    station_list.append({
        'station_name': sname, 'lat': round(lat, 6), 'lng': round(lng, 6),
        'total_departures': a['trips'], 'total_arrivals': arrivals,
        'total_activity': a['trips'] + arrivals,
        'net_flow': arrivals - a['trips'],
        'avg_duration_depart': round(a['dur_sum'] / a['trips'], 1),
        'subscriber_departures': a['sub'], 'customer_departures': a['cust'],
        'subscriber_pct': round(a['sub'] / a['trips'] * 100, 1) if a['trips'] > 0 else 0,
    })

station_list.sort(key=lambda x: x['total_activity'], reverse=True)

# Top routes
route_list = sorted(route_agg.items(), key=lambda x: x[1]['trips'], reverse=True)[:100]
top_routes = []
for (s, e), v in route_list:
    top_routes.append({
        'start_station_name': s, 'end_station_name': e,
        'trip_count': v['trips'],
        'avg_duration': round(v['dur_sum'] / v['trips'], 1) if v['trips'] > 0 else 0,
    })

# Station monthly (top 50 stations only)
top50_names = set(s['station_name'] for s in station_list[:50])
station_monthly_list = []
for (sname, ym), cnt in station_monthly_agg.items():
    if sname in top50_names:
        station_monthly_list.append({'station_name': sname, 'year_month': ym, 'trips': cnt})

# Yearly
yearly_list = []
for y in sorted(yearly_agg.keys()):
    a = yearly_agg[y]
    if pd.isna(y):
        continue
    yearly_list.append({
        'year': int(y), 'total_trips': a['trips'],
        'avg_duration': round(a['dur_sum'] / a['trips'], 1) if a['trips'] > 0 else 0,
        'unique_stations': len(a['start_stations'] | a['end_stations']),
    })

# Bike type
bike_type_list = []
for bt, a in bike_type_agg.items():
    bike_type_list.append({
        'rideable_type': bt, 'total_trips': a['trips'],
        'avg_duration': round(a['dur_sum'] / a['trips'], 1) if a['trips'] > 0 else 0,
    })

# Summary
sub_trips = sum(a['sub'] for a in station_depart.values())
summary = {
    'total_trips': total_trips,
    'date_range_start': str(min_date.date()) if min_date else 'N/A',
    'date_range_end': str(max_date.date()) if max_date else 'N/A',
    'total_stations': len(station_list),
    'subscriber_pct': round(sub_trips / total_trips * 100, 1) if total_trips > 0 else 0,
}

output = {
    'summary': summary,
    'monthly': monthly_list,
    'stations': station_list,
    'hourly': hourly_list,
    'dow': dow_list,
    'top_routes': top_routes,
    'station_monthly': station_monthly_list,
    'yearly': yearly_list,
    'bike_type': bike_type_list,
}

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        import numpy as np
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)

out_path = args.output
with open(out_path, 'w') as f:
    json.dump(output, f, cls=NumpyEncoder)

file_size = os.path.getsize(out_path)
print(f"\nDone! JSON: {file_size / 1024 / 1024:.1f} MB")
print(f"Summary: {json.dumps(summary, indent=2)}")
print(f"Stations: {len(station_list)}, Monthly records: {len(monthly_list)}")

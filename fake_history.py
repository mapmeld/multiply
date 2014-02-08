# fake_history.py

import os, json
from datetime import datetime

# verify that .git has been removed
if os.path.exists('.git'):
    print "first remove .git to delete old history"
    quit()

# git init and set identity
os.system('git init')
config_file = open('.git/config', 'r')
original_config = config_file.read()
config_file.close()
os.system('git config user.name "Divvy"')
os.system('git config user.email "Divvy@example.org"')

# first commit with empty GeoJSON
gj = {
    "type": "FeatureCollection",
    "features": [ ]
}
suggested = open('stations.geojson', 'w')
suggested.write( json.dumps( gj ) )
suggested.close()
os.system('git add stations.geojson')
os.system('git commit -m "initial commit"')

# read CSV lines and sort
csv = open('divvy_suggestions_dump.csv', 'r')
reports = [ ]
while True:
    # read all reports in file
    report = csv.readline()
    if report.find(',') == -1:
        break
    reports.append( report )

# sort by timestamp
def report_time(report):
    timestamp_text = report.split(',')
    timestamp_text = timestamp_text[len(timestamp_text) - 2]
    timestamp = datetime.strptime(timestamp_text, "%m/%d/%Y %H:%M:%S")
    return timestamp
reports = sorted(reports, key=report_time)

# convert each to GeoJSON and make a commit at the given timestamp
first_report = 1
for report in reports:
    timestamp = report_time(report)
    split = report.split(',')
    end_extra = len(split[ len(split) - 1 ]) + len( split[ len(split) - 2 ] ) + 3
    report = report[5:(len(report) - end_extra)]

    # parse error helper
    rj = open('report.csv', 'w')
    rj.write(report)
    rj.close()

    api_json = json.loads(report)

    gj = {
        "type": "FeatureCollection",
        "features": [ ]
    }
    for station in api_json:
        if first_report == 1:
            id = station[0]
            votes = station[1]
            comment = station[2]
            lat = station[4]
            lng = station[5]
        else:
            id = station["id"]
            votes = station["s"]
            comment = station["d"]
            lat = station["lat"]
            lng = station["lng"]

        station_json = {
          "type": "Feature",
          "geometry": {
            "type": "Point",
            "coordinates": [ lng, lat ]
          },
          "properties": {
            "id": id,
            "votes": votes,
            "comment": comment
          }
        }
        gj["features"].append(station_json)

    first_report = 0

    suggested = open('stations.geojson', 'w')
    suggested.write( json.dumps( gj ) )
    suggested.close()
    os.system('git add stations.geojson')
    os.system("GIT_AUTHOR_DATE='" + str(timestamp) + "' GIT_COMMITTER_DATE='" + str(timestamp) + "' git commit -m 'Updated " + str(timestamp) + "'")

# restore original config
config_file = open('.git/config', 'w')
config_file.write(original_config)
config_file.close()
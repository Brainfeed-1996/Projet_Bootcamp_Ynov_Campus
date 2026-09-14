import csv
# Correct CSV: inner double quotes are doubled
csv_content = 'level,message,source,occurred_at,metadata\nERROR,Connection refused,api,2026-01-01T12:00:00Z,"{""req_id"": 123}"\nINFO,Startup complete,system,,\n'
print("CSV content:")
print(repr(csv_content))
print()
reader = csv.DictReader(csv_content.splitlines())
for i, row in enumerate(reader):
    print(f'Row {i}: {row}')
    print(f'  metadata: {repr(row.get("metadata"))}')
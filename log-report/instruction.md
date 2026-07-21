Read the Apache-style access log at /app/access.log and write a JSON summary to /app/report.json.

1. Write a valid JSON object containing exactly the fields total_requests, unique_ips, and top_path.
2. Set total_requests and unique_ips to integers and top_path to a string.
3. Set total_requests to the number of nonempty, valid log entries. Ignore empty or malformed lines.
4. Set unique_ips to the number of distinct client IP addresses across valid entries.
5. Set top_path to the most frequently requested URL path across valid entries. If multiple paths have the same highest count, choose the path that appears first in the log.

Do not modify /app/access.log.

You have 120 seconds to complete this task. Do not cheat by using online solutions or hints specific to this task.
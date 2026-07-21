Read the Apache-style access log at /app/access.log and write a JSON summary to /app/report.json.

1. Count each nonempty, valid log entry as one request.
2. Count the number of distinct client IP addresses across valid entries.
3. Identify the most frequently requested URL path.
4. If multiple paths have the same highest count, choose the one that appears first in the log.
5. Write a valid JSON object containing exactly:
    * total_requests: integer
    * unique_ips: integer
    * top_path: string
6. Ignore empty or malformed lines.
7. Do not modify /app/access.log.

You have 120 seconds to complete this task. Do not cheat by using online solutions or hints specific to this task.

from google.oauth2 import service_account
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Metric, Dimension
from datetime import datetime, timedelta

SERVICE_ACCOUNT_FILE = '/data/.openclaw/workspace/analytics/credentials/service-account.json'
PROPERTY_ID = 'G-43M8TD6CPF'  # Property ID: 527914409

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=['https://www.googleapis.com/auth/analytics.readonly']
)
client = BetaAnalyticsDataClient(credentials=credentials)

# Find numeric property ID from measurement ID
# The property ID is needed for API calls (not G-XXXXXXXXX)

request = RunReportRequest(
    property=f"properties/{PROPERTY_ID}",
    dimensions=[Dimension(name="pagePath")],
    metrics=[Metric(name="sessions"), Metric(name="activeUsers")],
    date_ranges=[DateRange(start_date="28daysAgo", end_date="today")],
)
response = client.run_report(request)
print(response)

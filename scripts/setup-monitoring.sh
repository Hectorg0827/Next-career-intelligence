#!/bin/bash
# NEXT Career Intelligence - Production Monitoring Setup
# Automated setup for GCP monitoring, alerts, and dashboards
#
# Prerequisites:
# - gcloud CLI installed and authenticated
# - Appropriate IAM permissions for monitoring
#
# Usage: ./scripts/setup-monitoring.sh

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
GCP_PROJECT_ID="${GCP_PROJECT_ID:-your-gcp-project-id}"
GCP_REGION="${GCP_REGION:-us-central1}"
SERVICE_NAME="${SERVICE_NAME:-next-backend}"
NOTIFICATION_EMAIL="${NOTIFICATION_EMAIL:-team@example.com}"

echo -e "${BLUE}=================================${NC}"
echo -e "${BLUE}NEXT Monitoring Setup${NC}"
echo -e "${BLUE}=================================${NC}"
echo ""

# Check prerequisites
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}Error: gcloud CLI not found${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Prerequisites met${NC}"
echo ""

# Step 1: Create notification channel
echo -e "${BLUE}Step 1/5: Creating notification channel...${NC}"

# Create email notification channel
CHANNEL_ID=$(gcloud alpha monitoring channels create \
  --display-name="Team Email" \
  --type=email \
  --channel-labels=email_address="$NOTIFICATION_EMAIL" \
  --project="$GCP_PROJECT_ID" \
  --format="value(name)" 2>/dev/null || echo "")

if [ -n "$CHANNEL_ID" ]; then
    echo -e "${GREEN}✓ Notification channel created: $CHANNEL_ID${NC}"
else
    echo -e "${YELLOW}⚠️  Notification channel may already exist${NC}"
    # Get existing channel
    CHANNEL_ID=$(gcloud alpha monitoring channels list \
      --filter="type=email AND labels.email_address=$NOTIFICATION_EMAIL" \
      --project="$GCP_PROJECT_ID" \
      --format="value(name)" \
      --limit=1)
    echo -e "${GREEN}✓ Using existing channel: $CHANNEL_ID${NC}"
fi
echo ""

# Step 2: Create uptime check
echo -e "${BLUE}Step 2/5: Creating uptime check...${NC}"

SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
  --region="$GCP_REGION" \
  --project="$GCP_PROJECT_ID" \
  --format="value(status.url)")

if [ -z "$SERVICE_URL" ]; then
    echo -e "${RED}Failed to get service URL${NC}"
    exit 1
fi

# Create uptime check configuration
cat > /tmp/uptime-check.yaml <<EOF
display_name: "NEXT Backend Health Check"
monitored_resource:
  type: "uptime_url"
  labels:
    project_id: "$GCP_PROJECT_ID"
    host: "$(echo $SERVICE_URL | sed 's|https://||')"
http_check:
  path: "/health"
  port: 443
  use_ssl: true
  validate_ssl: true
period: 60s
timeout: 10s
EOF

gcloud monitoring uptime create \
  --config-from-file=/tmp/uptime-check.yaml \
  --project="$GCP_PROJECT_ID" 2>/dev/null || echo -e "${YELLOW}⚠️  Uptime check may already exist${NC}"

echo -e "${GREEN}✓ Uptime check configured${NC}"
echo ""

# Step 3: Create alert policies
echo -e "${BLUE}Step 3/5: Creating alert policies...${NC}"

# High Error Rate Alert
cat > /tmp/error-rate-alert.json <<EOF
{
  "displayName": "High Error Rate (5xx) - Production",
  "conditions": [
    {
      "displayName": "5xx errors > 5%",
      "conditionThreshold": {
        "filter": "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"$SERVICE_NAME\" AND metric.type=\"run.googleapis.com/request_count\" AND metric.labels.response_code_class=\"5xx\"",
        "comparison": "COMPARISON_GT",
        "thresholdValue": 0.05,
        "duration": "60s",
        "aggregations": [
          {
            "alignmentPeriod": "60s",
            "perSeriesAligner": "ALIGN_RATE"
          }
        ]
      }
    }
  ],
  "combiner": "OR",
  "enabled": true,
  "notificationChannels": ["$CHANNEL_ID"],
  "alertStrategy": {
    "autoClose": "1800s"
  }
}
EOF

gcloud alpha monitoring policies create \
  --policy-from-file=/tmp/error-rate-alert.json \
  --project="$GCP_PROJECT_ID" 2>/dev/null || echo -e "${YELLOW}⚠️  Error rate alert may already exist${NC}"

# High Latency Alert
cat > /tmp/latency-alert.json <<EOF
{
  "displayName": "High Latency (P95 > 2s) - Production",
  "conditions": [
    {
      "displayName": "P95 latency > 2000ms",
      "conditionThreshold": {
        "filter": "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"$SERVICE_NAME\" AND metric.type=\"run.googleapis.com/request_latencies\"",
        "comparison": "COMPARISON_GT",
        "thresholdValue": 2000,
        "duration": "300s",
        "aggregations": [
          {
            "alignmentPeriod": "60s",
            "perSeriesAligner": "ALIGN_DELTA",
            "crossSeriesReducer": "REDUCE_PERCENTILE_95"
          }
        ]
      }
    }
  ],
  "combiner": "OR",
  "enabled": true,
  "notificationChannels": ["$CHANNEL_ID"]
}
EOF

gcloud alpha monitoring policies create \
  --policy-from-file=/tmp/latency-alert.json \
  --project="$GCP_PROJECT_ID" 2>/dev/null || echo -e "${YELLOW}⚠️  Latency alert may already exist${NC}"

# Uptime Check Alert
cat > /tmp/uptime-alert.json <<EOF
{
  "displayName": "Service Down - Production",
  "conditions": [
    {
      "displayName": "Uptime check failed",
      "conditionThreshold": {
        "filter": "resource.type=\"uptime_url\" AND metric.type=\"monitoring.googleapis.com/uptime_check/check_passed\"",
        "comparison": "COMPARISON_LT",
        "thresholdValue": 1,
        "duration": "120s"
      }
    }
  ],
  "combiner": "OR",
  "enabled": true,
  "notificationChannels": ["$CHANNEL_ID"]
}
EOF

gcloud alpha monitoring policies create \
  --policy-from-file=/tmp/uptime-alert.json \
  --project="$GCP_PROJECT_ID" 2>/dev/null || echo -e "${YELLOW}⚠️  Uptime alert may already exist${NC}"

echo -e "${GREEN}✓ Alert policies created${NC}"
echo ""

# Step 4: Create dashboard
echo -e "${BLUE}Step 4/5: Creating monitoring dashboard...${NC}"

cat > /tmp/dashboard.json <<EOF
{
  "displayName": "NEXT Production Dashboard",
  "mosaicLayout": {
    "columns": 12,
    "tiles": [
      {
        "width": 6,
        "height": 4,
        "widget": {
          "title": "Request Rate",
          "xyChart": {
            "dataSets": [
              {
                "timeSeriesQuery": {
                  "timeSeriesFilter": {
                    "filter": "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"$SERVICE_NAME\" AND metric.type=\"run.googleapis.com/request_count\"",
                    "aggregation": {
                      "alignmentPeriod": "60s",
                      "perSeriesAligner": "ALIGN_RATE"
                    }
                  }
                }
              }
            ]
          }
        }
      },
      {
        "xPos": 6,
        "width": 6,
        "height": 4,
        "widget": {
          "title": "P95 Latency",
          "xyChart": {
            "dataSets": [
              {
                "timeSeriesQuery": {
                  "timeSeriesFilter": {
                    "filter": "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"$SERVICE_NAME\" AND metric.type=\"run.googleapis.com/request_latencies\"",
                    "aggregation": {
                      "alignmentPeriod": "60s",
                      "perSeriesAligner": "ALIGN_DELTA",
                      "crossSeriesReducer": "REDUCE_PERCENTILE_95"
                    }
                  }
                }
              }
            ]
          }
        }
      },
      {
        "yPos": 4,
        "width": 6,
        "height": 4,
        "widget": {
          "title": "Error Rate",
          "xyChart": {
            "dataSets": [
              {
                "timeSeriesQuery": {
                  "timeSeriesFilter": {
                    "filter": "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"$SERVICE_NAME\" AND metric.type=\"run.googleapis.com/request_count\" AND metric.labels.response_code_class=\"5xx\"",
                    "aggregation": {
                      "alignmentPeriod": "60s",
                      "perSeriesAligner": "ALIGN_RATE"
                    }
                  }
                }
              }
            ]
          }
        }
      },
      {
        "xPos": 6,
        "yPos": 4,
        "width": 6,
        "height": 4,
        "widget": {
          "title": "Memory Usage",
          "xyChart": {
            "dataSets": [
              {
                "timeSeriesQuery": {
                  "timeSeriesFilter": {
                    "filter": "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"$SERVICE_NAME\" AND metric.type=\"run.googleapis.com/container/memory/utilizations\"",
                    "aggregation": {
                      "alignmentPeriod": "60s",
                      "perSeriesAligner": "ALIGN_MEAN"
                    }
                  }
                }
              }
            ]
          }
        }
      }
    ]
  }
}
EOF

gcloud monitoring dashboards create \
  --config-from-file=/tmp/dashboard.json \
  --project="$GCP_PROJECT_ID" 2>/dev/null || echo -e "${YELLOW}⚠️  Dashboard may already exist${NC}"

echo -e "${GREEN}✓ Dashboard created${NC}"
echo ""

# Step 5: Setup log-based metrics
echo -e "${BLUE}Step 5/5: Creating log-based metrics...${NC}"

# Create custom metrics for important events
gcloud logging metrics create user_signups \
  --description="Count of user signups" \
  --log-filter='resource.type="cloud_run_revision" AND jsonPayload.event="user_signup"' \
  --project="$GCP_PROJECT_ID" 2>/dev/null || echo -e "${YELLOW}⚠️  user_signups metric may already exist${NC}"

gcloud logging metrics create ai_analyses \
  --description="Count of AI career analyses" \
  --log-filter='resource.type="cloud_run_revision" AND jsonPayload.event="career_analysis"' \
  --project="$GCP_PROJECT_ID" 2>/dev/null || echo -e "${YELLOW}⚠️  ai_analyses metric may already exist${NC}"

echo -e "${GREEN}✓ Log-based metrics created${NC}"
echo ""

# Cleanup temporary files
rm -f /tmp/uptime-check.yaml /tmp/*-alert.json /tmp/dashboard.json

# Summary
echo -e "${BLUE}=================================${NC}"
echo -e "${GREEN}✓ Monitoring Setup Complete!${NC}"
echo -e "${BLUE}=================================${NC}"
echo ""
echo -e "${GREEN}Configured:${NC}"
echo "  ✓ Email notifications to: $NOTIFICATION_EMAIL"
echo "  ✓ Uptime checks every 60s"
echo "  ✓ 3 alert policies (errors, latency, uptime)"
echo "  ✓ Production dashboard"
echo "  ✓ Custom log-based metrics"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. View dashboard: https://console.cloud.google.com/monitoring/dashboards"
echo "2. Configure additional notification channels (Slack, PagerDuty)"
echo "3. Set up log exports for long-term analysis"
echo "4. Enable Error Reporting: https://console.cloud.google.com/errors"
echo ""
echo -e "${GREEN}Monitoring configured successfully! 📊${NC}"

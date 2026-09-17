"""Fictional, anonymized ResolveIQ demonstration records."""

from .models import HistoricalIncident, Runbook

_HISTORICAL = [
    ("HIST-001", "API gateway latency after release", "API requests slowed after a scheduled release.", "api", "network", ["high latency", "release"], ["api", "latency", "release"], "Checked gateway metrics and rolled back a routing change."),
    ("HIST-002", "Worker queue backlog", "Background jobs accumulated and processing fell behind.", "worker", "capacity", ["queue backlog", "slow processing"], ["queue", "worker", "capacity"], "Raised worker capacity after confirming a sustained queue increase."),
    ("HIST-003", "Application server unreachable", "The application endpoint timed out after a configuration update.", "application-server", "network", ["timeout", "unreachable"], ["network", "timeout", "application"], "Validated route tables and corrected a fictional routing entry."),
    ("HIST-004", "Database connection saturation", "Services could not obtain database connections during a traffic spike.", "database", "database", ["connection exhaustion", "errors"], ["database", "connections", "capacity"], "Reduced connection pressure and verified pool recovery."),
    ("HIST-005", "DNS lookup failures", "Several services could not resolve the internal application hostname.", "dns", "network", ["DNS failure", "lookup error"], ["dns", "network", "resolution"], "Corrected the fictional DNS record and flushed the test resolver cache."),
    ("HIST-006", "Object upload failures", "The document service returned errors while uploading demo objects.", "object-store", "storage", ["upload error", "5xx"], ["storage", "upload", "permissions"], "Verified bucket policy configuration and retried after correction."),
    ("HIST-007", "Container health check failures", "A service repeatedly failed its health check after deployment.", "container", "deployment", ["health check", "restart loop"], ["container", "health", "deployment"], "Compared health-check path and deployment configuration."),
    ("HIST-008", "Authentication token expiry", "Users were unexpectedly asked to sign in again.", "identity", "authentication", ["token expiry", "sign-in"], ["identity", "token", "session"], "Verified token lifetime configuration and refreshed test sessions."),
    ("HIST-009", "Metrics ingestion delay", "Monitoring charts lagged behind the generated test traffic.", "monitoring", "observability", ["metrics delay", "lag"], ["metrics", "monitoring", "ingestion"], "Checked ingestion queue depth and confirmed delayed events were processed."),
    ("HIST-010", "Scheduled job did not run", "A daily housekeeping job was absent from the execution history.", "scheduler", "scheduling", ["missing execution", "schedule"], ["scheduler", "job", "configuration"], "Validated the schedule expression and enabled the test schedule."),
    ("HIST-011", "TLS certificate warning", "The demo endpoint presented an expired certificate.", "web", "certificate", ["certificate expired", "TLS warning"], ["tls", "certificate", "web"], "Renewed the fictional certificate and verified the endpoint chain."),
    ("HIST-012", "Cache hit rate dropped", "Read latency increased when cache hit rate declined.", "cache", "performance", ["low hit rate", "latency"], ["cache", "performance", "latency"], "Reviewed cache key changes and restored the expected key format."),
    ("HIST-013", "Application logs missing", "Expected application entries were not visible in the log stream.", "logging", "observability", ["missing logs", "log stream"], ["logging", "observability", "configuration"], "Checked log level and destination settings in the demo service."),
    ("HIST-014", "Application server timeout", "Application became unreachable after a deployment.", "application-server", "network", ["connection timeout", "application unreachable"], ["ec2", "network", "timeout"], "Validated network connectivity and corrected routing configuration."),
    ("HIST-015", "Read replica lag", "Reports showed stale data during a reporting window.", "database", "database", ["replica lag", "stale reads"], ["database", "replica", "lag"], "Reviewed replica load and waited for replication to catch up."),
    ("HIST-016", "Service configuration mismatch", "A service started with an outdated endpoint value.", "configuration", "configuration", ["wrong endpoint", "startup error"], ["configuration", "endpoint", "startup"], "Compared deployment configuration with the documented demo endpoint."),
    ("HIST-017", "Load balancer target unhealthy", "Traffic was not reaching one of the application targets.", "load-balancer", "network", ["unhealthy target", "failed probe"], ["load-balancer", "health", "network"], "Checked target health path and corrected the application listener."),
    ("HIST-018", "Memory pressure on worker", "A worker slowed down as memory usage approached its limit.", "worker", "capacity", ["memory pressure", "slow worker"], ["worker", "memory", "capacity"], "Reduced batch size and confirmed stable memory use."),
    ("HIST-019", "Message visibility timeout", "Messages were processed more than once by a worker.", "queue", "messaging", ["duplicate processing", "visibility timeout"], ["queue", "messaging", "timeout"], "Aligned processing duration and queue visibility settings."),
    ("HIST-020", "Firewall rule blocked callback", "An approved demo callback could not reach the service.", "network", "security", ["blocked callback", "connection refused"], ["firewall", "network", "callback"], "Reviewed the fictional allow rule and tested the callback path."),
    ("HIST-021", "Unexpected deployment version", "The running service did not match the intended demo release.", "deployment", "deployment", ["version mismatch", "release"], ["deployment", "version", "release"], "Compared deployment metadata and redeployed the intended version."),
    ("HIST-022", "Database schema check failed", "The service rejected requests after a schema change.", "database", "database", ["schema mismatch", "request error"], ["database", "schema", "migration"], "Validated migration order and applied the missing demo migration."),
    ("HIST-023", "Frontend asset delivery slow", "Static assets loaded slowly from the demo endpoint.", "web", "performance", ["slow assets", "latency"], ["web", "assets", "performance"], "Checked cache headers and confirmed compressed asset delivery."),
    ("HIST-024", "Alert threshold too sensitive", "A normal traffic pattern generated repeated alerts.", "monitoring", "observability", ["false alert", "threshold"], ["monitoring", "alert", "threshold"], "Compared the threshold with the fictional baseline and adjusted it."),
]


def historical_incidents() -> list[HistoricalIncident]:
    return [
        HistoricalIncident(
            incident_id=incident_id,
            title=title,
            description=description,
            environment="fictional-demo",
            service=service,
            category=category,
            symptoms=symptoms,
            resolution=resolution,
            tags=tags,
            created_at=f"2026-08-{index + 1:02d}T10:00:00Z",
        )
        for index, (incident_id, title, description, service, category, symptoms, tags, resolution) in enumerate(_HISTORICAL)
    ]


def curated_runbooks() -> list[Runbook]:
    common = ["Confirm the affected demo service and incident scope."]
    return [
        Runbook("RB-001", "Application connectivity troubleshooting", "A demo application endpoint cannot be reached.", common, ["Check DNS resolution.", "Check network path and listener health.", "Check application service status."], ["Confirm the endpoint responds successfully."], ["Apply an approved configuration correction after verification."], ["Escalate to the platform team if connectivity remains unavailable."], created_at="2026-08-25T10:00:00Z"),
        Runbook("RB-002", "Database connection troubleshooting", "A service cannot connect reliably to the demo database.", common, ["Check connection pool usage.", "Check database availability.", "Review recent schema or configuration changes."], ["Run a read-only connectivity check."], ["Apply an approved pool or configuration change after verification."], ["Escalate to the database team if errors continue."], created_at="2026-08-26T10:00:00Z"),
        Runbook("RB-003", "Queue backlog troubleshooting", "A demo worker queue is growing faster than it is processed.", common, ["Inspect queue depth.", "Check worker health and capacity.", "Review processing errors."], ["Confirm queue depth returns toward baseline."], ["Adjust approved worker capacity after review."], ["Escalate to the service owner if backlog persists."], created_at="2026-08-27T10:00:00Z"),
        Runbook("RB-004", "Deployment verification", "A demo service is unhealthy or running an unexpected version.", common, ["Review deployment version.", "Check health-check configuration.", "Inspect recent deployment events."], ["Confirm the intended version is healthy."], ["Use the approved rollback or redeployment procedure."], ["Escalate to release engineering if the version remains incorrect."], created_at="2026-08-28T10:00:00Z"),
        Runbook("RB-005", "DNS resolution troubleshooting", "A demo hostname does not resolve as expected.", common, ["Check the expected DNS record.", "Test resolution from the affected network.", "Check resolver health."], ["Confirm the hostname resolves to the expected demo address."], ["Apply an approved DNS record correction."], ["Escalate to the network team if resolution remains broken."], created_at="2026-08-29T10:00:00Z"),
        Runbook("RB-006", "Monitoring signal troubleshooting", "Demo metrics, logs, or alerts are delayed or unexpected.", common, ["Check ingestion status.", "Review log and metric configuration.", "Compare the signal with the demo baseline."], ["Confirm new signals arrive within the expected window."], ["Apply an approved threshold or configuration adjustment."], ["Escalate to observability support if signals remain unreliable."], created_at="2026-08-30T10:00:00Z"),
        Runbook("RB-007", "Storage upload troubleshooting", "A demo service cannot upload an object.", common, ["Check request and object size.", "Review storage policy configuration.", "Check service error logs."], ["Confirm a test object can be uploaded and read."], ["Apply an approved policy or configuration correction."], ["Escalate to the storage team if uploads continue to fail."], created_at="2026-08-31T10:00:00Z"),
    ]

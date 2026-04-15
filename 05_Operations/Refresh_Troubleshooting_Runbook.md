// Pseudocode: Refresh Troubleshooting Runbook (Top Failure Modes)

DEFINE RefreshTroubleshooting:

    FAILUREMODE CredentialErrors:
        Symptoms:
            - "Scheduled refresh failed"
        Fix:
            - Re-enter data source credentials in dataset settings
            - Confirm MFA rules OR service account configuration

    FAILUREMODE GatewayOffline:
        Symptoms:
            - "Gateway unreachable"
        Fix:
            - Confirm gateway service is running
            - Confirm network access available
            - Rebind dataset to gateway cluster if applicable

    FAILUREMODE SourceFileChanged:
        Symptoms:
            - Column not found
            - Type mismatch
        Fix:
            - Enforce naming + header rules
            - Use Power Query steps tolerant of extra columns
            - Apply Change Control when schema changes occur

    FAILUREMODE DatasetSizeOrTimeouts:
        Symptoms:
            - Refresh duration spikes
            - Refresh fails due to timeout
        Fix:
            - Reduce columns
            - Filter early in Power Query
            - Apply incremental refresh (only if needed)

    FAILUREMODE PermissionsOrWorkspaceIssues:
        Symptoms:
            - Users cannot see report/app
        Fix:
            - Prefer app-level permissions
            - Avoid per-item sharing
            - Maintain viewer list in writing

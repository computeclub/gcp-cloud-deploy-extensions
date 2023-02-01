# release-auto-promoter

Automatically promote releases when a rollout succeeds. Approvals are still
required if the pipeline stage requires it.

## User story

As an engineer, I want successful releases to be automatically promoted in my CI/CD
pipeline until a terminal stage is reached (production) or approval is required
for a stage.

## Configuration schema

`enabled` - a boolean that enables or disables the notifier. If not present the notifier is disabled.

Example:

```json
{
    "enabled": true
}
```

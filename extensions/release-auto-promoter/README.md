# release-auto-promoter

Automatically promote releases when a rollout succeeds. Approvals are still
required if the pipeline stage requires it.

## User story

As an engineer, I want successful releases to be automatically promoted in my CI/CD
pipeline until a terminal stage is reached (production) or approval is required
for a stage.

## Configuration schema

`enabled` - a boolean that enables or disables the extension. If not present the extension is disabled.

Example:

```json
{
    "enabled": true
}
```

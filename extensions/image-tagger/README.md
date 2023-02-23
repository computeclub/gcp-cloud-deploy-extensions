# image-tagger

A Cloud Depoloy extension to tag images following successful rollout operations.

## User story

As an engineer, I want a successful rollout to an environment target to result
in tags being added to the successfully deployed container image in a registry.
A moving tag of `<ENV>-current` gives an at-a-glance view of what is currently
deployed where when looking at a list of images in the registry. Likewise, tags
having `<ENV>-<SHORT_DIGEST>` provide a historical record of what was previously
deployed successfully to a target.

## Configuration schema

`enabled` - a boolean that enables or disables the extension. If not present the extension is disabled.
`tag_templates`- the set of tag templates to apply to all successful deployments.

Example:

```json
{
    "enabled": true,
    "tag_templates": [
        "${ENVIRONMENT}-current",
        "${ENVIRONMENT}-${SHORT_DIGEST}",
        "${ENVIRONMENT}-${FULL_DIGEST}"
    ]
}
```

## Specifying template variable values

Tag template variable values (e.g. ${ENVIRONMENT} above) are fetched from
the annotations of the deployment target. If not found, the tag with a missing
value will not be applied to the container image and a log message will be
emitted.

## Built-in template variable values

Certain template variable values are always available and can't be overridden by
target labels. For now those are:

`SHORT_DIGEST` - the annotated 12 byte hash of the container image.
`FULL_DIGEST` - the full 40 byte hash of the container image.

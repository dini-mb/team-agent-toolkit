---
name: aws-cli
description: 'Use for read-only AWS CLI tasks and permission dry-runs. Select the -agent profile matching the active task and always pass --profile explicitly; never fall back to admin or perform real writes.'
---

# AWS CLI

## Select

1. Establish the active task's project, account, and environment from the user, approved ticket, or repository configuration, not terminal state or earlier tasks.
2. Read `AWS_CONFIG_FILE` or `~/.aws/config`; discover profiles ending exactly in `-agent`. Match names, account, role, and region. Inspect `credential_process` and its source profile/script if needed, without executing the script directly or exposing credentials.
3. Ask before AWS requests if the task is unspecified, configuration is missing, or no single profile matches. One configured profile alone does not establish a match. Reevaluate when the task or configuration changes.

## Execute

- State the profile and operation; pass `--profile <selected-agent-profile>` on every AWS invocation, including chains, pipelines, and wrappers. Never rely on `asp`, environment-selected profiles, or defaults: the agent terminal is separate.
- Use the profile's region; pass `--region` when the task requires a confirmed region. An availability zone does not select the CLI region.
- Verify the task's account and role with `sts get-caller-identity` using the selected profile before relying on account-specific results; stop on mismatch.
- Run only read-only calls or documented permission dry-runs; never perform real writes under this skill, even if separately authorised. Stop and explain that write requests are outside its scope. Preserve existing hooks and task restrictions, including Terraform/deployment restrictions.
- Permission tests must use documented, service-supported `--dry-run`; never remove it or create real test resources instead.
- Never fall back to non-agent/admin profiles, inject credentials, bypass session policies, or expose keys, tokens, or credential-process JSON.

## Handle Results

- On permission-denied errors, stop and report the denied action, profile, and reason. Do not retry with other profiles, credentials, commands, or APIs to achieve the same operation. Further diagnosis requires an explicit user request and remains subject to the read-only and no-bypass rules above.
- Stop on missing credentials or configuration; explain the blocker without switching profiles. For expired source SSO, identify the session and ask the user to renew it in their terminal/browser. Do not use source admin credentials for service calls or edit authentication configuration without permission.
- EC2 `UnauthorizedOperation` means denied; `DryRunOperation` means permitted but not performed. Other errors are inconclusive. One denial does not prove all writes are blocked.
- Report profile, region, outcome, and read-only/dry-run status.

The deny hook requires an explicit `--profile` ending in `-agent` on each visible AWS command, including chains; omitted profiles are denied regardless of environment selection. IAM/session policies enforce permissions; the suffix is only a convention. Hooks do not cover manual terminals or hidden script calls, and skills are not a sandbox.
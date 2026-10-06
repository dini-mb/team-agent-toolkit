# Team Agent Toolkit

Shared Copilot skills, instructions, hooks, MCP configuration, and read-only AWS tooling.

## Capabilities

- `aws-cli`: choose a task-matched `-agent` profile for read-only AWS work and permission dry-runs.
- `work-on-jira-task`: inspect tickets, prepare branches, and implement approved changes.
- `create-pr`: prepare and publish PRs with the shared template and verified checks.
- `update-jira-task`: post authorised progress and PR updates to the supplied ticket.
- Atlassian MCP: access Jira and Confluence tools through the hosted server, subject to client sign-in and user permissions.
- Hooks: require explicit `-agent` profiles for visible AWS commands and block Terraform `apply` and `destroy`.

## Repository layout

```text
team-agent-toolkit/
|-- README.md
|-- .gitignore
|-- instructions/
|   `-- copilot-instructions.md
|-- install.sh
|-- aws/
|   |-- config
|   `-- readonly-agent.sh
|-- hooks/
|   |-- aws-profile-safety.json
|   |-- deny-aws-non-agent-profile.py
|   |-- terraform-safety.json
|   `-- deny-terraform-deploy.py
|-- mcp/
|   `-- config.json
|-- skills/
|   |-- aws-cli/SKILL.md
|   |-- create-pr/SKILL.md
|   |-- update-jira-task/SKILL.md
|   `-- work-on-jira-task/SKILL.md
`-- tests/
	|-- __init__.py
	`-- test_hooks.py
```

## Setup

From the repository directory, run:

```sh
chmod +x install.sh
./install.sh
```

The installer puts skills, instructions, and hooks under `~/.copilot`, and the credential helper under `~/.aws`. It does not install or change MCP configuration.

In VS Code, select the Local session target and confirm skills and hooks appear in Chat. The installed `~/.copilot/copilot-instructions.md` applies to Copilot Agent Host sessions.

## Atlassian MCP setup

1. Press F1 and run `MCP: Open Remote User Configuration`.
2. Copy the Atlassian server entry from `mcp/config.json` into the `servers` object in the remote configuration. Merge it with existing entries; do not replace the whole configuration.
3. Open MCP Servers in the agent customisation UI and start the Atlassian server.
4. Complete Atlassian sign-in when prompted and grant only the permissions required for your workflow.

## AWS config

The installer does not modify `~/.aws/config`. Review the sanitised `aws/config.example`, then add its sections to your existing config. Replace every placeholder with values from your AWS IAM Identity Center and account setup; do not replace the whole config.

```ini
[sso-session <org>-sso]
sso_start_url = https://d-<directory-id>.awsapps.com/start
sso_region = ap-southeast-2

[profile <project>-nonprod-admin]
sso_session = <org>-sso
sso_account_id = <account-id>
sso_role_name = sso-admin
region = ap-southeast-2

[profile <project>-nonprod-agent]
credential_process = /home/<wsl-user>/.aws/readonly-agent.sh <project>-nonprod-admin arn:aws:iam::<account-id>:role/sso-admin
region = ap-southeast-2
```

Replace `<org>`, `<project>`, `<directory-id>`, `<account-id>`, and `<wsl-user>` with your values before adding these sections to `~/.aws/config`. The `-agent` profile uses the source SSO profile to assume the target role with the AWS managed `ReadOnlyAccess` session policy. The target role must trust the source identity and grant the required access; the session policy only limits permissions granted by that role.

Install AWS CLI v2 and `jq`. From your own terminal, start device-code sign-in for the source profile with:

```sh
aws sso login --use-device-code --no-browser --profile <project>-nonprod-admin
```

Then check the agent profile with `aws sts get-caller-identity --profile <project>-nonprod-agent`. Use an agent profile ending in `-agent` for AWS CLI commands issued by Copilot.

## Guardrails and tests

The AWS hook blocks visible AWS CLI commands that omit `--profile` or use a profile without the `-agent` suffix. The Terraform hook blocks visible `terraform apply` and `terraform destroy` commands. Hooks do not cover manual terminal commands or AWS and Terraform calls hidden inside scripts; IAM policies remain the permissions boundary.

Run the simulated hook tests with:

```sh
python3 -m unittest discover -s tests -v
```

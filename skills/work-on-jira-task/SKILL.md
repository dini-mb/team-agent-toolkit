---
name: work-on-jira-task
description: 'Start or continue a Jira task: read the ticket and prepare a feature/fix branch, pause for implementation direction on ticket-only requests, or implement supplied changes. Reuse the task branch and deliver only the agreed scope, with Jira-prefixed commits and PR/Jira updates when requested.'
---

# Work on a Jira Task

## Entry Points
- **Ticket only** ("start working on JIRA-ID"): read the ticket and prepare the branch, then summarise scope and ask whether to implement. Stop without code edits, staging, or committing, even if the ticket describes a solution.
- **Ticket plus change instructions**: reconcile the user's details with the ticket, prepare the branch, then implement clearly requested changes. Ask only if scope is unclear or conflicting. An explicit request to implement the ticket also authorises implementation.
- Respect narrower endpoints: planning only, branch preparation only, editing without committing, or drafting messages. Updating customisations alone does not authorise application-repository Git operations.

## Prepare
1. Obtain the current Jira ID if missing; read the ticket with the Jira tool. Confirm repository, scope, and delivery endpoint from the request; ask when unclear. Ask `feature` or `fix` unless specified. Read repository instructions and relevant domain skills.
2. Inspect the active branch, staged/unstaged changes, and conflicts. Stop on conflicts or uncommitted changes that would carry between branches or block preparation; never automatically stash, reset, discard, or force checkout.
3. Preserve an existing user-created task branch. Otherwise check out `main`, run `git pull --ff-only`, and create `feature/` or `fix/` plus lowercase kebab-case Jira ID and description (for example `feature/jira-1234-stg-infra`). Stop on existing branch names, failed Git operations, divergence, or conflicts; never replace branches or auto-merge/rebase/resolve.
4. For ticket-only or preparation-only requests, report the branch and proposed scope, then stop for implementation direction.

## Implement and Deliver
1. Continue as the user approves changes in chat. Reuse the confirmed ticket and prepared branch; inspect the current worktree without repeating main checkout, pull, or branch creation. Reconfirm only changed or unclear scope. Preserve unrelated work and repository conventions.
2. Implement approved changes and self-review the diff and relevant evidence. Update relevant living domain documentation with actual decisions, results, and blockers. Leave local builds and Terraform checks to pipelines; read-only review is not successful CI validation.
3. Stage/commit only when the agreed implementation scope is complete and the delivery endpoint includes committing. Review the index; stage only approved files, never blanket `git add .`. If unrelated staged changes would enter the commit, stop and ask rather than unstage or include them.
4. Inspect commit hooks; stop if they run prohibited builds/Terraform, without bypassing them. Use the message format below and confirm Jira-prefix mismatches. Stop on commit failure; do not amend, force, bypass hooks, or rewrite history without explicit authorisation. Inspect and report the resulting commit.
5. Push/create PRs only when requested or included in the agreed endpoint, using [the PR skill](../create-pr/SKILL.md); PR titles use conventional-commit syntax. A commit request alone does not authorise publishing. For requested Jira updates, use [the Jira update skill](../update-jira-task/SKILL.md), keep comments compact, and report write-access blockers accurately.

## Commit Message

```text
<JIRA-ID>: <Title>

<Description of what changed and why.>
<Actual verification and pending pipeline checks, where relevant.>
```

## Guardrails
- All local builds and Terraform commands are prohibited, including fmt/init/validate/plan/apply/destroy/import/state. Preserve task-specific constraints.
- No deployments, deployment-pipeline triggers, or AWS mutations without explicit authorisation; a PR is not deployment authorisation.
- Modify only the user-supplied Jira ticket for the authorised action; other tickets may be read, not modified.

## Verification
Verify against the agreed endpoint. Preparation-only success is the intended branch ready with scope summarised; no implementation or commit is required. For implementation, report approved changes and actual checks/blockers. Verify any requested commit contains only approved changes and the correct Jira prefix; confirm requested PR/Jira delivery through their tools or report blockers. Do not claim unfinished stages are complete.
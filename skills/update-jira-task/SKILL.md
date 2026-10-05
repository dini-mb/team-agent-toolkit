---
name: update-jira-task
description: 'Post compact Jira progress or completion comments for an approved task, including actual changes, PR links, verification, and blockers. Use when asked to update a Jira ticket or comment after implementation or PR creation.'
---

# Update a Jira Task

## When to Use
Use when authorised to post a progress, completion, or PR update to Jira. This skill does not authorise changing ticket status, assignee, or description.

## Authorised Ticket Boundary
Only modify the Jira issue ID explicitly supplied by the user for the current task, and only perform the requested action. Other Jira issues may be searched and read for context, but must not be modified. Related issues, parent tickets, epics, dependencies, or tickets mentioned in comments do not inherit permission.

This restriction applies to every Jira write, including comments, fields, status transitions, assignments, attachments, worklogs, links, and deletions. Do not use bulk operations or actions that also modify unapproved tickets. If another ticket needs a change, first ask the user for its ID and explicit authorisation. Reading a ticket or discovering its ID is not write permission.

## Procedure
1. Ask for the Jira ID unless already supplied for the current task. Read the ticket using the Jira tool to confirm identity and scope.
2. Read relevant recent comments to avoid duplicate updates. Respect comment visibility; do not copy restricted content into a broader audience.
3. Draft a compact comment of a few sentences: what changed, the actual PR link if one exists, verified checks or pending pipeline validation, and any material blocker. Do not include a full PR body or unverified claims.
4. Use the Jira comment tool or discover the exact comment-writing operation before calling the corresponding write tool. Reuse the session's site ID. Before every write, verify that the target issue (including the owning issue of a comment or attachment) resolves to the user-provided Jira ID. Stop if the target differs or cannot be confirmed; do not substitute a related issue. Never guess an operation name or bypass read-only access through another API.
5. If write access or the operation is unavailable, stop the posting attempt, report the blocker, and provide the prepared compact comment. Do not claim that Jira was updated. On ambiguous write results, check comments before retrying to avoid duplicates.
6. Confirm successful posting from the tool response and report the ticket or comment link. Leave ticket status and other fields unchanged unless requested.

## Comment Pattern

```text
<Concise outcome and scope>. PR: <actual URL, only if created>.
<Actual verification or pending pipeline checks>. <Material blocker, if any>.
```

## Guardrails
- Keep comments compact and exclude credentials, state, tokens, and secrets.
- Do not run builds, Terraform commands, or deployments to produce an update.
- Distinguish prepared code, a published PR, merged code, and deployed resources.

## Verification
Only the user-provided ticket received the authorised update, confirmed by the tool; no other tickets were modified. Otherwise, the user was told why posting was unavailable and given the draft instead.
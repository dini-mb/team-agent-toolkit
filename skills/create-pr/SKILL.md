---
name: "create-pr"
description: "Create GitHub pull requests using the embedded pull-request body template. Use when preparing or creating a PR with a conventional-commit title, a prose body heading, and truthful checklist results."
---

# Create a GitHub Pull Request

## When to Use
Use when creating a GitHub pull request, unless the user provides a different PR body or the checked-out repository has a mandatory template that differs from the embedded template. Preparing a body does not authorise publishing a PR.

## Procedure
1. Confirm the target repository, head branch, and authorisation to create the PR. Inspect existing PRs to avoid duplicates. Do not create a branch, commit, push, or trigger deployment without authorisation. If implementation, branch preparation, or committing is still needed, use [the Jira task workflow](../work-on-jira-task/SKILL.md) first.
2. Determine the PR base branch, a conventional-commit PR title, and a prose body title from the user's request and the implemented changes. Format the PR title as `type(scope): description` (scope optional), for example `fix(auth): reject expired tokens`. Use a concise prose heading for the body `## <Title>`, for example `Reject expired tokens`; do not put conventional-commit syntax in that body heading.
3. Start with the embedded template below as the complete PR body. Preserve its headings, field labels, and checkbox wording.
4. Replace every relevant placeholder with accurate information from the implemented changes. Include required dependencies in the description. Write `Not applicable.` for optional fields that do not apply. Do not invent screenshots, issue links, Jira links, or validation results.
5. Select the applicable type-of-change checkbox. Complete checklist items truthfully: tick an item only when it has been verified, and leave it unticked when it has not. Do not run local builds or Terraform commands to satisfy the checklist. Preserve the local-unit-test checkbox wording, but leave it unchecked if not verified under the applicable restrictions.
6. Write the completed body to a secure temporary file created with `mktemp`. Populate it with the file-editing tool, not shell write tricks. Create the PR with an explicit conventional-commit title and body file:

   ```sh
   gh pr create \
     --base "$base" \
     --title "$title" \
     --body-file "$body_file"
   ```

   Remove the temporary body file after the command succeeds or fails. Stop and report failures; do not retry blindly and risk duplicate PRs.
7. Inspect the created PR and confirm its title uses conventional-commit syntax and its body retains the template headings and completed prose content, beginning with the `## <Title>` section. Report the PR URL.
8. Use [Jira updates](../update-jira-task/SKILL.md) to post a compact PR link and status update when authorised; report unavailable write access accurately.

## Template

```markdown
## <Title>
<Description of change>

- Screenshot (if applicable): <screenshot>
- Jira Issue link (if applicable): <jira link>

### Fixes # (Issue/Ticket)
- Fixes # (issue): <github issue>
- Jira Issue link (If applicable): <jira link>

### Type of change
- [ ] Bugfix (non-breaking change which fixes an issue)
- [ ] New feature (adds new functionality)
- [ ] Feature Enhancement (Modified or improved an existing feature)
- [ ] Technical task (technical improvement, debt, or enabler)

### Checklist:
- [ ] My code follows the coding guidelines of this project
- [ ] My code generates no new errors/bugs in the static code analysis results (Linting, SonarQube, CodeQL)
- [ ] My code does not cause the continuous integration build to fail
- [ ] My code does not break existing unit tests
- [ ] My code has added adequate and relevant level of unit tests to test my changes locally
- [ ] I have performed a self-review of my own code
```

## Pitfalls
- Do not replace the template with a handwritten summary or omit its sections.
- Do not use the PR conventional-commit title verbatim as the body `## <Title>` heading; the body heading must remain prose.
- Do not add validation prose beyond the template's required checklist, unless the user asks for it.
- Do not leave placeholder text in the final PR body.
- Do not confuse Jira-prefixed commit titles with conventional-commit PR titles.

## Verification
1. The PR title uses conventional-commit format, while the body `## <Title>` heading is prose that describes the same change.
2. Every applicable template field is accurate, and every inapplicable optional field says `Not applicable.`.
3. Only verified checklist items are ticked.
4. The published PR body preserves the template's structure.
5. The temporary body file has been removed and the actual PR URL reported.
# GitHub App Setup Guide

This guide walks through creating and configuring the Engineering Memory GitHub App,
installing it on a GitHub organisation, and wiring up the webhook receiver.

---

## Prerequisites

- A GitHub account with access to create GitHub Apps
- Your Engineering Memory instance deployed and reachable over HTTPS  
  (GitHub will reject non-HTTPS webhook URLs in production)
- The `GITHUB_WEBHOOK_SECRET` environment variable ready (generate one below)

---

## Step 1 — Generate a Webhook Secret

The webhook secret is used to verify that incoming webhook requests are
genuinely from GitHub.  Generate a cryptographically secure random string:

```bash
# macOS / Linux
openssl rand -hex 32
```

Copy the output — you will need it in Step 4 and again in your `.env`.

---

## Step 2 — Create the GitHub App

1. Go to **GitHub → Settings → Developer Settings → GitHub Apps**
   - For a personal account: `https://github.com/settings/apps`
   - For an organisation: `https://github.com/organizations/<org>/settings/apps`

2. Click **New GitHub App**.

3. Fill in the **GitHub App name** — e.g. `Engineering Memory`.

4. Set **Homepage URL** to your deployment URL (e.g. `https://app.yourdomain.com`).

5. **Webhook**:
   - Check **Active**
   - Set **Webhook URL** to: `https://your-api-domain.com/github/webhook`
   - Set **Webhook secret** to the value generated in Step 1

6. **Repository permissions** — set the following:

   | Permission | Access |
   |---|---|
   | **Contents** | Read-only |
   | **Metadata** | Read-only (mandatory) |
   | **Pull requests** | Read-only |

7. **Subscribe to events** — check:
   - ✅ **Pull request**

8. Under **"Where can this GitHub App be installed?"**, select:
   - **Any account** (allows installation on any GitHub org)

9. Click **Create GitHub App**.

---

## Step 3 — Note Your App Credentials

After creation, you will be on the App's settings page.  Note down:

| Value | Where to find it | Environment variable |
|---|---|---|
| **App ID** | Listed near the top of the settings page | `GITHUB_APP_ID` |
| **Webhook Secret** | The value you set in Step 2 | `GITHUB_WEBHOOK_SECRET` |

---

## Step 4 — Generate and Download the Private Key

The private key is used to authenticate API calls made on behalf of the
GitHub App (e.g. listing repositories, fetching PR diffs).

1. On the App settings page, scroll down to **Private keys**.
2. Click **Generate a private key**.
3. A `.pem` file will be downloaded to your machine.
4. Store this file securely — **do not commit it to version control**.

To use it in your environment:

```bash
# Convert to a single-line string for use in environment variables
cat your-app-name.YYYY-MM-DD.private-key.pem | base64 | tr -d '\n'
```

Set the output as `GITHUB_APP_PRIVATE_KEY` in your `.env`.

---

## Step 5 — Configure Environment Variables

Add the following to your `.env` file (see `.env.example` for the full template):

```bash
# GitHub App
GITHUB_APP_ID=123456
GITHUB_APP_PRIVATE_KEY=LS0tLS1CRUdJTi...  # base64-encoded .pem
GITHUB_WEBHOOK_SECRET=your-32-char-hex-string-from-step-1
```

---

## Step 6 — Install the App on a GitHub Organisation

1. Go to the GitHub App's settings page.
2. Click **Install App** in the left sidebar.
3. Click **Install** next to the target organisation.
4. Select **All repositories** or choose specific repositories.
5. Click **Install**.

GitHub will display a confirmation page with the **Installation ID** in the URL:
```
https://github.com/organizations/<org>/settings/installations/<installation-id>
```

Note this `installation-id` — you will use it when linking the GitHub
installation to an Engineering Memory organisation via the API.

---

## Step 7 — Link the Installation to an Engineering Memory Organisation

After installing the app on GitHub, associate the installation with your
Engineering Memory organisation using the Admin API (to be implemented):

```http
POST /api/v1/organizations/{slug}/github/installations
Authorization: Bearer <your-jwt-token>
X-Org-Slug: your-org-slug

{
  "github_installation_id": 12345678,
  "github_account_login": "acme-corp",
  "github_account_type": "Organization"
}
```

Until this is done, incoming webhook events for this installation will be
stored in `raw_events` with `organization_id = NULL`.

---

## Step 8 — Verify the Webhook

After installing the app and starting your API server:

1. Open a pull request on any connected repository.
2. Merge the pull request.
3. GitHub will deliver a `pull_request` webhook to `/github/webhook`.
4. Check the API logs for:
   ```
   Stored merged PR event (delivery=<uuid>, pr=#<n>, repo=<owner/repo>, event_id=<uuid>)
   ```
5. Query the database to confirm the event was stored:
   ```sql
   SELECT id, event_type, action, github_delivery_id, created_at
   FROM raw_events
   ORDER BY created_at DESC
   LIMIT 5;
   ```

---

## Webhook Event Reference

| GitHub Event | Action | Accepted? |
|---|---|---|
| `pull_request` | `closed` + `merged: true` | ✅ **Stored in raw_events** |
| `pull_request` | `closed` + `merged: false` | ❌ Acknowledged, not stored |
| `pull_request` | `opened`, `synchronize`, etc. | ❌ Acknowledged, not stored |
| Any other event | — | ❌ Acknowledged, not stored |

---

## Troubleshooting

### Webhook returns 401
- Ensure `GITHUB_WEBHOOK_SECRET` matches exactly what was set in the GitHub App settings.
- Check for trailing whitespace or newline characters in the env var.

### Webhook returns 422
- The payload failed Pydantic validation.  Check the API logs for the exact error.
- This may indicate a GitHub payload schema change — open an issue.

### Event stored but `organization_id` is NULL
- The GitHub installation has not been linked to an Engineering Memory org yet.
- Complete Step 7 above.

### GitHub shows webhook delivery failures
- Verify the webhook URL is accessible from the internet (not `localhost`).
- For local development, use a tunnelling tool such as [ngrok](https://ngrok.com):
  ```bash
  ngrok http 8000
  # Use the generated HTTPS URL as your webhook URL
  ```

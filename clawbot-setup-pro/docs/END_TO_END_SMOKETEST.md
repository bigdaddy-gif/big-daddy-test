# End-to-End Smoketest (Backend + Desktop Helper)

## Prereqs
- Docker installed (for backend + Postgres)
- Go installed (to build the helper)

## 1) Run backend
From `clawbot-setup-pro/backend`:

```bash
export STRIPE_SECRET_KEY=sk_test_...              # optional for checkout
export STRIPE_WEBHOOK_SECRET=whsec_...            # required if testing webhooks
export RESEND_API_KEY=re_...                      # optional for real magic-link emails

docker compose up --build
```

API: http://localhost:8000

## 2) Authenticate (dev login → JWT)
This is the fastest way to test end-to-end.

```bash
JWT=$(curl -s -X POST http://localhost:8000/v1/dev/login \
  -H 'content-type: application/json' \
  -d '{"email":"you@example.com"}' | python3 -c 'import sys, json; print(json.load(sys.stdin)["access_token"])')

echo "$JWT"
```

> Note: `/v1/dev/login` only works when `JWT_SECRET` is the default dev value (`dev-secret-change-me`).

## 3) Pair device
Create a pairing code (requires JWT):
```bash
curl -s -X POST http://localhost:8000/v1/devices/pair \
  -H "authorization: Bearer $JWT"
```

## 4) Activate helper
Build helper (from `clawbot-setup-pro/desktop-helper`):
```bash
go build ./cmd/helper
```

Activate (exchange pairing code for device token):
```bash
./helper activate <PAIR_CODE> --name "My PC" --platform macos --base-url http://localhost:8000
```

Start loop:
```bash
./helper loop --device-id <DEVICE_ID> --device-token <DEVICE_TOKEN> --base-url http://localhost:8000
```

## 5) Start a job
Use the smoketest plan in `clawbot-setup-pro/plans/basic-smoketest.json`.

```bash
PLAN_JSON=$(cat clawbot-setup-pro/plans/basic-smoketest.json)

curl -s -X POST http://localhost:8000/v1/jobs/start \
  -H "authorization: Bearer $JWT" \
  -H 'content-type: application/json' \
  -d '{"device_id":"<DEVICE_ID>","plan":'$PLAN_JSON'}'
```

## 6) View status + logs
Job status:
```bash
curl -s http://localhost:8000/v1/jobs/<JOB_ID> \
  -H "authorization: Bearer $JWT"
```

Device logs:
```bash
curl -s http://localhost:8000/v1/devices/<DEVICE_ID>/logs?limit=200 \
  -H "authorization: Bearer $JWT"
```

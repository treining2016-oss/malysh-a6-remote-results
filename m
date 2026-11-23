#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail
umask 077
CODE="${1:-}"
if [[ ! "$CODE" =~ ^[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}$ ]]; then
  echo MALYSH_SENTINEL_BAD_CODE >&2
  exit 2
fi
STATUS_DIR="/storage/emulated/0/Android/data/com.termux/files"
STATUS="$STATUS_DIR/malysh-sentinel-status.log"
AGENT_LOG="$STATUS_DIR/malysh-sentinel-agent.log"
mkdir -p "$STATUS_DIR"
: > "$STATUS"
phase(){ printf 'MALYSH_SENTINEL_PHASE=%s\n' "$1" | tee -a "$STATUS"; }
fail(){ rc=$?; printf 'MALYSH_SENTINEL_FAIL line=%s rc=%s\n' "$LINENO" "$rc" | tee -a "$STATUS"; exit "$rc"; }
trap fail ERR
phase START
command -v termux-wake-lock >/dev/null 2>&1 && termux-wake-lock || true
pkg update -y
pkg install -y proot-distro termux-services
phase TERMUX_READY
if ! proot-distro login debian -- true >/dev/null 2>&1; then
  proot-distro install debian
fi
phase DEBIAN_READY
proot-distro login debian -- bash -lc 'export DEBIAN_FRONTEND=noninteractive; apt-get update && apt-get install -y python3 python3-venv python3-pip git curl ca-certificates'
phase DEBIAN_DEPS_READY
if proot-distro login debian -- test -s /etc/sentinelx/identity.json; then
  phase IDENTITY_PRESENT
else
  proot-distro login debian -- env SENTINELX_ENROLL_CODE="$CODE" bash -lc 'curl -fsSL https://get.sentinelx.app | SENTINELX_ENROLL_CODE="$SENTINELX_ENROLL_CODE" bash'
  phase ENROLLMENT_COMPLETE
fi
: > "$AGENT_LOG"
nohup proot-distro login debian -- runuser -u sentinelx -- /opt/sentinelx-cloud-core/.venv/bin/sentinelx-cloud-core --hub https://mcp.sentinelx.app --identity /etc/sentinelx/identity.json --config /etc/sentinelx/config.yaml >"$AGENT_LOG" 2>&1 &
AGENT_PID=$!
printf 'MALYSH_SENTINEL_AGENT_PID=%s\n' "$AGENT_PID" | tee -a "$STATUS"
sleep 8
if kill -0 "$AGENT_PID" 2>/dev/null; then
  phase AGENT_RUNNING
else
  phase AGENT_EXITED
  tail -80 "$AGENT_LOG" | tee -a "$STATUS"
  exit 3
fi
phase COMPLETE

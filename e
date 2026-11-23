#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail
umask 077
CODE="${1:-}"
if [[ ! "$CODE" =~ ^[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}$ ]]; then
  echo MALYSH_SENTINEL_BAD_CODE >&2
  exit 2
fi
MARK=/sdcard/Android/data/com.termux/files
LOG="$MARK/sx-enroll.log"
exec > >(tee -a "$LOG") 2>&1
printf 'stage=sentinel_install\n' > "$MARK/sx-stage.txt"
proot-distro login debian -- env SENTINELX_ENROLL_CODE="$CODE" bash -lc 'curl -fsSL https://get.sentinelx.app | SENTINELX_ENROLL_CODE="$SENTINELX_ENROLL_CODE" bash'
printf 'stage=sentinel_installed\n' > "$MARK/sx-stage.txt"
S="$PREFIX/var/service/sentinelx"
mkdir -p "$S/log" "$S/control"
cat > "$S/run" <<'EOF'
#!/data/data/com.termux/files/usr/bin/sh
exec proot-distro login debian -- runuser -u sentinelx -- /opt/sentinelx-cloud-core/.venv/bin/sentinelx-cloud-core --hub https://mcp.sentinelx.app --identity /etc/sentinelx/identity.json --config /etc/sentinelx/config.yaml 2>&1
EOF
cat > "$S/control/t" <<'EOF'
#!/data/data/com.termux/files/usr/bin/sh
pkill -TERM -f "sentinelx_core --identity|sentinelx-cloud-core --hub" 2>/dev/null || true
EOF
chmod 700 "$S/run" "$S/control/t"
ln -sf "$PREFIX/share/termux-services/svlogger" "$S/log/run"
if ! pgrep -f "runsvdir.*$PREFIX/var/service" >/dev/null 2>&1; then
  nohup runsvdir -P "$PREFIX/var/service" >"$HOME/.malysh-runsvdir.log" 2>&1 &
  sleep 2
fi
sv up sentinelx || true
sleep 5
sv status sentinelx || true
printf 'stage=complete\n' > "$MARK/sx-stage.txt"

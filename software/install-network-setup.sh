#!/bin/bash
# Explicit, optional one-time system setup. Does not activate any connection.
set -euo pipefail
[[ $EUID -eq 0 ]] || { echo 'Run with sudo: sudo bash install-network-setup.sh USER'; exit 1; }
INSTALL_USER=${1:-${SUDO_USER:-}}
[[ "$INSTALL_USER" =~ ^[a-z_][a-z0-9_-]*[$]?$ ]] && id "$INSTALL_USER" >/dev/null || { echo 'Specify the installation user.'; exit 1; }
PROFILE='Just one more moment — smartphone'
if ! nmcli -g connection.id connection show | grep -Fxq "$PROFILE"; then
    nmcli connection add type wifi ifname '*' con-name "$PROFILE" ssid just-one-more-moment \
        connection.permissions "user:$INSTALL_USER" connection.autoconnect-priority -10 \
        wifi-sec.key-mgmt wpa-psk wifi-sec.psk hslu-phki-hs26
fi
# Grant only connection activation/deactivation, not profile/system/radio editing.
RULE_DIR=/etc/polkit-1/rules.d
install -d -m 0755 "$RULE_DIR"
RULE_FILE=$(mktemp)
trap 'rm -f "$RULE_FILE"' EXIT
cat >"$RULE_FILE" <<EOF
// Just one more moment: installed explicitly for $INSTALL_USER.
polkit.addRule(function(action, subject) {
    if (subject.user === "$INSTALL_USER" &&
        action.id === "org.freedesktop.NetworkManager.network-control") {
        return polkit.Result.YES;
    }
});
EOF
install -o root -g root -m 0644 "$RULE_FILE" "$RULE_DIR/49-just-one-more-moment-network.rules"
echo 'Hotspot profile and connection permission installed. Current connection unchanged.'

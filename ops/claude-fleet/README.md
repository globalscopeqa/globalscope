# Claude Code fleet provisioning

Idempotent Ansible setup for running Claude Code as a persistent,
auto-restarting `systemd` service across your VPS fleet.

## What this does, per server

- Installs Node.js 20 (only if not already 18+)
- Installs the Claude Code CLI (`@anthropic-ai/claude-code`)
- Runs it as a `systemd` service (`claude-code.service`) — auto-restarts on
  crash **and on reboot**, unlike a bare `tmux` session
- Authenticates via `ANTHROPIC_API_KEY` (usage-based billing) — no manual
  OAuth click needed per server
- Confirms SSH key login works, then disables SSH password auth
- Enables UFW (SSH-only) and fail2ban

## One-time setup (on your own machine, not the VPS)

```bash
# Install Ansible
pip install ansible   # or: brew install ansible / apt install ansible

# Point at your real 21 servers
$EDITOR inventory.ini

# Add your Anthropic API key (from console.anthropic.com -> API Keys)
cp vault.yml.example vault.yml
$EDITOR vault.yml            # paste your real key in
ansible-vault encrypt vault.yml   # sets a password to unlock it later
```

## Run it against the whole fleet

```bash
ansible-playbook -i inventory.ini claude-fleet.yml --ask-vault-pass
```

Safe to re-run any time (e.g., after adding a new server to `inventory.ini`,
or to pick up an updated `claude-code` version) — Ansible only changes what's
actually out of date.

## Checking a server afterward

```bash
ssh vps1   # if you set up ~/.ssh/config aliases, otherwise: ssh root@<ip>
systemctl status claude-code    # confirm it's running
journalctl -u claude-code -f    # tail its logs live
```

## Notes / decisions worth revisiting

- **Permission mode**: the systemd unit runs `claude --permission-mode=auto`.
  Auto mode lets Claude execute lower-risk actions without asking, which is
  necessary for something running unattended — but review
  https://code.claude.com/docs/en/permission-modes and decide if that's the
  right default for production servers, or if some servers should run more
  conservatively.
- **Root vs. a scoped user**: the service runs as root for full maintenance
  capability. If some servers don't need that, consider a dedicated sudo
  user instead — smaller blast radius if anything ever goes wrong.
- **Cost**: API key usage is billed per-token via Anthropic Console,
  separate from any Claude.ai subscription. Monitor usage at
  https://console.anthropic.com, especially once all 21 are running
  unattended.
- **Key rotation**: if you ever need to revoke access, delete/rotate the key
  in Anthropic Console — no need to touch each server individually.

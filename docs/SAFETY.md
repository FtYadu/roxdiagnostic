# ROX 01 Diagnostic Tool - Safety Guidelines

## ⚠️ CRITICAL WARNING

**Using this tool to modify vehicle firmware can:**
- Disable critical safety systems
- Cause engine damage
- Result in vehicle immobilization
- Violate manufacturer warranties
- Be illegal in your jurisdiction

**You use this tool at your own risk. The developers and maintainers assume NO LIABILITY for damage, injury, or legal consequences.**

---

## Prerequisites Before Using This Tool

### Legal Requirements

- ✅ **You must own the vehicle** or have explicit permission from the owner
- ✅ **Check local laws** regarding firmware modification (DMCA, EU right-to-repair, etc.)
- ✅ **Understand warranty implications** - modifications will void manufacturer warranty
- ✅ **Accept full liability** for any consequences

### Technical Requirements

- ✅ **Keep a backup** of the original firmware before any modifications
- ✅ **Test on a simulator first** (if available) before touching real vehicle
- ✅ **Never interrupt a firmware update** - it can brick the ECU
- ✅ **Ensure stable power** - use a battery charger, never rely on engine battery
- ✅ **Disconnect safety-critical systems** if performing experimental changes

---

## Safe Operating Procedures

### 1. Firmware Extraction (SAFE - Read-Only)

✅ **Safe to perform:**
- Extracting firmware creates a read-only copy
- No changes to vehicle
- Can be done repeatedly

### 2. Live Data Reading (SAFE - Read-Only)

✅ **Safe to perform:**
- Reading live data is non-invasive
- No modifications to ECU
- Can be done repeatedly

### 3. DTC Reading (SAFE - Read-Only)

✅ **Safe to perform:**
- Reading fault codes doesn't modify anything
- Can be done repeatedly

### 4. DTC Clearing (MODERATE RISK)

⚠️ **Potential issues:**
- Clears check engine light
- May be illegal if hiding emissions failures

### 5. ECU Firmware Update (CRITICAL RISK)

🚨 **HIGH RISK - Only advanced users:**

**DO THIS ONLY IF:**
- You have extracted and verified a firmware backup
- You understand the firmware changes
- Vehicle is parked on level ground
- Engine is OFF and will stay OFF during update
- Battery is fully charged
- You have 30+ minutes uninterrupted

---

## Emergency Procedures

### If Firmware Update Gets Interrupted

**Vehicle may not start. Follow this exactly:**

1. **DO NOT attempt to start the vehicle**
2. **Reconnect ENET cable immediately**
3. **Run restore from backup:**
   ```bash
   python implementation/rox_diagnostic.py firmware update firmware_backup_*.bin
   ```

---

## Legal Disclaimer

**By using this tool, you:**

1. Accept full responsibility for all consequences
2. Acknowledge the risks of vehicle firmware modification
3. Release the developers from all liability
4. Confirm you have legal right to modify your vehicle
5. Agree not to use this for illegal purposes

**This tool is provided "AS IS" without any warranty.**

See [LICENSE](../LICENSE) for full legal terms.

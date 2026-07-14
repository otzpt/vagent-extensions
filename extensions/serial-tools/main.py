"""Serial Tools — list serial ports and talk to a board (Arduino, Pico, ESP32…).

Port listing is pure stdlib. Sending/receiving needs pyserial
(pip install pyserial) and returns a clear message when it's missing.

V-Agent extension contract:
  register(ctx) is called once at sidecar startup;
  each tool is fn(cwd: str, args: dict) -> str.
"""

import glob
import sys


def list_serial_ports(cwd, args):
    ports = []
    if sys.platform == "win32":
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DEVICEMAP\SERIALCOMM")
            i = 0
            while True:
                try:
                    _, value, _ = winreg.EnumValue(key, i)
                    ports.append(str(value))
                    i += 1
                except OSError:
                    break
        except OSError:
            pass
    elif sys.platform == "darwin":
        ports = glob.glob("/dev/cu.*")
    else:
        ports = glob.glob("/dev/ttyACM*") + glob.glob("/dev/ttyUSB*")
    return "\n".join(sorted(ports)) if ports else "(no serial ports detected)"


def serial_send(cwd, args):
    args = args or {}
    port = str(args.get("port", "")).strip()
    data = str(args.get("data", ""))
    baud = int(args.get("baud", 115200))
    if not port:
        return "ERROR: 'port' is required (use list_serial_ports first)."
    try:
        import serial  # pyserial
    except ImportError:
        return "ERROR: pyserial is not installed. Run in the terminal: pip install pyserial"
    try:
        with serial.Serial(port, baud, timeout=1) as conn:
            if data:
                conn.write((data + "\n").encode("utf-8", "replace"))
            reply = conn.read(4096).decode("utf-8", "replace").strip()
        return f"sent: {data!r}\nreceived: {reply or '(nothing within 1s)'}"
    except Exception as e:
        return f"ERROR on {port}: {e} (is the Serial Monitor holding the port open?)"


def register(ctx):
    ctx.add_tool(
        "list_serial_ports",
        list_serial_ports,
        "args: {} — list the serial ports currently present (COMx / /dev/tty*).",
    )
    ctx.add_tool(
        "serial_send",
        serial_send,
        'args: {"port": "COM3", "data": "text", "baud": 115200} — send one line '
        "over serial and return whatever the board replies within 1 second. "
        "Requires pyserial; the port must not be held open by a monitor.",
    )

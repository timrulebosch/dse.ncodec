from typing import Dict
import re

def decode_mime_type(mime_type: str) -> Dict[str, str]:
    if not mime_type:
        raise ValueError("MimeType is empty")
    
    mime_map = {}

    parts = [part.strip() for part in re.split(r'[;\s]+', mime_type) if part.strip()]
    
    for part in parts:
        if '=' in part:
            kv = part.split('=', 1)
            if len(kv) == 2:
                key = kv[0].strip()
                value = kv[1].strip()
                mime_map[key] = value
    
    # Required parameters
    guard = ["interface", "type", "schema"]
    for key in guard:
        if key in mime_map:
            param = mime_map[key]
            if key == "type":
                if param not in ["can", "pdu"]:
                    raise ValueError(f"unsupported type: {param}")
            elif key == "interface":
                if param != "stream":
                    raise ValueError(f"wrong interface: {param}")
            elif key == "schema":
                if param != "fbs":
                    raise ValueError(f"wrong schema: {param}")
        else:
            raise ValueError("missing required mimetype parameter")
    
    # All possible parameters
    options = ["type", "schema", "interface", "bus", "bus_id", "node_id", 
               "interface_id", "swc_id", "ecu_id"]
    
    for key in mime_map:
        if key not in options:
            raise ValueError(f"unexpected mimetype parameter: {key}")
    
    return mime_map
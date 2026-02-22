import re

def parse_target_path(target_string) -> dict:
    """Attempts to parse a target track or device in ClyphX notation,
    returns a dict you can use to find the target object manually."""
    result = {
        "input_string": target_string,
        "track": None,
        "ring_track": None,
        "device": None,
        "parameter_type": None,
        "parameter_name": None,
        "bank": None,
        "parameter_number": None,
        "chain": None,
        "send": None,
        "chain_map": None,
        "error": None,
        "send_track": None,
        "arm": False,
        "monitor": False,
        "mute": False,
        "solo": False,
        "track_select": False,
        "play": False,
        "stop": False,
        "x_fade_assign": False,
    }

    # Handle NONE and SELP special cases (case-insensitive)
    target_upper = target_string.upper()
    if target_upper == "NONE":
        return result
    elif target_upper == "SELP":
        result["parameter_type"] = "SELP"
        return result
    elif target_upper == "XFADER":
        result["parameter_type"] = "XFADER"
        return result

    # Check if this starts with DEV( - if so, no track part
    if target_string.upper().startswith("DEV("):
        # This is a device-only specification
        return parse_device_specification(target_string, result)

    # Use find_split_index to properly handle quoted strings with '/' characters
    split_index = find_split_index(target_string)

    if split_index == -1:
        # No '/' found outside of quotes
        # Check for ring(n) format
        ring_pattern = re.compile(r"^ring\((\d+)\)$", re.IGNORECASE)
        ring_match = ring_pattern.match(target_string)

        if ring_match:
            result["ring_track"] = ring_match.group(1)
            return result
        elif target_string.startswith('"') and target_string.endswith('"'):
            result["track"] = target_string[1:-1]
            return result
        else:
            result["track"] = target_string
            return result

    # Split the target_string into track_part and rest using the proper index
    track_part = target_string[:split_index].strip()
    rest = target_string[split_index + 1 :].strip()

    # Check for ring(n) format in track_part
    ring_pattern = re.compile(r"^ring\((.*?)\)$", re.IGNORECASE)
    ring_match = ring_pattern.match(track_part)

    if ring_match:
        result["ring_track"] = ring_match.group(1)
    else:
        if track_part.startswith('"') and track_part.endswith('"'):
            result["track"] = track_part[1:-1]
        else:
            result["track"] = track_part

    if (
        not result["ring_track"]
        and result["track"]
        and re.match(r"^[a-zA-Z]$", result["track"])
    ):
        result["send_track"] = result["track"]
        result["track"] = None

    return parse_rest_specification(rest, result)


def parse_device_specification(target_string, result):
    """Parse a device specification that starts with DEV("""
    dev_pattern = re.compile(r"DEV\(", re.IGNORECASE)
    dev_match = dev_pattern.search(target_string)
    dev_start = dev_match.end()
    dev_end = target_string.find(")", dev_start)
    if dev_start > 0 and dev_end > dev_start:
        dev_spec = target_string[dev_start:dev_end]

        # Use the shared device spec parsing function
        result = parse_device_spec(dev_spec, result)
        if result["error"]:
            return result

        param_part = target_string[dev_end + 1 :].strip()
        return parse_parameter_part(param_part, result)

    result["error"] = f"Unrecognized parameter format: {target_string[4:]}"
    return result


def parse_rest_specification(rest, result):
    """Parse the part after the track specification"""
    rest_upper = rest.upper()

    if rest_upper == "ARM":
        result["parameter_type"] = "ARM"
        result["arm"] = True
        return result
    elif rest_upper.startswith("MON "):
        parts = rest.split()
        if len(parts) >= 2:
            mon_state = parts[1].upper()
            if mon_state in ["IN", "AUTO", "OFF"]:
                result["parameter_type"] = "MON"
                result["monitor"] = mon_state.lower()
                return result
    elif rest_upper == "MUTE":
        result["parameter_type"] = "MUTE"
        result["mute"] = True
        return result
    elif rest_upper == "PLAY":
        result["parameter_type"] = "PLAY"
        result["play"] = True
        return result
    elif rest_upper == "SEL":
        result["parameter_type"] = "SEL"
        result["track_select"] = True
        return result
    elif rest_upper == "SOLO":
        result["parameter_type"] = "SOLO"
        result["solo"] = True
        return result
    elif rest_upper == "STOP":
        result["parameter_type"] = "STOP"
        result["stop"] = True
        return result
    elif rest_upper.startswith("XFADE "):
        parts = rest.split()
        if len(parts) >= 2:
            xfade_state = parts[1].upper()
            if xfade_state in ["A", "B", "OFF"]:
                result["parameter_type"] = "XFADE"
                result["x_fade_assign"] = xfade_state.lower()
                return result

    # Existing parameter checks
    if rest_upper in ["VOL", "PAN", "CUE", "XFADER", "PANL", "PANR"]:
        result["parameter_type"] = rest_upper
        return result

    # Handle send parameters without device
    if rest_upper.startswith("SEND"):
        result["parameter_type"] = "SEND"
        parts = rest.split()
        if len(parts) >= 2:
            result["send"] = parts[1]
        return result

    # Handle device parameters
    dev_pattern = re.compile(r"DEV\(", re.IGNORECASE)
    if dev_pattern.search(rest):
        dev_match = dev_pattern.search(rest)
        dev_start = dev_match.end()
        dev_end = rest.find(")", dev_start)
        if dev_start > 0 and dev_end > dev_start:
            dev_spec = rest[dev_start:dev_end]

            # Use the shared device spec parsing function
            result = parse_device_spec(dev_spec, result)
            if result["error"]:
                return result

            param_part = rest[dev_end + 1 :].strip()
            return parse_parameter_part(param_part, result)

    return result


def parse_parameter_part(param_part, result):
    """Parse the parameter part after a device specification"""
    if not param_part:
        return result

    # Handle chain parameters
    chain_pattern = re.compile(r"CH\(", re.IGNORECASE)
    if chain_pattern.search(param_part):
        chain_match = chain_pattern.search(param_part)
        chain_start = chain_match.end()
        chain_end = param_part.find(")", chain_start)
        if chain_start > 0 and chain_end > chain_start:
            result["chain"] = param_part[chain_start:chain_end]
            param_part = param_part[chain_end + 1 :].strip()
            param_part_upper = param_part.upper()

            if param_part_upper.startswith("SEND"):
                parts = param_part.split()
                result["parameter_type"] = "chain_send"
                if len(parts) >= 2:
                    result["send"] = parts[1]
            elif param_part_upper in ["PAN", "VOL"]:
                result["parameter_type"] = param_part_upper

            return result

    # Check for standard parameter types (PAN, VOL, etc.) first
    param_part_upper = param_part.upper()
    if param_part_upper in [
        "PAN",
        "VOL",
        "CUE",
        "XFADER",
        "PANL",
        "PANR",
        "SEL",
    ]:
        result["parameter_type"] = param_part_upper
    # Handle SEND directly after DEV(...)
    elif param_part_upper.startswith("SEND"):
        parts = param_part.split()
        result["parameter_type"] = "SEND"
        if len(parts) >= 2:
            result["send"] = parts[1]
    elif param_part.startswith('"') and param_part.endswith('"'):
        result["parameter_name"] = param_part[1:-1]
    elif param_part_upper == "CS":
        result["parameter_type"] = "CS"
    elif " " in param_part:
        parts = param_part.split()
        if parts[0].upper().startswith("B") and parts[1].upper().startswith("P"):
            result["bank"] = parts[0][1:]
            result["parameter_number"] = parts[1][1:]
    elif param_part_upper.startswith("P"):
        result["parameter_number"] = param_part[1:]

    return result
def find_split_index(target_string):
    """Find the index of the '/' that separates track from the rest,
    considering quoted strings that may contain '/' characters."""
    in_quotes = False
    for i, char in enumerate(target_string):
        if char == '"':
            in_quotes = not in_quotes
        elif char == "/" and not in_quotes:
            return i
    return -1


def parse_device_spec(dev_spec, result):
    """Parse device specification and populate result with device or chain_map.

    Args:
        dev_spec: The device specification string (content between DEV(...))
        result: The result dictionary to populate

    Returns:
        The updated result dictionary
    """
    # Check if there are any dots outside of quoted segments
    has_unquoted_dots = "." in re.sub(r'"[^"]*"', "", dev_spec)

    if has_unquoted_dots:
        # Split by dots and process each part
        chain_parts = dev_spec.split(".")
        processed_parts = []

        for i, part in enumerate(chain_parts, start=1):
            # Strip quotes from quoted parts
            if part.startswith('"') and part.endswith('"'):
                processed_part = part[1:-1]
            else:
                processed_part = part

            processed_parts.append(processed_part)

            # Check SEL keyword position constraint
            if processed_part.upper() == "SEL" and i > 2:
                result["error"] = (
                    f"zcx only supports the SEL keyword in position 1 or 2: {dev_spec}"
                )
                return result

        result["chain_map"] = processed_parts
    else:
        # Single device specification
        if dev_spec.startswith('"') and dev_spec.endswith('"'):
            result["device"] = dev_spec[1:-1]
        else:
            result["device"] = dev_spec

    return result

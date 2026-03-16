import json
import csv
import re
import os

ARKIT_KEYS = [
    "EyeBlinkLeft", "EyeLookDownLeft", "EyeLookInLeft", "EyeLookOutLeft", "EyeLookUpLeft",
    "EyeSquintLeft", "EyeWideLeft", "EyeBlinkRight", "EyeLookDownRight", "EyeLookInRight",
    "EyeLookOutRight", "EyeLookUpRight", "EyeSquintRight", "EyeWideRight", "JawForward",
    "JawRight", "JawLeft", "JawOpen", "MouthClose", "MouthFunnel", "MouthPucker",
    "MouthRight", "MouthLeft", "MouthSmileLeft", "MouthSmileRight", "MouthFrownLeft",
    "MouthFrownRight", "MouthDimpleLeft", "MouthDimpleRight", "MouthStretchLeft",
    "MouthStretchRight", "MouthRollLower", "MouthRollUpper", "MouthShrugLower",
    "MouthShrugUpper", "MouthPressLeft", "MouthPressRight", "MouthLowerDownLeft",
    "MouthLowerDownRight", "MouthUpperUpLeft", "MouthUpperUpRight", "BrowDownLeft",
    "BrowDownRight", "BrowInnerUp", "BrowOuterUpLeft", "BrowOuterUpRight", "CheekPuff",
    "CheekSquintLeft", "CheekSquintRight", "NoseSneerLeft", "NoseSneerRight", "TongueOut",
    "HeadYaw", "HeadPitch", "HeadRoll", "LeftEyeYaw", "LeftEyePitch", "LeftEyeRoll",
    "RightEyeYaw", "RightEyePitch", "RightEyeRoll"
]

BLENDSHAPE_COUNT = len(ARKIT_KEYS)  # 61


def extract_arkit_from_response(response: str):
    """Extract the last JSON object (ARKit coefficients) from the response field."""
    # Find the last { ... } block
    last_brace = response.rfind('}')
    if last_brace == -1:
        return None
    # Search backward for the matching {
    depth = 0
    start = -1
    for i in range(last_brace, -1, -1):
        if response[i] == '}':
            depth += 1
        elif response[i] == '{':
            depth -= 1
            if depth == 0:
                start = i
                break
    if start == -1:
        return None
    json_str = response[start:last_brace + 1]
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return None


def image_path_to_timecode(image_path: str, index: int = 0) -> str:
    """Convert a sequential frame index (0-based) to a timecode string at 1 fps.
    e.g. index=0 -> 00:00:00:00.000, index=1 -> 00:00:01:00.000
    """
    # 1 fps: each record advances by 1 second
    seconds_total = index
    hours = seconds_total // 3600
    minutes = (seconds_total % 3600) // 60
    seconds = seconds_total % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}:00.000"


def convert_jsonl_to_csv(input_path: str, output_path: str):
    fieldnames = ["Timecode", "BlendshapeCount"] + ARKIT_KEYS

    with open(input_path, 'r', encoding='utf-8') as fin, \
         open(output_path, 'w', newline='', encoding='utf-8') as fout:

        writer = csv.DictWriter(fout, fieldnames=fieldnames)
        writer.writeheader()

        frame_index = 0
        for line_num, line in enumerate(fin, 1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"[Warning] Line {line_num}: JSON parse error: {e}")
                continue

            response = record.get("response", "")
            arkit = extract_arkit_from_response(response)
            if arkit is None:
                print(f"[Warning] Line {line_num}: Failed to extract ARKit coefficients")
                continue

            # Generate timecode starting from 00:00:00 at 1 fps
            images = record.get("images", [])
            image_path = images[0].get("path", "") if images else ""
            timecode = image_path_to_timecode(image_path, index=frame_index)
            frame_index += 1

            row = {
                "Timecode": timecode,
                "BlendshapeCount": BLENDSHAPE_COUNT,
            }
            for key in ARKIT_KEYS:
                row[key] = arkit.get(key, 0.0)

            writer.writerow(row)

        print(f"Done. Output saved to: {output_path}")


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_jsonl = os.path.join(script_dir, "example_result.jsonl")
    output_csv = os.path.join(script_dir, "example_result.csv")
    convert_jsonl_to_csv(input_jsonl, output_csv)

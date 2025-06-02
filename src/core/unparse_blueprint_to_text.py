import json


def unparse_blueprint_to_text(blueprint_data):
    """
    Converts parsed blueprint data back to the original raw blueprint text format.

    :param blueprint_data: list of (expression_blueprint: dict, count: int)
    :returns: *(str)* Reconstructed blueprint as a human-readable string.
    """
    lines = []
    if isinstance(blueprint_data, str):
        blueprint_data = json.loads(blueprint_data)

    for blueprint, count in blueprint_data:
        category = blueprint["category"]
        lines.append(f"{category}: {count}")

        if category == "math":
            for elem in blueprint["elements"]:
                type_ = elem["type"]
                if type_ == "bracket":
                    lines.append(f"  {elem['value']}")
                elif type_ == "int":
                    start, end = elem["start"], elem["end"]
                    if start == 0:
                        lines.append(f"  int {end}")
                    else:
                        lines.append(f"  int {start} {end}")
                elif type_.startswith("float"):
                    start, end = elem["start"], elem["end"]
                    if start == 0.0:
                        lines.append(f"  {type_} {end}")
                    else:
                        lines.append(f"  {type_} {start} {end}")
                elif type_ == "operator":
                    val = elem["value"]
                    if isinstance(val, list):
                        ops = " ".join(val)
                    else:
                        ops = val
                    lines.append(f"  op {ops}")
                elif type_ == "function":
                    lines.append(f"  func {elem['value']}")
                elif type_ == "constant":
                    lines.append(f"  const {elem['value']}")
        elif category == "date":
            if "start_year" in blueprint:
                lines.append(f"  start {blueprint['start_year']}")
            if "end_year" in blueprint:
                lines.append(f"  end {blueprint['end_year']}")

        lines.append("")  # Add blank line between blocks

    return "\n".join(lines).strip()

import re
import json
import yaml
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

from collections import defaultdict


def extract_parameters(input_string):
    parameter_pattern = re.compile(r'parameter Real (\w+) = ([\d.]+);')
    return {match[0]: float(match[1]) for match in parameter_pattern.findall(input_string)}


def evaluate_expression(expression, context):
    try:
        return str(eval(expression, {}, context))
    except Exception as e:
        return expression


def convert_to_json_compatible(annotation):
    # Replace Modelica array syntax with JSON array syntax
    annotation = annotation.replace("{", "[").replace("}", "]")

    # Replace Modelica key=value with "key": value
    annotation = re.sub(r'(\w+)\s*=\s*', r'"\1": ', annotation)

    # Correctly handle and wrap non-numeric values in quotes
    def wrap_non_numeric(match):
        value = match.group(1)
        if re.match(r'^\d+(\.\d+)?$', value):  # If it's a number, don't wrap
            return value
        else:
            return f'"{value}"'

    annotation = re.sub(r'(?<=:\s)([.\w]+)', wrap_non_numeric, annotation)

    # Convert object-like structures to JSON key-value format
    annotation = re.sub(r'(\w+)\s*\(', r'"\1": {', annotation)
    annotation = annotation.replace('),', '},').replace(')', '}')

    annotation = annotation.splitlines()
    annotation[0] = annotation[0].replace('[', '{')
    annotation[-1] = annotation[-1].replace(']', '}')
    no_comments = []
    for i, line in enumerate(annotation):
        if not line.strip().startswith('//'):
            no_comments.append(line)

    annotation = '\n'.join(no_comments)

    return annotation


def replace_parameters_in_string(s, parameters):
    for key, value in parameters.items():
        # Using regex to ensure exact matches only (e.g., avoid partial replacements)
        s = re.sub(r'\b' + re.escape(key) + r'\b', str(value), s)
    return s


class UniqueKeyLoader(yaml.SafeLoader):
    def __init__(self, stream):
        super().__init__(stream)
        self._parents = []

    def construct_mapping(self, node, deep=False):
        mapping = defaultdict(list)
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            value = self.construct_object(value_node, deep=deep)
            mapping[key].append(value)

        unique_mapping = {}
        for key, values in mapping.items():
            if len(values) > 1:
                for i, value in enumerate(values):
                    unique_mapping[f"{key}_{i}"] = value
            else:
                unique_mapping[key] = values[0]

        return unique_mapping


def unique_key_loader(stream):
    return yaml.load(stream, UniqueKeyLoader)


def safe_eval(expr):
    try:
        return eval(expr)
    except Exception as e:
        return expr


# Recursive function to traverse and evaluate expressions in the dictionary
def evaluate_dict(d):
    for key, value in d.items():
        if isinstance(value, dict):
            evaluate_dict(value)
        elif isinstance(value, list):
            d[key] = [evaluate_dict_list(item) for item in value]
        elif isinstance(value, str):
            d[key] = safe_eval(value)
    return d


# Helper function to handle lists
def evaluate_dict_list(item):
    if isinstance(item, dict):
        return evaluate_dict(item)
    elif isinstance(item, list):
        return [evaluate_dict_list(sub_item) for sub_item in item]
    elif isinstance(item, str):
        return safe_eval(item)
    else:
        return item


def convert_color(color):
    return tuple(c / 255 for c in color)


def rotate_point(x, y, angle, origin=(0, 0)):
    rad = np.deg2rad(angle)
    ox, oy = origin
    cos_angle = np.cos(rad)
    sin_angle = np.sin(rad)
    x_rot = ox + cos_angle * (x - ox) - sin_angle * (y - oy)
    y_rot = oy + sin_angle * (x - ox) + cos_angle * (y - oy)
    return x_rot, y_rot


def draw_rectangle(ax, rect):
    x1, y1 = rect["extent"][0]
    x2, y2 = rect["extent"][1]
    width = x2 - x1
    height = y2 - y1
    facecolor = convert_color(rect["fillColor"])
    edgecolor = convert_color(rect["lineColor"])

    if "rotation" in rect:
        angle = rect["rotation"]
        # Pivot point is the top-right corner (x2, y2)
        origin = (0, 0)
        # Create a rectangle at the origin
        rectangle = patches.Rectangle((x1, y1), width, height, linewidth=rect["lineThickness"], edgecolor=edgecolor, facecolor=facecolor)
        # Create a transform for rotation around the pivot point
        t = patches.transforms.Affine2D().rotate_deg_around(origin[0], origin[1], angle)
        # Apply the transform to the rectangle
        rectangle.set_transform(t + ax.transData )
    else:
        # Create a rectangle without rotation
        rectangle = patches.Rectangle((x1, y1), width, height, linewidth=rect["lineThickness"], edgecolor=edgecolor, facecolor=facecolor)

    ax.add_patch(rectangle)


def draw_line(ax, line):
    xs = [point[0] for point in line["points"]]
    ys = [point[1] for point in line["points"]]
    color = convert_color(line["color"])
    ax.plot(xs, ys, color=color, linewidth=line["thickness"])


def draw_text(ax, text):
    x = (text["extent"][0][0] + text["extent"][1][0]) / 2
    y = (text["extent"][0][1] + text["extent"][1][1]) / 2
    ax.text(x, y, text["textString"], fontsize=text["fontSize"], ha='center', va='center')


def draw_ellipse(ax, ellipse):
    x = (ellipse["extent"][0][0] + ellipse["extent"][1][0]) / 2
    y = (ellipse["extent"][0][1] + ellipse["extent"][1][1]) / 2
    width = ellipse["extent"][1][0] - ellipse["extent"][0][0]
    height = ellipse["extent"][1][1] - ellipse["extent"][0][1]
    edgecolor = convert_color(ellipse["lineColor"])
    facecolor = convert_color(ellipse["fillColor"])
    ellipse_patch = patches.Ellipse((x, y), width, height, linewidth=ellipse["lineThickness"], edgecolor=edgecolor, facecolor=facecolor)
    ax.add_patch(ellipse_patch)


def draw_polygon(ax, polygon):
    points = polygon["points"]
    edgecolor = convert_color(polygon["lineColor"])
    facecolor = convert_color(polygon["fillColor"])
    polygon_patch = patches.Polygon(points, closed=True, linewidth=polygon["lineThickness"], edgecolor=edgecolor, facecolor=facecolor)
    ax.add_patch(polygon_patch)


def visualize_openmodelica_graphics(graphics_dict):
    fig, ax = plt.subplots()

    for key, graphic in graphics_dict["graphics"].items():
        if "Rectangle" in key:
            draw_rectangle(ax, graphic)
        elif "Line" in key:
            draw_line(ax, graphic)
        elif "Text" in key:
            draw_text(ax, graphic)
        elif "Ellipse" in key:
            draw_ellipse(ax, graphic)
        elif "Polygon" in key:
            draw_polygon(ax, graphic)

    ax.set_xlim(-150, 150)
    ax.set_ylim(-100, 100)
    ax.set_aspect('equal')
    plt.grid(True)
    return fig


def plot(input_string: str):
    # Extract parameters
    parameters = extract_parameters(input_string)

    # Step 1: Extract Icon and Diagram annotations
    icon_annotation_match = re.search(r'annotation\s*\(\s*Icon\s*\((.*?)\)\s*\)\s*;', input_string, re.DOTALL)
    diagram_annotation_match = re.search(r'annotation\s*\(\s*Diagram\s*\((.*?)\)\s*\)\s*;', input_string, re.DOTALL)

    if icon_annotation_match:
        icon_annotation = icon_annotation_match.group(1).strip()
    if diagram_annotation_match:
        diagram_annotation = diagram_annotation_match.group(1).strip()

    icon_annotation = replace_parameters_in_string(icon_annotation, parameters)
    diagram_annotation = replace_parameters_in_string(diagram_annotation, parameters)
    # Step 2: Convert to JSON-compatible strings
    icon_annotation_json = convert_to_json_compatible(icon_annotation)
    diagram_annotation_json = convert_to_json_compatible(diagram_annotation)
    print(icon_annotation_json)
    # Step 3: Parse JSON-compatible strings into Python dictionaries
    icon_dict = unique_key_loader(icon_annotation_json)
    diagram_dict = unique_key_loader(diagram_annotation_json)

    icon_dict = evaluate_dict(icon_dict)
    diagram_dict = evaluate_dict(diagram_dict)

    return visualize_openmodelica_graphics(icon_dict), visualize_openmodelica_graphics(diagram_dict)


if __name__ == "__main__":
    model = """
    model ForkedTube
  parameter Real length1 = 1; // Length of the straight part
  parameter Real length2 = 0.5; // Length of the bent part
  parameter Real radius = 0.05; // Radius of the tube
  Real x1(length1);
  Real x2(length2);
  Real angle = 90; // Angle of the bent part

  // Icon View
  annotation(
    Icon(
      graphics = {
        Rectangle(
          extent = {{-120, -60}, {120, 60}},
          lineColor = {0, 0, 0},
          fillColor = {255, 255, 255},
          fillPattern = FillPattern.None,
          lineThickness = 3
        ),
        Ellipse(
          extent = {{-100, 0}, {-80, 20}},
          lineColor = {0, 0, 0},
          fillColor = {255, 0, 0},
          fillPattern = FillPattern.Solid,
          smooth = Smooth.None,
          lineThickness = 3
        ),
        Ellipse(
          extent = {{80, 0}, {100, 20}},
          lineColor = {0, 0, 0},
          fillColor = {0, 0, 255},
          fillPattern = FillPattern.Solid,
          smooth = Smooth.None,
          lineThickness = 3
        ),
        Line(
          points = {{-90, 0}, {0, 0}},
          color = {0, 0, 0},
          thickness = 3.0
        ),
        Line(
          points = {{0, 0}, {90, 0}},
          color = {0, 255, 0},
          thickness = 3.0
        ),
        Line(
          points = {{90, 0}, {90, 60}},
          color = {0, 255, 0},
          thickness = 3.0
        ) 
      }
    )
  );

  // Diagram View
  annotation(
    Diagram(
      graphics = {
        Line(
          points = {{-90, 0}, {0, 0}},
          color = {0, 0, 0},
          thickness = 2.0
        ),
        Line(
          points = {{0, 0}, {90, 0}},
          color = {0, 255, 0},
          thickness = 2.0
        ),
        Line(
          points = {{90, 0}, {90, 60}},
          color = {0, 255, 0},
          thickness = 2.0
        )
      }
    )
  );

equation
  x1 = length1;
  x2 = length2;
end ForkedTube;
    """
    # from example_tube import input_string
    # model = input_string
    plot(model)
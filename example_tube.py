# Define the input string
default_model = """
model DefaultModel
  parameter Real length = 10;
  parameter Real diameter = 2;
  parameter Real pressure_in = 100000;
  parameter Real pressure_out = 101325;

  Real flow_rate;

  // Icon View
  annotation(
    Icon(
      graphics = {
        Rectangle(
          extent = {{-50, -10}, {50, 10}},
          lineColor = {0, 0, 0},
          fillColor = {200, 200, 255},
          borderPattern = LinePattern.Solid,
          fillPattern = FillPattern.Solid,
          lineThickness = 1
        ),
        Line(
          points = {{-50, 0}, {50, 0}},
          color = {0, 0, 255},
          thickness = 2.0
        ),
        Text(
          extent = {{-70, 10}, {-30, 30}},
          textString = "Inlet",
          fontSize = 12
        ),
        Text(
          extent = {{30, 10}, {70, 30}},
          textString = "Outlet",
          fontSize = 12
        )
      }
    )
  );

  // Diagram View
  annotation(
    Diagram(
      graphics = {
        Rectangle(
          extent = {{-50, -10}, {50, 10}},
          lineColor = {0, 0, 0},
          fillColor = {200, 200, 255},
          borderPattern = LinePattern.Solid,
          fillPattern = FillPattern.Solid,
          lineThickness = 1
        ),
        Line(
          points = {{-50, 0}, {50, 0}},
          color = {0, 0, 255},
          thickness = 2.0
        ),
        Text(
          extent = {{-70, 10}, {-30, 30}},
          textString = "Inlet",
          fontSize = 12
        ),
        Text(
          extent = {{30, 10}, {70, 30}},
          textString = "Outlet",
          fontSize = 12
        )
      }
    )
  );

equation
  flow_rate = (pressure_in - pressure_out) / (length * diameter);
end DefaultModel;
"""

input_string = """
model ForkedTubeFlow
  parameter Real length1 = 5;
  parameter Real length2 = 5;
  parameter Real diameter = 0.1;
  parameter Real pressure_in = 100000;
  parameter Real pressure_out1 = 101325;
  parameter Real pressure_out2 = 101325;
  Real flow_rate1;
  Real flow_rate2;
  Real total_flow_rate;
  // Icon View
  annotation(
    Icon(
      graphics = {
        Rectangle(
          extent = {{-120, -60}, {120, 60}},
          lineColor = {0, 0, 0},
          fillColor = {200, 200, 255},
          borderPattern = LinePattern.Solid,
          fillPattern = FillPattern.Solid,
          lineThickness = 1
        ),
        Line(
          points = {{-80, 0}, {0, 0}, {40, 40}},
          color = {0, 0, 255},
          thickness = 2.0
        ),
        Line(
          points = {{0, 0}, {40, -40}},
          color = {0, 0, 255},
          thickness = 2.0
        ),
        Text(
          extent = {{-100, 20}, {-60, 40}},
          textString = "Inlet",
          fontSize = 12
        ),
        Text(
          extent = {{50, 50}, {90, 70}},
          textString = "Outlet1",
          fontSize = 12
        ),
        Text(
          extent = {{50, -70}, {90, -50}},
          textString = "Outlet2",
          fontSize = 12
        ),
        Ellipse(
          extent = {{-5, -5}, {5, 5}},
          lineColor = {255, 0, 0},
          fillColor = {255, 0, 0},
          lineThickness = 1.0
        )
      }
    )
  );
  // Diagram View
  annotation(
    Diagram(
      graphics = {
        // Main tube
        Rectangle(
          extent = {{-100, -diameter * 100}, {-50, diameter * 100}},
          lineColor = {0, 0, 255},
          fillColor = {0, 0, 255},
          fillPattern = FillPattern.Solid,
          lineThickness = 1.0
        ),
        // Forked tube 1
        Rectangle(
          extent = {{-50, 0}, {30, diameter * 100}},
          rotation = 30,
          lineColor = {0, 0, 255},
          fillColor = {0, 0, 255},
          fillPattern = FillPattern.Solid,
          lineThickness = 1.0
        ),
        // Forked tube 2
        Rectangle(
          extent = {{-50, 0}, {0, -diameter * 100}},
          rotation = -45,
          lineColor = {0, 0, 255},
          fillColor = {0, 0, 255},
          fillPattern = FillPattern.Solid,
          lineThickness = 1.0
        ),
        // Junction point
        Ellipse(
          extent = {{-52, -diameter * 2}, {-48, diameter * 2}},
          lineColor = {255, 0, 0},
          fillColor = {255, 0, 0},
          lineThickness = 1.0
        ),
        // Inlet arrow
        Polygon(
          points = {{-110, 5}, {-100, 0}, {-110, -5}},
          lineColor = {0, 0, 0},
          fillColor = {0, 0, 0},
          lineThickness = 1
        ),
        // Outlet arrows
        Polygon(
          points = {{5, 50 + diameter * 50}, {0, 50}, {5, 50 - diameter * 50}},
          lineColor = {0, 0, 0},
          fillColor = {0, 0, 0},
          lineThickness = 1
        ),
        Polygon(
          points = {{5, -50 + diameter * 50}, {0, -50}, {5, -50 - diameter * 50}},
          lineColor = {0, 0, 0},
          fillColor = {0, 0, 0},
          lineThickness = 1
        ),
        // Text labels
        Text(
          extent = {{-130, 10}, {-90, 30}},
          textString = "Pressure In",
          fontSize = 12
        ),
        Text(
          extent = {{10, 60 + diameter * 50}, {50, 80 + diameter * 50}},
          textString = "Pressure Out 1",
          fontSize = 12
        ),
        Text(
          extent = {{10, -70 + diameter * 50}, {50, -50 + diameter * 50}},
          textString = "Pressure Out 2",
          fontSize = 12
        )
      }
    )
  );
equation
  total_flow_rate = (pressure_in - pressure_out1) / (length1 * diameter) + (pressure_in - pressure_out2) / (length2 * diameter);
  flow_rate1 = (pressure_in - pressure_out1) / (length1 * diameter);
  flow_rate2 = (pressure_in - pressure_out2) / (length2 * diameter);
end ForkedTubeFlow;
"""
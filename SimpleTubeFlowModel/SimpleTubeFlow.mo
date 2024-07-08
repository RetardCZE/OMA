
model SimpleTubeFlow
  parameter Real length = 10;
  parameter Real diameter = 0.1;
  parameter Real pressure_in = 100000;
  parameter Real pressure_out = 101325;
  Real flow_rate;

  annotation(
    Diagram(
      graphics = {
        Rectangle(
          extent = {{-50, -50}, {50, 50}},
          lineColor = {0, 0, 255},
          fillColor = {255, 255, 255},
          borderPattern = LinePattern.Solid,
          fillPattern = FillPattern.None,
          lineThickness = 0.25
        ),
        Text(
          extent = {{-50, 60}, {50, 80}},
          textString = "SimpleTubeFlow",
          fontSize = 12
        )
      }
    )
  );
equation
  flow_rate = (pressure_in - pressure_out) / (length * diameter);
end SimpleTubeFlow;

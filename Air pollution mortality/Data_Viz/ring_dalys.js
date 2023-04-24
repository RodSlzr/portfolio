d3.csv('data/data_age_dalys_19.csv').then((data) => {

  for (let d of data) {
    d.dalys = +d.dalys;
  }

  const height = 500,
    width = 600,
    innerRadius = 125,
    outerRadius = 175,
    labelRadius = 200;

  const arcs = d3.pie().value(d => d.dalys)(data);
  const arc = d3.arc().innerRadius(innerRadius).outerRadius(outerRadius);
  const arcLabel = d3.arc().innerRadius(labelRadius).outerRadius(labelRadius);

  const svg = d3.select("#ring_dalys")
    .append("svg")
    .attr("width", width)
    .attr("height", height)
    .attr("viewBox", [-width / 2, -height / 2, width, height])
    .attr("style", "max-width: 100%; height: auto; height: intrinsic;");

  svg.append("g")
    .attr("stroke", "white")
    .attr("stroke-width", 2)
    .attr("stroke-linejoin", "round")
    .selectAll("path")
    .data(arcs)
    .join("path")
    .attr("fill", (d, i) => d3.schemeCategory10[i+2])
    .attr("d", arc);

   svg.append("g")
     .attr("font-size", 10)
     .attr("text-anchor", "middle")
     .selectAll("text")
     .data(arcs)
     .join("text")
     .attr("transform", d => `translate(${arcLabel.centroid(d)})`)
     .selectAll("tspan")
     .data(d => {
       return [d.data.age_group, d.data.dalys];
     })
     .join("tspan")
     .attr("x", 0)
     .attr("y", (d, i) => `${i * 1.1}em`)
     .attr("font-weight", (d, i) => i ? null : "bold")
     .text(d => d);

   svg.append("text")
     .attr("font-size", 30)
     .attr("font-weight", "bold")
     .attr("text-anchor", "middle")
     .attr("alignment-baseline", "middle")
     .text("Age")
     .style("font-size", 20);
});
Promise.all([
  d3.csv("data/data_map_welfare_gdp_19.csv"),
  d3.json("libs/countries-110m.json")
]).then(([data, world]) => {

  const tooltip = d3.select("body")
  .append("div")
  .attr("class", "svg-tooltip")
  .style("position", "absolute")
  .style("visibility", "hidden");

  const height = 610,
  width = 975;

  
  const svg = d3.select("#chart_map")
  .append("svg")
  .attr("viewBox", [0, 0, width, height]);

  const dataByCountry = {};

  for (let d of data) {
    d.welf_cost_gdp = +d.welf_cost_gdp;
    //making a lookup table from the array (unemployment data)
    dataByCountry[d.country] = d;
  }


  const countries = topojson.feature(world, world.objects.countries);
  const mesh = topojson.mesh(world, world.objects.countries);


  // Quantize evenly breakups domain into range buckets
   const color = d3.scaleQuantize()
     .domain([0, 14]).nice()
     .range(d3.schemeReds[9]);

  const projection = d3.geoMercator()
    .fitSize([width, height], mesh);
  const path = d3.geoPath().projection(projection);


   d3.select("#legend")
     .node()
     .appendChild(
       Legend(
         d3.scaleOrdinal(
           ["1.5", "3", "4.5", "6", "7.5", "9", "10.5", "12", "13.5+"],
           d3.schemeReds[9]
         ),
         { title: "Percent of GDP (%)" }
       ));

   svg.append("g")
     .selectAll("path")
     .data(countries.features)
     .join("path")
     .attr("fill", d => (d.properties.name in dataByCountry) ? color(dataByCountry[d.properties.name].welf_cost_gdp) : '#ccc')
     .attr("d", path)
     .on("mousemove", function (event, d) {
       let info = dataByCountry[d.properties.name];
       tooltip
         .style("visibility", "visible")
         .html(`${info.country}<br>${info.welf_cost_gdp}%`)
         .style("top", (event.pageY - 10) + "px")
         .style("left", (event.pageX + 10) + "px");
       d3.select(this).attr("fill", "goldenrod");
     })
     .on("mouseout", function () {
       tooltip.style("visibility", "hidden");
       d3.select(this).attr("fill", d => (d.properties.name in dataByCountry) ? color(dataByCountry[d.properties.name].welf_cost_gdp) : '#ccc');
     });
});
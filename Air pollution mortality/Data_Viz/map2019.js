Promise.all([
  d3.csv("data/data_scatter_premdeaths_90vs15vs19.csv"),
  d3.json("libs/countries-110m.json")
]).then(([data, world]) => {

  const tooltip = d3.select("body")
  .append("div")
  .attr("class", "svg-tooltip")
  .style("position", "absolute")
  .style("visibility", "hidden");

  const height = 610,
  width = 975;

  
  const svg = d3.select("#chart_map_2019")
  .append("svg")
  .attr("viewBox", [0, 0, width, height]);

  const dataByCountry = {};

  for (let d of data) {
    d.rel_prem_deaths_2019 = +d.rel_prem_deaths_2019;
    //making a lookup table from the array (unemployment data)
    dataByCountry[d.country] = d;
  }


  const countries = topojson.feature(world, world.objects.countries);
  const mesh = topojson.mesh(world, world.objects.countries);


  // Quantize evenly breakups domain into range buckets
   const color = d3.scaleQuantize()
     .domain([50, 850]).nice()
     .range(d3.schemeBlues[9]);


  const projection = d3.geoMercator()
    .fitSize([width, height], mesh);
  const path = d3.geoPath().projection(projection);


   d3.select("#legend_map_2019")
     .node()
     .appendChild(
       Legend(
         d3.scaleOrdinal(
           ["50", "150", "250", "350", "450", "550", "650", "750", "850+"],
           d3.schemeBlues[9]
         ),
         { title: "Premature deaths per million people" }
       ));

   svg.append("g")
     .selectAll("path")
     .data(countries.features)
     .join("path")
     .attr("fill", d => (d.properties.name in dataByCountry) ? color(dataByCountry[d.properties.name].rel_prem_deaths_2019) : '#ccc')
     .attr("d", path)
     .on("mousemove", function (event, d) {
       let info = dataByCountry[d.properties.name];
       tooltip
         .style("visibility", "visible")
         .html(`${info.country}<br>${info.rel_prem_deaths_2019}`)
         .style("top", (event.pageY - 10) + "px")
         .style("left", (event.pageX + 10) + "px");
       d3.select(this).attr("fill", "goldenrod");
     })
     .on("mouseout", function () {
       tooltip.style("visibility", "hidden");
       d3.select(this).attr("fill", d => (d.properties.name in dataByCountry) ? color(dataByCountry[d.properties.name].rel_prem_deaths_2019) : '#ccc');
     });
});
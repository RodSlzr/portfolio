let height = 600,
    width = 600,
    margin = ({ top: 25, right: 30, bottom: 35, left: 40 });
  
const svg = d3.select("#chart")
    .append("svg")
    .attr("viewBox", [0, 0, width, height]);


d3.csv('data/data_scatter_premdeaths_90vs15vs19.csv').then(data => {

  for (let d of data) {
    d.rel_prem_deaths_1990 = +d.rel_prem_deaths_1990;
    d.rel_prem_deaths_2019 = +d.rel_prem_deaths_2019;
    d.abs_prem_deaths_2019 = +d.abs_prem_deaths_2019;
  };
  
  let x = d3.scaleLinear()
    .domain(d3.extent(data, d => d.rel_prem_deaths_1990)).nice()
    .range([margin.left, width - margin.right]);

  let y = d3.scaleLinear()
    .domain(d3.extent(data, d => d.rel_prem_deaths_2019)).nice()
    .range([height - margin.bottom, margin.top]);

  const radius = d3.scaleLinear()
    .domain([0, d3.max(data, d => d.abs_prem_deaths_2019)])
    .range([6, 30]);


  svg.append("circle").attr("cx",60).attr("cy",50).attr("r", 6).style("fill", "green")
  svg.append("text").attr("x", 70).attr("y", 50).text("G7").style("font-size", "15px").attr("alignment-baseline","middle")
  svg.append("circle").attr("cx",60).attr("cy",70).attr("r", 6).style("fill", "blue")
  svg.append("text").attr("x", 70).attr("y", 70).text("G20").style("font-size", "15px").attr("alignment-baseline","middle")
  svg.append("circle").attr("cx",60).attr("cy",90).attr("r", 6).style("fill", "red")
  svg.append("text").attr("x", 70).attr("y", 90).text("Balkans").style("font-size", "15px").attr("alignment-baseline","middle")
  svg.append("circle").attr("cx",60).attr("cy",110).attr("r", 6).style("fill", "#cecece")
  svg.append("text").attr("x", 70).attr("y", 110).text("Rest of the world").style("font-size", "15px").attr("alignment-baseline","middle")
  svg.append("text").attr("x", 280).attr("y", 595).text("1990").style("font-size", "15px").attr("alignment-baseline","middle")
  svg.append("text").attr("x", 0).attr("y", 277).text("2019").style("font-size", "15px").attr("alignment-baseline","middle").attr("text-orientation","sideways")


  var color_table = {
    'yes'   : 'green',
    'no'   : 'red',
    'other'   : '#cecece',
    'G7'   : 'green',
    'G20'   : 'blue',
    'Eeurope'   : '#cecece',
    'Balkans'   : 'red'
    }

  svg.append('line')
    .attr('x1',x(0))
    .attr('x2',x(1400))
    .attr('y1',y(0))
    .attr('y2',y(1400))
    .attr('stroke', "red")
    .attr("fill", "none")
    .attr("stroke-width", 4);


  svg.append("g")
    .attr("transform", `translate(0,${height - margin.bottom})`)
    .attr("class", "x-axis")
    .call(d3.axisBottom(x).tickSize(-height + margin.top + margin.bottom))

  svg.append("g")
    .attr("transform", `translate(${margin.left},0)`)
    .attr("class", "y-axis")
    .call(d3.axisLeft(y).tickSize(-width + margin.left + margin.right))

   svg.append("g")
     .selectAll("circle")
     .data(data)
     .join("circle")
     .attr("fill", d => color_table[d.cat])
     .attr("r", d => radius(d.abs_prem_deaths_2019)) 
     .attr("cx", d => x(d.rel_prem_deaths_1990))
     .attr("cy", d => y(d.rel_prem_deaths_2019))
     .attr("opacity", 0.55);


   const tooltip = d3.select("body").append("div")
     .attr("class", "svg-tooltip")
     .style("position", "absolute")
     .style("visibility", "hidden");

   d3.selectAll("circle")
     .on("mouseover", function(event, d) {
       tooltip
         .style("visibility", "visible")
         .html(`Country: ${d.country}<br />Deaths: ${d.abs_prem_deaths_2019}`);
     })
     .on("mousemove", function(event) {
       tooltip
         .style("top", (event.pageY - 10) + "px")
         .style("left", (event.pageX + 10) + "px");
     })
     .on("mouseout", function() {
       tooltip.style("visibility", "hidden");
     })
    
});
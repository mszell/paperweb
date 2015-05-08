var width = 1400,
    height = 1400;

var force = d3.layout.force()
    .charge(-300)
    .linkStrength( function(edge, i) { if (edge.typ == 0) {return (edge.value);} else {return edge.value/4;} } )
    .linkDistance( function(edge, i) { if (edge.typ == 0) {return 6;} else {return 128+410/Math.sqrt(edge.value+0.5);} } )
    .gravity(0.1)
    .size([width, height]);

var svg = d3.select("#paperweb").append("svg")
    .attr("width", width)
    .attr("height", height);

d3.json("data/paperweb_barabasi.json", function(error, graph) {
  var nodeMap = {};
    graph.nodes.forEach(function(x) { nodeMap[x.name] = x; });
    graph.links = graph.links.map(function(x) {
      return {
        source: nodeMap[x.source],
        target: nodeMap[x.target],
        value: x.value,
        typ: x.typ,
        yearfirst: x.yearfirst,
        yearlast: x.yearlast
      };
    });

  force
      .nodes(graph.nodes)
      .links(graph.links)
      .start();

  var link = svg.selectAll(".link")
      .data(graph.links)
      .enter().append("line")
      .attr("class", function(d) { return "link" + d.typ + "";})
      .style("stroke-width", function(d) { return d.value; });

  var node = svg.selectAll(".node")
      .data(graph.nodes)
      .enter().append("circle")
      .attr("class", "node")
      .attr("r", function(d) { return Math.sqrt(30+50*(d.yearlast-d.yearfirst)); })
      .style("fill", function(d) { return "#9"+Math.max(Math.min(9-(d.yearlast-2009), 9), 0)+""+Math.max(Math.min(9-(d.yearlast-2009), 9))+""; })
      .call(force.drag)
      .on('mouseover', tip.show) //Added
      .on('mouseout', tip.hide); //Added

  force.on("tick", function() {
    graph.nodes[0].x = width / 2;
    graph.nodes[0].y = height / 2;

    link.attr("x1", function(d) { return d.source.x; })
        .attr("y1", function(d) { return d.source.y; })
        .attr("x2", function(d) { return d.target.x; })
        .attr("y2", function(d) { return d.target.y; });

    node.attr("cx", function(d) { return d.x; })
        .attr("cy", function(d) { return d.y; });

  });
});

//Set up tooltip
var tip = d3.tip()
    .attr('class', 'd3-tip')
    .offset([-7, 0])
    .html(function (d) {
    return  d.fullname + "";
})
svg.call(tip);

// ====================================
// Variables
// ====================================
var width = 1400,
    height = 1400,
    padding = 1.5;

var force = d3.layout.force()
    .charge(-300)
    .linkStrength( function(edge, i) { if (edge.typ == 0) {return (edge.value);} else {return edge.value/4;} } )
    .linkDistance( function(edge, i) { if (edge.typ == 0) {return 10;} else {return 128+410/Math.sqrt(edge.value+0.5);} } )
    .gravity(0.1)
    .size([width, height]);

var svg = d3.select("#paperweb").append("svg")
    .attr("width", width)
    .attr("height", height);


// ====================================
// JSON call
// ====================================
d3.json("data/paperweb_barabasi_a.json", function(error, graph) {
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
      .on('mouseover', tip.show)
      .on('mouseout', tip.hide);

  force.on("tick", function() {
    graph.nodes[0].x = width / 2;
    graph.nodes[0].y = height / 2;

    link.attr("x1", function(d) { return d.source.x; })
        .attr("y1", function(d) { return d.source.y; })
        .attr("x2", function(d) { return d.target.x; })
        .attr("y2", function(d) { return d.target.y; });

    node.attr("cx", function(d) { return d.x; })
        .attr("cy", function(d) { return d.y; });

    node.each(collide(graph.nodes, 0.3));
  });

  var optArray = [];
  for (var i = 0; i < graph.nodes.length - 1; i++) {
      optArray.push(graph.nodes[i].name);
  }
  optArray = optArray.sort();
  $(function () {
      $("#search").autocomplete({
          source: optArray
      });
  });
});


// ====================================
// Tooltip
// ====================================
var tip = d3.tip()
    .attr('class', 'd3-tip')
    .offset([-7, 0])
    .html(function (d) {
    return  d.fullname + "";
})
svg.call(tip);


// ====================================
// Collision detection
// ====================================
function collide(nodes, alpha) {
  var quadtree = d3.geom.quadtree(nodes);
  return function(d) {
    var rb = 2*(Math.sqrt(30+50*(d.yearlast-d.yearfirst))) + padding, // would be nice if we didn't have to re-compute the radius here. no idea how to pass it over unfortunately.
        nx1 = d.x - rb,
        nx2 = d.x + rb,
        ny1 = d.y - rb,
        ny2 = d.y + rb;
    
    quadtree.visit(function(quad, x1, y1, x2, y2) {
      if (quad.point && (quad.point !== d)) {
        var x = d.x - quad.point.x,
            y = d.y - quad.point.y,
            l = Math.sqrt(x * x + y * y);
          if (l < rb) {
          l = (l - rb) / l * alpha;
          d.x -= x *= l;
          d.y -= y *= l;
          quad.point.x += x;
          quad.point.y += y;
        }
      }
      return x1 > nx2 || x2 < nx1 || y1 > ny2 || y2 < ny1;
    });
  };
}


// ====================================
// Search
// ====================================
function searchNode() {
    //find the node
    var selectedVal = document.getElementById('search').value;
    var node = svg.selectAll(".node");
    if (selectedVal == "none") {
        node.style("stroke", "white").style("stroke-width", "1");
    } else {
        var selected = node.filter(function (d, i) {
            return d.name != selectedVal;
        });
        selected.style("opacity", "0");
        var link = svg.selectAll(".link0, .link1")
        link.style("opacity", "0.05");
        d3.selectAll(".node, .link0, .link1").transition()
            .duration(4000)
            .style("opacity", 1);
    }
}

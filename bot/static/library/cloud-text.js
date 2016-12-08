var most = "天氣 天氣 美食 笑話 笑話 笑話 笑話 身分證";

var lack = "我帥嗎 你好 嗚嗚 嗚嗚 english";

document.getElementById("text").value = most;
var text1 = most.split(" ");
var used = [text1[0]];
for (var i = 0; i < text1.length; i++) {
	for (var j = 0; j < used.length; j++) {
		if (text1[i] == used[j]) {
			break;
		}
		if (j == used.length - 1) {
			used.push(text1[i]);
			break;
		}
	}
}
var spec = 0;

function change() {
	if (document.type.check1.checked == true && document.type.check2.checked == true) {
		document.getElementById("text").value = most + " " + lack;
		spec = 1;
	} else if (document.type.check1.checked == true) {
		document.getElementById("text").value = most;
		spec = 0;
		type = 0;
	} else if (document.type.check2.checked == true) {
		document.getElementById("text").value = lack;
		spec = 0;
		type = 1;
	} else {
		document.getElementById("text").value = null;
	}

	function t() {
		c = +d3.select("#angle-count").property("value"), u = Math.max(-90, Math.min(90, 0)), i = Math.max(-90, Math.min(90, 0)), e()
	}

	function e() {
		h.domain([0, c - 1]).range([u, i]);
		var t = l.selectAll("path.angle").data([{
			startAngle: u * d,
			endAngle: i * d
				}]);
		t.enter().insert("path", "circle").attr("class", "angle").style("fill", "#fc0"), t.attr("d", f);
		var o = l.selectAll("line.angle").data(d3.range(c).map(h));
		o.enter().append("line").attr("class", "angle"), o.exit().remove(), o.attr("transform", function (t) {
			return "rotate(" + (90 + t) + ")"
		}).attr("x2", function (t, e) {
			return e && e !== c - 1 ? -r : -r - 5
		});
		var s = l.selectAll("path.drag").data([u, i]);
		s.enter().append("path").attr("class", "drag").attr("d", "M-9.5,0L-3,3.5L-3,-3.5Z").call(d3.behavior.drag().on("drag", function (t, o) {
			t = (o ? i : u) + 90;
			var s = [-r * Math.cos(t * d), -r * Math.sin(t * d)],
				l = [d3.event.x, d3.event.y],
				c = ~~(Math.atan2(n(s, l), a(s, l)) / d);
			t = Math.max(-90, Math.min(90, t + c - 90)), c = i - u, o ? (i = t, c > 360 ? u += c - 360 : 0 > c && (u = i)) : (u = t, c > 360 ? i += 360 - c : 0 > c && (i = u)), e()
		}).on("dragend", generate)), s.attr("transform", function (t) {
			return "rotate(" + (t + 90) + ")translate(-" + r + ")"
		}), layout.rotate(function () {
			return h(~~(Math.random() * c))
		}), d3.select("#angle-count").property("value", c), d3.select("#angle-from").property("value", u), d3.select("#angle-to").property("value", i)
	}

	function n(t, e) {
		return t[0] * e[1] - t[1] * e[0]
	}

	function a(t, e) {
		return t[0] * e[0] + t[1] * e[1]
	}
	var r = 40.5,
		o = 35,
		s = 20,
		l = d3.select("#angles").append("svg").attr("width", 2 * (r + o)).attr("height", r + 1.5 * s).append("g").attr("transform", "translate(" + [r + o, r + s] + ")");
	l.append("path").style("fill", "none").attr("d", ["M", -r, 0, "A", r, r, 0, 0, 1, r, 0].join(" ")), l.append("line").attr("x1", -r - 7).attr("x2", r + 7), l.append("line").attr("y2", -r - 7), l.selectAll("text").data([-90, 0, 90]).enter().append("text").attr("dy", function (t, e) {
		return 1 === e ? null : ".3em"
	}).attr("text-anchor", function (t, e) {
		return ["end", "middle", "start"][e]
	}).attr("transform", function (t) {
		return t += 90, "rotate(" + t + ")translate(" + -(r + 10) + ")rotate(" + -t + ")translate(2)"
	}).text(function (t) {
		return t + "\xb0"
	});
	var u, i, c, d = Math.PI / 180,
		h = d3.scale.linear(),
		f = d3.svg.arc().innerRadius(0).outerRadius(r);
	d3.selectAll("#angle-count, #angle-from, #angle-to").on("change", t).on("mouseup", t), t(), parseText(d3.select("#text").property("value"));
	//d3.selectAll("text").style("fill","black");
	//document.getElementById("vis").style.fill="black";
}
var dots = new L.LayerGroup(),
	mymap;


function arrayUnique(array) {
	var a = array.concat();
	for (var i = 0; i < a.length; ++i) {
		for (var j = i + 1; j < a.length; ++j) {
			if (a[i][0] === a[j][0] && a[i][1] === a[j][1]) {
				a.splice(j--, 1);
			}
		}
	}

	return a;
}

function filterOutliers(someArray) {

	// Copy the values, rather than operating on references to existing values
	var values = someArray.concat();

	// Then sort
	values.sort(function (a, b) {
		return a - b;
	});

	/* Then find a generous IQR. This is generous because if (values.length / 4)
	 * is not an int, then really you should average the two elements on either
	 * side to find q1.
	 */
	var q1 = values[Math.floor((values.length / 4))];
	// Likewise for q3.
	var q3 = values[Math.ceil((values.length * (3 / 4)))];
	var iqr = q3 - q1;

	// Then find min and max values
	var maxValue = q3 + iqr * 1.5;
	var minValue = q1 - iqr * 1.5;

	// Then filter anything beyond or beneath these values.
	var filteredValues = values.filter(function (x) {
		return (x < maxValue) && (x > minValue);
	});

	// Then return
	return filteredValues;
}

function sum(array) {
	var s = array.reduce(function (pv, cv) {
		return pv + cv;
	}, 0);
	return s;
}


$.getJSON("../data/breeding_source_20160912.json", function (datas) {
	//console.log(datas); // this will show the info it in firebug console
	var dot = [],
		center = [0, 0];

	datas.data.forEach(function (d) {
		dot.push([d.lat, d.lng]);
	})


	if (dot.length > 0) { //none empty



		$('.title').append('<div id="mapid"></div>');
		mymap = L.map('mapid').setView([22.9971, 120.2126], 15);

		L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpandmbXliNDBjZWd2M2x6bDk3c2ZtOTkifQ._QA7i5Mpkd_m30IGElHziw', {
			maxZoom: 18,
			attribution: '',
			id: 'mapbox.streets'
		}).addTo(mymap);





		// dot plot
		var markers = L.markerClusterGroup();

		for (var i = 0; i < dot.length; i++) {
			var a = dot[i];

			var marker = L.marker(new L.LatLng(a[0], a[1]));
			marker.bindPopup('<p>' + i + '</p>');
			markers.addLayer(marker);
		}

		dots.addLayer(markers);
		mymap.addLayer(dots);

		/////////////////////////

		dot = arrayUnique(dot);

		var xArr = [],
			yArr = [];

		dot.forEach(function (d) {
			xArr.push(d[0]);
			yArr.push(d[1]);
		})

		if (filterOutliers(xArr).length != 0) {
			xArr = filterOutliers(xArr);
			yArr = filterOutliers(yArr);
		}

		center = [sum(xArr) / xArr.length, sum(yArr) / yArr.length];

		mymap.setView(center, 16);


	}
});
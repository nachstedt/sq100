window.addEvent('domready', function() {		
	document.getElements('.wait').addEvent('click', function(e){
		//preload activity-animation
		new Element('img', {'src':'/static/activity.gif'})
		
		var modal = new Element('div', 
			{'class': 'modal', styles: {opacity: .5, width: window.getSize().x, height: window.getSize().y}}
		).inject(document.getElement('body'), 'top');
		
		var hold = new Element('div', 
			{html: 'Please hold ... sending and receiving data', 'class': 'hold'}
		).inject(modal, 'after');
		
		hold.tween('top', [-100,0]);
	})
})

var Map = new Class({
    Implements: Options,
    
    options: {
        map: 'map',
        center: null,
        latitude_field: 'latitude',
        longitude_field: 'longitude',
        altitude_field: 'altitude'
    },

    initialize: function(options){
    	this.setOptions(options);
	    	
    	this.map = new GMap2($(this.options.map));    	
		this.map.setCenter($pick(this.options.center, new GLatLng(37.4419, -122.1419)), 10);
		this.map.disableDoubleClickZoom();
		this.map.enableScrollWheelZoom();
		this.map.addControl(new GScaleControl());
		this.map.addControl(new GSmallZoomControl());
		this.map.addControl(new GMapTypeControl());
		
		GMap2.prototype.centerAndZoomOnBounds = function(bounds){
		   var center_lat = (bounds.getNorthEast().lat() + bounds.getSouthWest().lat())/2;
		   var center_lng = (bounds.getNorthEast().lng() + bounds.getSouthWest().lng())/2;
		   var center = new GLatLng(center_lat,center_lng);
		   
		   this.setCenter(center, this.getBoundsZoomLevel(bounds));
		}
		
		this.tinyIcon_blue = new GIcon();
		this.tinyIcon_blue.image = "http://labs.google.com/ridefinder/images/mm_20_blue.png";
		this.tinyIcon_blue.shadow = "http://labs.google.com/ridefinder/images/mm_20_shadow.png";
		this.tinyIcon_blue.iconSize = new GSize(12, 20);
		this.tinyIcon_blue.shadowSize = new GSize(22, 20);
		this.tinyIcon_blue.iconAnchor = new GPoint(6, 20);
		this.tinyIcon_blue.infoWindowAnchor = new GPoint(5, 1);
		
		this.tinyIcon_red = new GIcon();
		this.tinyIcon_red.image = "http://labs.google.com/ridefinder/images/mm_20_red.png";
		this.tinyIcon_red.shadow = "http://labs.google.com/ridefinder/images/mm_20_shadow.png";
		this.tinyIcon_red.iconSize = new GSize(12, 20);
		this.tinyIcon_red.shadowSize = new GSize(22, 20);
		this.tinyIcon_red.iconAnchor = new GPoint(6, 20);
		this.tinyIcon_red.infoWindowAnchor = new GPoint(5, 1);
    },
    
    setup_geocoder: function(form) {
		this.geocoder = new GClientGeocoder();
		$(form).addEvent('submit', function(e){
			e.stop()
    		this.geocode(form);
		}.bind(this));
    },
    
    setup_marker_placement: function() {
    	GEvent.addListener(this.map, "dblclick", function(overlay, point) {
			this.place_marker(point);
		}.bind(this));
    },
    
    add_markers: function(points, icon) {
    	points.each(function(point){
			this.map.addOverlay(new GMarker(point, icon));
		}.bind(this));
    },
    
	place_marker: function(point) {
		this.map.clearOverlays();
		var m = new GMarker(point, {'draggable':'true'})
		this.map.addOverlay(m);
		
		GEvent.addListener(m, "drag", function(p) {
		  $(this.options.latitude_field).set('value', p.lat());
		  $(this.options.longitude_field).set('value', p.lng());
		}.bind(this));
		
		GEvent.addListener(m, "dragend", function(p) {
		  this.get_altitude(p);
		}.bind(this));
		
		$(this.options.latitude_field).set('value', point.lat());
		$(this.options.longitude_field).set('value', point.lng());
	},
	
	get_altitude: function(point) {
		new Request({
			method: 'post',
			url: '/waypoints/getWaypointAltitude',
			onSuccess: function(value){
				 $(this.options.altitude_field).set('value', value);
			}.bind(this),
			onFailure: function(){
			}
		}).send({data: {latitude: $(this.options.latitude_field).get('value'), longitude: $(this.options.longitude_field).get('value')}});
    },
			
	geocode: function(form) {
		var address = $(form).getElement('input').get('value');
		this.geocoder.getLatLng(address,
	      function(point) {
	        if (!point) {alert(address + " not found")} 
	        else {
	          this.map.setCenter(point, 13);
			  this.place_marker(point);
	        }
	      }.bind(this)
	    );
	}
});
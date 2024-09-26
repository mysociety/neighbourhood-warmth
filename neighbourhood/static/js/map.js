import $ from '../jquery/jquery.esm.js'
import L from '../leaflet/leaflet-1.9.3.esm.js'

L.Icon.Default.imagePath = "/static/leaflet/images/";

// https://github.com/ebrelsford/Leaflet.snogylop
(function(){var isFlat=L.LineUtil.isFlat?L.LineUtil.isFlat:L.LineUtil._flat;function defineSnogylop(L){var worldLatlngs=[L.latLng([90,180]),L.latLng([90,-180]),L.latLng([-90,-180]),L.latLng([-90,180])];if(L.version<'1.0.0'){L.extend(L.Polygon.prototype,{initialize:function(latlngs,options){worldLatlngs=(options.worldLatLngs?options.worldLatLngs:worldLatlngs);if(options&&options.invert&&!options.invertMultiPolygon){var newLatlngs=[];newLatlngs.push(worldLatlngs);newLatlngs.push(latlngs[0]);latlngs=newLatlngs}L.Polyline.prototype.initialize.call(this,latlngs,options);this._initWithHoles(latlngs)},getBounds:function(){if(this.options.invert){return new L.LatLngBounds(this._holes)}return new L.LatLngBounds(this.getLatLngs())}});L.extend(L.MultiPolygon.prototype,{initialize:function(latlngs,options){worldLatlngs=(options.worldLatLngs?options.worldLatLngs:worldLatlngs);this._layers={};this._options=options;if(options.invert){options.invertMultiPolygon=true;var newLatlngs=[];newLatlngs.push(worldLatlngs);for(var l in latlngs){newLatlngs.push(latlngs[l][0])}latlngs=[newLatlngs]}this.setLatLngs(latlngs)}})}else{var OriginalPolygon={toGeoJSON:L.Polygon.prototype.toGeoJSON};L.extend(L.Polygon.prototype,{_setLatLngs:function(latlngs){this._originalLatLngs=latlngs;if(isFlat(this._originalLatLngs)){this._originalLatLngs=[this._originalLatLngs]}if(this.options.invert){worldLatlngs=(this.options.worldLatLngs?this.options.worldLatLngs:worldLatlngs);var newLatlngs=[];newLatlngs.push(worldLatlngs);for(var l in latlngs){newLatlngs.push(latlngs[l])}latlngs=[newLatlngs]}L.Polyline.prototype._setLatLngs.call(this,latlngs)},getBounds:function(){if(this._originalLatLngs){return new L.LatLngBounds(this._originalLatLngs)}return new L.LatLngBounds(this.getLatLngs())},getLatLngs:function(){return this._originalLatLngs},toGeoJSON:function(precision){if(!this.options.invert){return OriginalPolygon.toGeoJSON.call(this,precision)}var holes=!isFlat(this._originalLatLngs),multi=holes&&!isFlat(this._originalLatLngs[0]);var coords=L.GeoJSON.latLngsToCoords(this._originalLatLngs,multi?2:holes?1:0,true,precision);if(!holes){coords=[coords]}return L.GeoJSON.getFeature(this,{type:(multi?'Multi':'')+'Polygon',coordinates:coords})}})}}if(typeof define==='function'&&define.amd){define(['leaflet'],function(L){defineSnogylop(L)})}else{defineSnogylop(L)}})();

$(function(){
    var map = new L.Map("leaflet");
    map.attributionControl.setPrefix('');
    var OpenStreetMap_HOT = L.tileLayer('https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, <a href="https://www.hotosm.org/" target="_blank">HOT OSM</a>'
    });
    map.addLayer(OpenStreetMap_HOT);

    if ( window.gss && window.mapit_id ) {
        // Local authority area page
        var areas = L.featureGroup().addTo(map);

        function area_loaded(data) {
            var area = new L.GeoJSON(data);
            area.on('dblclick', function(e){
                var z = map.getZoom() + (e.originalEvent.shiftKey ? -1 : 1);
                map.setZoomAround(e.containerPoint, z);
            });
            areas.addLayer(area);
            map.fitBounds(areas.getBounds());
        };

        function teams_loaded(data) {
            var area = new L.GeoJSON(data, {
                onEachFeature: function (feature, layer) {
                    layer.bindPopup('<p><a href="'+feature.properties.url+'">'+feature.properties.name+'</a></p>');
                }
            });
            areas.addLayer(area);
        }

        $.ajax({
            dataType: "json",
            url: "/area/" + window.mapit_id + "/geometry",
            success: area_loaded
        });

        $.ajax({
            dataType: "json",
            url: "/area/" + window.gss + "/teams",
            success: teams_loaded
        });

    }

    if ( window.user_latlon ) {
        var user_marker = new L.circleMarker(
            window.user_latlon,
            {
                color: "#ffffff",
                fillColor: "#0d6efd",
                fillOpacity: 1,
                className: "current-location-marker",
                pane: "markerPane",
                interactive: false
            }
        ).addTo(map);
        map.setView(window.user_latlon, 14);
    } else if ( window.team_latlon ) {
        map.setView(window.team_latlon, 14);
    }

    if ( window.team_boundary_geojson ) {
        var team_boundary = L.geoJSON(
            window.team_boundary_geojson,
            {
                invert: true,
                renderer: L.svg({ padding: 1 }),
                interactive: false,
                style: {
                    color: "#FCBF49",
                    weight: 4,
                    fillColor: "#fff",
                    fillOpacity: 0.6
                }
            }
        ).addTo(map);
        map.fitBounds(team_boundary.getBounds());
    }

    // Reload map, if it is inside a bootstrap collapse element
    // that has just been shown (as happens for logged-in team
    // members switching to the public view of their team page).
    $(document).on('shown.bs.collapse', function(e){
        if ( map && e.target.contains(map._container) ) {
            map.invalidateSize();
            if ( team_boundary ) {
                map.fitBounds(team_boundary.getBounds());
            } else if ( window.user_latlon ) {
                map.setView(window.user_latlon, 14);
            } else if ( window.team_latlon ) {
                map.setView(window.team_latlon, 14);
            }
        }
    });
});

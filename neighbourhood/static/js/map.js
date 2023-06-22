import $ from '../jquery/jquery.esm.js'
import L from '../leaflet/leaflet-1.9.3.esm.js'

$(function(){
    /* for some reason leaflet's icon path detection is failing for some icons
     * so hard code it for now */
    L.Icon.Default.prototype.options["imagePath"] = "/static/leaflet/images/";
    var map = new L.Map("leaflet");
    map.attributionControl.setPrefix('');
    var osm = new L.TileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: 'Map © <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 18
    });
    map.addLayer(osm);

    var mapit = mapit || {};
    mapit.area_loaded = function(data) {
        var area = new L.GeoJSON(data);
        area.on('dblclick', function(e){
            var z = map.getZoom() + (e.originalEvent.shiftKey ? -1 : 1);
            map.setZoomAround(e.containerPoint, z);
        });
        mapit.areas.addLayer(area);
        map.fitBounds(mapit.areas.getBounds());
    };

    mapit.teams_loaded = function(data) {
        var area = new L.GeoJSON(data, {
            onEachFeature: function (feature, layer) {
                layer.bindPopup('<p><a href="'+feature.properties.url+'">'+feature.properties.name+'</a></p>');
            }
        });
        mapit.areas.addLayer(area);
    }
    mapit.areas = L.featureGroup().addTo(map);

    $.ajax({
      dataType: "json",
      url: "/area/" + mapit_id + "/geometry",
      success: mapit.area_loaded
    });

    $.ajax({
      dataType: "json",
      url: "/area/" + gss + "/teams",
      success: mapit.teams_loaded
    });

});

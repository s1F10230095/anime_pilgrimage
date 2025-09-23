const markers = [];

{% for spot in spots %}
  const genre = "{{ spot.spot_type }}";
  const marker = L.marker([{{ spot.latitude }}, {{ spot.longitude }}]).addTo(map)
    .bindPopup(`<img src="{{ spot.image_url }}" class="popup-img"><strong>{{ spot.title }}</strong><br>{{ spot.location }}<br>{{ spot.description }}`);
  marker.genre = genre;
  markers.push(marker);
{% endfor %}

document.getElementById("genreFilter").addEventListener("change", function() {
  const selected = this.value;
  markers.forEach(m => {
    if (selected === "all" || m.genre.includes(selected)) {
      map.addLayer(m);
    } else {
      map.removeLayer(m);
    }
  });
});

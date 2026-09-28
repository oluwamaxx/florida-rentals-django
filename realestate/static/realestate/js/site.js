(function(){
  function esc(s){const m={'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;',"\"":'&quot;'};return String(s??'').replace(/[&<>'"]/g,c=>m[c]);}

  async function geocode(item){
    if(item.lat!=null && item.lng!=null && Number.isFinite(Number(item.lat)) && Number.isFinite(Number(item.lng))) {
      return [Number(item.lat),Number(item.lng)];
    }
    if(!item.geocode_url) return null;
    try{
      const r=await fetch(item.geocode_url,{headers:{'Accept':'application/json'},cache:'no-store'});
      if(!r.ok) return null;
      const j=await r.json();
      if(j.ok && Number.isFinite(Number(j.lat)) && Number.isFinite(Number(j.lng))) {
        return [Number(j.lat),Number(j.lng)];
      }
    }catch(e){}
    return null;
  }

  function addBasemap(map){
    // Carto's dark basemap is the primary layer because it works well with the
    // site's dark/green design. OpenStreetMap is retained as an automatic fallback.
    const cartoUrl='https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png';
    const osmUrl='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
    const options={maxZoom:19,subdomains:'abcd',attribution:'© OpenStreetMap contributors © CARTO'};
    let current=L.tileLayer(cartoUrl,options).addTo(map);
    let errors=0;
    let switched=false;
    current.on('tileerror',function(){
      errors += 1;
      // Switch providers after repeated failures rather than leaving an empty map.
      if(!switched && errors >= 2){
        switched=true;
        map.removeLayer(current);
        current=L.tileLayer(osmUrl,{maxZoom:19,attribution:'© OpenStreetMap contributors'}).addTo(map);
      }
    });
    return current;
  }

  function popupHtml(item){
    return `<div class="popup">${item.image?`<img src="${esc(item.image)}" alt="">`:''}<strong>${esc(item.title)}</strong><span>${esc(item.address)}</span><br><b>$${esc(item.rent)}/mo</b><br><span>${esc(item.bedrooms)} Beds · ${esc(item.bathrooms)} Baths · ${esc(item.sqft)} Sq Ft</span><a class="btn btn-primary" href="${esc(item.detail_url)}">View Property</a></div>`;
  }

  async function initMap(el){
    if(!window.L || !el) return;

    const defaultLat=Number(el.dataset.defaultLat || 27.9944);
    const defaultLng=Number(el.dataset.defaultLng || -81.7603);
    const map=L.map(el,{scrollWheelZoom:false,zoomControl:true}).setView([defaultLat,defaultLng],7);
    addBasemap(map);

    // Give Leaflet the correct dimensions after the map is attached to the page.
    setTimeout(()=>map.invalidateSize(true),50);
    window.addEventListener('resize',()=>map.invalidateSize(true));

    const endpoint=el.dataset.mapEndpoint;
    let data=[];
    try{
      const r=await fetch(endpoint,{headers:{'Accept':'application/json'},cache:'no-store'});
      if(!r.ok) throw new Error('Map data request failed: '+r.status);
      data=(await r.json()).listings||[];
    }catch(e){
      el.innerHTML='<div class="map-empty">We could not load the available home locations. Please refresh the page.</div>';
      return;
    }

    if(!data.length){
      el.innerHTML='<div class="map-empty">No available homes at this time.</div>';
      return;
    }

    const markers=new Map();
    const bounds=[];
    const requestedId=window.INITIAL_MAP_SELECTED_ID ? String(window.INITIAL_MAP_SELECTED_ID) : null;

    for(let i=0;i<data.length;i++){
      const item=data[i];
      const pos=await geocode(item);
      if(pos){
        const popup=popupHtml(item);
        const marker=L.marker(pos).addTo(map).bindPopup(popup);
        markers.set(String(item.id),marker);
        bounds.push(pos);
      }
      // Nominatim asks clients to keep automated requests to no more than
      // one request per second. Only uncached listings use this endpoint.
      if(item.lat==null || item.lng==null){
        await new Promise(resolve=>setTimeout(resolve,1100));
      }
    }

    if(!markers.size){
      el.innerHTML='<div class="map-empty">We could not locate the available home addresses right now. Please refresh and try again.</div>';
      return;
    }

    // Always start with an available home. A requested tour property takes priority;
    // otherwise the first available listing returned by Django is selected.
    const defaultId=requestedId && markers.has(requestedId) ? requestedId : markers.keys().next().value;
    const defaultMarker=markers.get(defaultId);
    const selectedPos=defaultMarker.getLatLng();

    if(requestedId && markers.has(requestedId)){
      map.setView(selectedPos,15,{animate:false});
      defaultMarker.openPopup();
    }else{
      // Show all available homes, then focus on the first available home and open it.
      map.fitBounds(bounds,{padding:[35,35],maxZoom:13});
      setTimeout(()=>{
        map.setView(selectedPos,Math.max(map.getZoom(),14),{animate:false});
        defaultMarker.openPopup();
      },80);
    }

    setTimeout(()=>map.invalidateSize(true),100);

    document.querySelectorAll('[data-map-listing-id]').forEach(link=>{
      link.addEventListener('click',function(e){
        const id=this.dataset.mapListingId;
        const marker=markers.get(String(id));
        if(!marker) return;
        e.preventDefault();
        map.setView(marker.getLatLng(),Math.max(map.getZoom(),15),{animate:true});
        marker.openPopup();
      });
    });
  }

  document.addEventListener('DOMContentLoaded',()=>{
    if(window.INITIAL_MAP_ID) initMap(document.getElementById(window.INITIAL_MAP_ID));
  });
})();

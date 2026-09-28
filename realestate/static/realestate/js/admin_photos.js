(function(){
  function updateRows(container){
    const rows = container.querySelectorAll('.dynamic-listingphoto');
    rows.forEach((row, i) => {
      const input = row.querySelector('input[name$="-order"]');
      if (input) input.value = i + 1;
      row.style.cursor = 'grab';
    });
  }
  function init(){
    document.querySelectorAll('.inline-group').forEach(group => {
      if (!group.querySelector('input[name$="-order"]')) return;
      let dragged = null;
      group.querySelectorAll('.dynamic-listingphoto').forEach(row => {
        row.draggable = true;
        row.addEventListener('dragstart', e => { dragged = row; row.style.opacity = '.45'; e.dataTransfer.effectAllowed='move'; });
        row.addEventListener('dragend', () => { row.style.opacity=''; dragged=null; updateRows(group); });
        row.addEventListener('dragover', e => { e.preventDefault(); if(dragged && dragged!==row){ const r=row.getBoundingClientRect(); const after=e.clientY > r.top+r.height/2; row.parentNode.insertBefore(dragged, after ? row.nextSibling : row); }});
      });
      updateRows(group);
    });
  }
  document.addEventListener('DOMContentLoaded', init);
})();

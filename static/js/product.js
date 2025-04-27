$(function(){
  attachClose();
  let selectedProduct, products=[];
  const $select = $('#product-select');
  const $btns = $('.box-btn.product-btn');
  const $warning = $('#plot-warning');

  function init(){
    $.get('/api/products/options', function(data){
      products = data.products || [];
      if(!products.length){
        showPopup('<div class="alert alert-warning">No products available.</div>');
        return;
      }
      $select.empty();
      products.forEach(p=> $select.append(`<option value="${p}">${p}</option>`));
      selectedProduct = products[0];
      $select.val(selectedProduct);
      updateButtonsAndFetch();
    });
    $select.on('change', function(){ selectedProduct = $(this).val(); updateButtonsAndFetch(); });
  }

  function updateButtonsAndFetch(){
    $btns.each(function(){
      const label = $(this).text().trim();
      let file = '';
      if(label === 'Qty by Country') file = `${selectedProduct}_qty_by_country.csv`;
      else if(label === 'Qty by Month') file = `${selectedProduct}_qty_by_month.csv`;
      else if(label === 'Qty by Hour') file = `${selectedProduct}_qty_by_hour.csv`;
      else if(label === 'Qty by Day of Week') file = `${selectedProduct}_qty_by_dayofweek.csv`;
      else if(label === 'Summary') file = `${selectedProduct}_summary.txt`;
      const url = `/api/product/${encodeURIComponent(file)}`;
      $(this).data('url', url);
    });
    // initial click removed to avoid auto-popup on load
  }

  function onBtnClick(){
    const url = $(this).data('url');
    showPopup('<div class="alert alert-info">Loading...</div>');
    $.get(url, function(data){ renderData(data); })
      .fail(function(xhr){
        if(xhr.status === 404){
          showPopup('<div class="alert alert-danger">No report exists for this product/report type.<br><button id="generate-report" class="btn btn-warning mt-2">Generate Report</button></div>');
          $(document).off('click', '#generate-report').on('click', '#generate-report', function(){
            showPopup('<div class="alert alert-info">Generating report, please wait...</div>');
            $.ajax({
              url: '/api/product/generate',
              method: 'POST',
              contentType: 'application/json',
              data: JSON.stringify({product: selectedProduct}),
              success: function(){
                // auto-fetch the report after generation
                $.get(url, function(data){ renderData(data); })
                  .fail(function(){ showPopup('<div class="alert alert-danger">Still no report available. Please try again later.</div>'); });
              },
              error: function(xhr){ showPopup('<div class="alert alert-danger">Failed to generate report: ' + xhr.responseText + '</div>'); }
            });
          });
        } else {
          showPopup('<div class="alert alert-danger">Error fetching report.</div>');
        }
      });
  }

  function renderData(data){
    let html = '';
    if(typeof data === 'string') data = JSON.parse(data);
    if(Array.isArray(data)){
      if(data.length > 0 && Object.keys(data[0]).length >= 2){
        const keys = Object.keys(data[0]);
        const x = data.map(r => r[keys[0]]), y = data.map(r => r[keys[1]]);
        Plotly.newPlot('report-plot', [{ x, y, mode: 'markers' }], { title: `${keys[0]} vs ${keys[1]}`, xaxis: {title: keys[0]}, yaxis: {title: keys[1]}, autosize: true }, {responsive: true});
        $warning.hide();
      } else {
        Plotly.purge('report-plot');
        $warning.text('Not enough numeric columns to plot.').show();
      }
      html = `<table class="table table-bordered"><thead><tr>${Object.keys(data[0]).map(c=>`<th>${c}</th>`).join('')}</tr></thead><tbody>${data.map(r=>`<tr>${Object.values(r).map(v=>`<td>${v}</td>`).join('')}</tr>`).join('')}</tbody></table>`;
    } else if(data.text){
      html = `<pre>${data.text}</pre>`;
      Plotly.purge('report-plot');
      $warning.text('No chart for this report type.').show();
    }
    showPopup(html);
  }

  $btns.on('click', onBtnClick);
  init();
});

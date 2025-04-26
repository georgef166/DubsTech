$(function(){
  let selectedMonth, selectedYear, validOptions = [];
  const $month = $('#month-select'), $year = $('#year-select');
  const $btns = $('#report-btn-group .report-btn');
  const $warning = $('#plot-warning');

  function loadOptions(){
    $.get('/api/monthly/options', function(data){
      validOptions = data.options;
      const months = [...new Set(validOptions.map(o=>o.month))];
      const years = [...new Set(validOptions.map(o=>o.year))];
      $month.empty();
      months.forEach(m=> $month.append(`<option value="${m}">${m}</option>`));
      $year.empty();
      years.forEach(y=> $year.append(`<option value="${y}">${y}</option>`));
      selectedMonth = months[0]; selectedYear = years[0];
      $month.val(selectedMonth); $year.val(selectedYear);
      updateAndFetch();
    });
  }

  function updateAndFetch(){
    selectedMonth = $month.val(); selectedYear = $year.val();
    const exists = validOptions.some(o=>o.month===selectedMonth && o.year==selectedYear);
    if(!exists){ showPopup(`<div class="alert alert-danger">No report exists for ${selectedMonth} ${selectedYear}.</div>`); return; }
    $btns.each(function(){
      const type = $(this).data('type');
      $(this).data('url', `/api/monthly/${type}?month=${encodeURIComponent(selectedMonth)}&year=${encodeURIComponent(selectedYear)}`);
    });
    $btns.first().click();
  }

  function onBtnClick(){
    const url = $(this).data('url');
    showPopup('<div class="alert alert-info">Loading...</div>');
    $.get(url, function(data){ renderData(data); })
      .fail(function(){ showPopup('<div class="alert alert-danger">Error fetching report.</div>'); });
  }

  function renderData(data){
    let html = '';
    if(typeof data==='string') data = JSON.parse(data);
    if(Array.isArray(data)){
      if(data.length>0 && Object.keys(data[0]).length>=2){
        const keys = Object.keys(data[0]);
        const x = data.map(r=>r[keys[0]]), y = data.map(r=>r[keys[1]]);
        Plotly.newPlot('report-plot', [{ x, y, mode:'markers' }], { title:`${keys[0]} vs ${keys[1]}`, xaxis:{title:keys[0]}, yaxis:{title:keys[1]}, autosize:true }, { responsive:true });
        $warning.hide();
      } else { Plotly.purge('report-plot'); $warning.text('Not enough numeric columns to plot.').show(); }
      html = `<table class="table table-bordered"><thead><tr>${Object.keys(data[0]).map(c=>`<th>${c}</th>`).join('')}</tr></thead><tbody>${data.map(r=>`<tr>${Object.values(r).map(v=>`<td>${v}</td>`).join('')}</tr>`).join('')}</tbody></table>`;
    } else if(data.text){ html = `<pre>${data.text}</pre>`; Plotly.purge('report-plot'); $warning.text('No chart for this report type.').show(); }
    showPopup(html);
  }

  $month.on('change', updateAndFetch);
  $year.on('change', updateAndFetch);
  $btns.on('click', onBtnClick);
  attachClose();
  loadOptions();
});
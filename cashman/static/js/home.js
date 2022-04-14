$(document).ready(function () {
  var citynames = new Bloodhound({
    datumTokenizer: Bloodhound.tokenizers.obj.whitespace("name"),
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    prefetch: {
      url: "https://bootstrap-tagsinput.github.io/bootstrap-tagsinput/examples/assets/citynames.json",
      filter: function (list) {
        return $.map(list, function (cityname) {
          return { name: cityname };
        });
      },
    },
  });
  citynames.initialize();

  var elt = $("#txn-tag");

  elt.tagsinput({
    typeaheadjs: {
      name: "citynames",
      displayKey: "name",
      valueKey: "name",
      source: citynames.ttAdapter(),
    },
  });

  $("#userForm").hide();

  $("#txn-add-btn").click(() => {
    $("#userForm").toggle(500);
  });

  // Attach a submit handler to the form
  $("#userForm").submit(function (event) {
    // Stop form from submitting normally
    event.preventDefault();

    const form = $(this);
    const formData = {
      title: $("#title").val(),
      amount: $("#amount").val(),
      txn_date: $("#txn_date").val(),
      type: $("#type").val(),
      category: $("#category").val(),
      brand: $("#brand").val(),
      description: $("#description").val(),
      group_id: group_id,
      tags: elt.data("tagsinput").itemsArray,
    };
    // alert(`${JSON.stringify(formData)}`)
    $.ajax({
      type: form.attr("method"),
      url: form.attr("action"),
      data: JSON.stringify(formData),
      dataType: "json",
      contentType: "application/json; charset=utf-8",
      success: function (response) {
        // refresh the list
        $("#userForm").trigger("reset");
        location.reload();
      },
      error: function (error) {
        console.log(JSON.stringify(error));
        alert("Something went wrong from our side. Please try later!");
      },
    });
  });

  new Chart("myChart", {
    type: "line",
    data: {
      labels: xValues,
      datasets: [
        {
          fill: false,
          lineTension: 0,
          backgroundColor: "#ffc107",
          borderColor: "#ffc107",
          data: incomeValues,
        },
        {
          fill: false,
          lineTension: 0,
          backgroundColor: "#17a2b8",
          borderColor: "#17a2b8",
          data: expenceValues,
        },
        {
          fill: false,
          lineTension: 0,
          backgroundColor: "#28a745",
          borderColor: "#28a745",
          data: netValues,
        },
      ],
    },
    options: {
      legend: { display: false },
    },
  });

  new Chart("dailyViewChart", {
    type: "line",
    data: {
      labels: day_view_x_values,
      datasets: [
        {
          fill: false,
          lineTension: 0,
          backgroundColor: "#ffc107",
          borderColor: "#ffc107",
          data: day_view_income_values,
        },
        {
          fill: false,
          lineTension: 0,
          backgroundColor: "#17a2b8",
          borderColor: "#17a2b8",
          data: day_view_expence_values,
        },
        {
          fill: false,
          lineTension: 0,
          backgroundColor: "#28a745",
          borderColor: "#28a745",
          data: day_view_net_values,
        },
      ],
    },
    options: {
      legend: { display: false },
    },
  });
});

function deleteTxn(id) {
  $.ajax({
    type: "DELETE",
    url: `http://localhost:5000/transactions/${id}`,
    success: function (response) {
      location.reload();
    },
    error: function (error) {
      console.log(JSON.stringify(error));
      alert("Something went wrong from our side. Please try later!");
    },
  });
}

function downloadFile() {
  const urlToSend = `http://localhost:5000/pdf/${group_id}/${group_name}`;
  const req = new XMLHttpRequest();
  req.open("GET", urlToSend, true);
  req.responseType = "blob";
  req.onload = function (event) {
      const blob = req.response;
      const fileNameStrTemp = req.getResponseHeader("content-disposition").split(";")[1];
      const fileName = fileNameStrTemp.substr(10, fileNameStrTemp.length)
      const link=document.createElement('a');
      link.href=window.URL.createObjectURL(blob);
      link.download=fileName;
      link.click();
  };
  req.send();
}
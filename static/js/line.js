new Chart(document.getElementById("line-chart"), {
    type: 'line',
    data: {
      labels: ["10분", "20분", "30분", "40분", "50분"],
      legend: {
        display: false
      },
    
    datasets: [
        {
          label: "1",
          fill: true,
          backgroundColor: "rgba(179,181,198,0.2)",
          borderColor: 'rgb(75, 192, 192)',
          pointBorderColor: "#fff",
          pointBackgroundColor: "rgba(179,181,198,1)",
          data: [55.77,45.61,42.69,50.62,34.82]
        }
      ]
      
    },
});

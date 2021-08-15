new Chart(document.getElementById("radar-chart"), {
    type: 'radar',
    data: {
      labels: ["CS수급", "적극성", "시야점수", "교전 기여도", "캐리력"],
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
          data: [5, 5, 5, 5, 5]
        }
      ]
      
    },
});

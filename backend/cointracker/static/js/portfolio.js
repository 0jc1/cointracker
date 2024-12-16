document.addEventListener('DOMContentLoaded', () => {

    const ctx = document.getElementById('canvas1').getContext('2d');

    // Example data: each label might represent a point in time
    const data = {
        labels: ["2024-12-10", "2024-12-11", "2024-12-12", "2024-12-13", "2024-12-14"],
        datasets: [{
            label: 'Price over Time',
            data: [100, 200, 150, 300, 250], // Example USD values
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 2,
            fill: false,
            tension: 0.1
        }]
    };

    const config = {
        type: 'line',
        data: data,
        options: {
            responsive: true,
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Time'
                    },
                    // If using dates, consider using a time scale and a date adapter
                    // type: 'time',
                    // time: {
                    //   unit: 'day'
                    // }
                },
                y: {
                    title: {
                        display: true,
                        text: 'USD value'
                    },
                    beginAtZero: false
                }
            }
        }
    };

    const myChart = new Chart(ctx, config);

});
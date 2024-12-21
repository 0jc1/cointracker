// portfolio.js

document.addEventListener('DOMContentLoaded', () => {
    const ctx = document.getElementById('canvas1').getContext('2d');

    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, 'rgb(64, 174, 248)'); // Top color (semi-transparent)
    gradient.addColorStop(1, 'rgba(215, 226, 233, 0.15)');   // Bottom color (transparent)

    fetch('/api/portfolio/balance/', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'), // If using CSRF tokens
        },
        credentials: 'include', // Include cookies for authentication
    })
        .then(response => response.json())
        .then(data => {
            const chartData = {
                labels: data.labels,
                datasets: [{
                    label: 'Portfolio Balance',
                    data: data.data.map(value => parseFloat(value)),
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.3,
                    pointRadius: 0,
                    backgroundColor: gradient,
                }]
            };


            const config = {
                type: 'line',
                data: chartData,
                options: {
                    responsive: true,
                    plugins: {
                        tooltip: {
                            mode: 'index',
                            intersect: false,
                        },
                    },
                    interaction: {
                        mode: 'nearest',
                        intersect: true
                    },
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: 'Date'
                            },
                            type: 'time',
                            time: {
                                unit: 'day',
                                displayFormats: {
                                    day: 'MM-DD'
                                }
                            },
                            grid: {
                                display: false // Optional: Hide x-axis grid lines
                            }
                        },
                        y: {
                            title: {
                                display: true,
                                text: 'USD'
                            },
                            beginAtZero: false,
                            grid: {
                                color: 'rgba(127, 127, 127, 0.2)' // Light grid lines
                            }
                        }
                    },
                    elements: {
                        line: {
                            borderWidth: 2,
                        },
                    },
                    maintainAspectRatio: false, // Allows the chart to resize properly
                }
            };

            const myChart = new Chart(ctx, config);
        })
        .catch(error => {
            console.error('Error fetching portfolio balance:', error);
        });

    // Helper function to get CSRF token (if needed)
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
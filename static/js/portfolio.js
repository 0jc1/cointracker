// portfolio.js

document.addEventListener('DOMContentLoaded', () => {
    // Copy to clipboard functionality
    document.querySelectorAll('.copy-button').forEach(button => {
        button.addEventListener('click', async () => {
            const address = button.dataset.address;
            try {
                await navigator.clipboard.writeText(address);
                
                // Visual feedback
                button.classList.add('copied');
                const originalHTML = button.innerHTML;
                button.innerHTML = `
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polyline points="20 6 9 17 4 12"></polyline>
                    </svg>
                `;
                
                // Reset after 2 seconds
                setTimeout(() => {
                    button.classList.remove('copied');
                    button.innerHTML = originalHTML;
                }, 2000);
            } catch (err) {
                console.error('Failed to copy:', err);
            }
        });
    });

    // Chart setup
    const ctx = document.getElementById('canvas1').getContext('2d');
    let myChart = null;

    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, 'rgb(64, 174, 248)'); // Top color (semi-transparent)
    gradient.addColorStop(1, 'rgba(215, 226, 233, 0.15)');   // Bottom color (transparent)

    // Period button handling
    const periodButtons = document.querySelectorAll('.period-btn');
    periodButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Update active state
            periodButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            
            // Fetch new data
            fetchChartData(button.dataset.period);
        });
    });

    // Initial chart data fetch
    fetchChartData('30d');

    function fetchChartData(period) {
        fetch(`/api/portfolio/balance/?period=${period}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'), // If using CSRF tokens
            },
            credentials: 'include', // Include cookies for authentication
        })
        .then(response => response.json())
        .then(data => {
            // Destroy existing chart if it exists
            if (myChart) {
                myChart.destroy();
            }

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

            myChart = new Chart(ctx, config);
        })
        .catch(error => {
            console.error('Error fetching portfolio balance:', error);
        });
    }

    // Helper function to get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});

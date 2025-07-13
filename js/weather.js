const apiKey = "ad0505430d10317c8c9783809eb1b211"; // Replace with your API key

// Get the city name from the page (Use a `data-city` attribute in HTML)
const city = document.getElementById("weather-info").dataset.city || "Agra"; 

async function fetchWeather() {
    try {
        const weatherUrl = `https://api.openweathermap.org/data/2.5/weather?q=${city}&appid=${apiKey}&units=metric`;
        const response = await fetch(weatherUrl);
        const data = await response.json();

        // Update weather details
        document.getElementById("weather-details").innerHTML = `
            <strong>${city}</strong> <br>
            Temperature: ${data.main.temp}°C <br>
            Weather: ${data.weather[0].description} <br>
            Humidity: ${data.main.humidity}% <br>
            Wind Speed: ${data.wind.speed} m/s
        `;

        // Initialize the map with latitude and longitude
        initMap(data.coord.lat, data.coord.lon);
    } catch (error) {
        console.error("Error fetching weather data:", error);
        document.getElementById("weather-details").innerHTML = "Weather data unavailable.";
    }
}

function initMap(lat, lon) {
    var map = new google.maps.Map(document.getElementById("weather-map"), {
        center: { lat: lat, lng: lon },
        zoom: 10,
    });

    new google.maps.Marker({
        position: { lat: lat, lng: lon },
        map: map,
        title: city,
    });
}

// Load weather data on page load
document.addEventListener("DOMContentLoaded", fetchWeather);

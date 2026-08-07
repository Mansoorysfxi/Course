/*
 * Exercise 04 reference solution — Fetch, Promises, and Async/Await.
 *
 * Don't read this until you've made a genuine attempt at
 * starter/script.js.
 */

const citySelect = document.querySelector("#city-select");
const getWeatherBtn = document.querySelector("#get-weather-btn");
const triggerErrorBtn = document.querySelector("#trigger-error-btn");
const statusEl = document.querySelector("#weather-status");
const resultEl = document.querySelector("#weather-result");

const BROKEN_URL = "https://api.open-meteo.com/v1/forecast?longitude=13.41&current=temperature_2m";

async function getCurrentTemperature(latitude, longitude) {
  const response = await fetch(
    `https://api.open-meteo.com/v1/forecast?latitude=${latitude}&longitude=${longitude}&current=temperature_2m,relative_humidity_2m`
  );

  if (!response.ok) {
    throw new Error(`Weather service returned status ${response.status}`);
  }

  const data = await response.json();
  return {
    temperature: data.current.temperature_2m,
    humidity: data.current.relative_humidity_2m,
  };
}

async function fetchAndShow(url) {
  statusEl.textContent = "Loading...";
  resultEl.textContent = "";

  try {
    const response = await fetch(url);

    if (!response.ok) {
      throw new Error(`Weather service returned status ${response.status}`);
    }

    const data = await response.json();
    statusEl.textContent = "";
    resultEl.textContent = `${data.current.temperature_2m}°C, ${data.current.relative_humidity_2m}% humidity`;
  } catch (error) {
    statusEl.textContent = `Error: ${error.message}`;
  }
}

getWeatherBtn.addEventListener("click", async function () {
  const [latitude, longitude] = citySelect.value.split(",");

  statusEl.textContent = "Loading...";
  resultEl.textContent = "";

  try {
    const weather = await getCurrentTemperature(latitude, longitude);
    statusEl.textContent = "";
    resultEl.textContent = `${weather.temperature}°C, ${weather.humidity}% humidity`;
  } catch (error) {
    statusEl.textContent = `Error: ${error.message}`;
  }
});

triggerErrorBtn.addEventListener("click", function () {
  fetchAndShow(BROKEN_URL);
});

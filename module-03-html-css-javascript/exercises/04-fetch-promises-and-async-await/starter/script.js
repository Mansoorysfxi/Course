/*
 * Exercise 04 starter — Fetch, Promises, and Async/Await.
 *
 * Implement each TODO below. See INSTRUCTIONS.md for exactly what each
 * piece must do and how it will be checked. This calls the real, live
 * Open-Meteo API — you need an internet connection to test this.
 */

const citySelect = document.querySelector("#city-select");
const getWeatherBtn = document.querySelector("#get-weather-btn");
const triggerErrorBtn = document.querySelector("#trigger-error-btn");
const statusEl = document.querySelector("#weather-status");
const resultEl = document.querySelector("#weather-result");

// A deliberately broken URL: Open-Meteo REQUIRES a latitude parameter, and
// this URL doesn't supply one. The real API responds with a 400-range
// error status. Use this for the "Trigger a Deliberate Error" button.
const BROKEN_URL = "https://api.open-meteo.com/v1/forecast?longitude=13.41&current=temperature_2m";

// TODO 1: implement this async function.
// It must:
//   - fetch https://api.open-meteo.com/v1/forecast?latitude=<lat>&longitude=<lon>&current=temperature_2m,relative_humidity_2m
//   - check response.ok; if false, throw a real Error with a useful message
//   - parse the JSON body
//   - return { temperature: <number>, humidity: <number> } pulled from
//     data.current.temperature_2m and data.current.relative_humidity_2m
async function getCurrentTemperature(latitude, longitude) {
  // TODO: implement this.
}

// TODO 2: attach a click listener to getWeatherBtn that:
//   - reads citySelect.value (a "latitude,longitude" string) and splits it
//     on the comma into two numbers
//   - sets statusEl's text to "Loading..." and clears resultEl
//   - calls getCurrentTemperature(...) inside a try/catch
//   - on success: clears statusEl and writes something like
//     "18.4°C, 62% humidity" into resultEl
//   - on failure: writes a clear error message into statusEl

// TODO 3: attach a click listener to triggerErrorBtn that runs the SAME
// loading -> fetch(BROKEN_URL) -> success-or-error DOM update logic as
// TODO 2, but against BROKEN_URL directly, to prove your error handling
// genuinely works. (You may factor shared logic into a helper function if
// you like — not required.)

function getToday(): string {
  return new Date().toLocaleDateString('en-CA'); // YYYY-MM-DD format
}

function getCurrentTime(): string {
  return new Date().toLocaleTimeString('en-CA', { hour12: false, hour: '2-digit', minute: '2-digit' }); // HH:MM format
}

export { getToday, getCurrentTime };

//en-CA is a common trick to get YYYY-MM-DD without manual formatting.
// /SO 8601 (YYYY-MM-DD) is the international standard for date
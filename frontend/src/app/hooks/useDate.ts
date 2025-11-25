function getToday(): string {
  return new Date().toISOString().slice(0, 10);
}

export { getToday };
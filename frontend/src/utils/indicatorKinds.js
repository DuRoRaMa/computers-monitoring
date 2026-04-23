const RANGE_INDICATORS = new Set([
  "CPU загрузка",
  "RAM занятость",
  "CPU температура",
  "Диск скорость",
  "Диск заполнение",
  "Сеть пропускная",
  "Процессы количество",
]);

const SCALAR_INDICATORS = new Set([
  "Сервисы состояние",
]);

export const getIndicatorInputMode = (indicatorName) => {
  if (RANGE_INDICATORS.has(indicatorName)) {
    return "range";
  }

  if (SCALAR_INDICATORS.has(indicatorName)) {
    return "scalar";
  }

  return null;
};
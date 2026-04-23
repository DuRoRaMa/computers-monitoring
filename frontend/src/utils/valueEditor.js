export const createValueEditor = (mode = "empty") => ({
  mode, // empty | scalar | range
  scalar: "",
  min: "",
  max: "",
  minInclusive: true,
  maxInclusive: true,
});

export const parseValueText = (valueText) => {
  const text = (valueText || "").trim();

  if (!text) {
    return createValueEditor("empty");
  }

  const match = text.match(
    /^([\[\(])\s*(-?\d+(?:[.,]\d+)?)\s*;\s*(-?\d+(?:[.,]\d+)?)\s*([\]\)])$/
  );

  if (match) {
    return {
      mode: "range",
      scalar: "",
      min: match[2].replace(",", "."),
      max: match[3].replace(",", "."),
      minInclusive: match[1] === "[",
      maxInclusive: match[4] === "]",
    };
  }

  return {
    mode: "scalar",
    scalar: text,
    min: "",
    max: "",
    minInclusive: true,
    maxInclusive: true,
  };
};

export const validateValueEditor = (editor, { allowEmpty = true } = {}) => {
  if (!editor || !editor.mode) {
    return {
      valid: false,
      message: "Некорректное значение",
      fields: {},
    };
  }

  if (editor.mode === "empty") {
    return {
      valid: allowEmpty,
      message: allowEmpty ? "" : "Значение обязательно",
      fields: {},
    };
  }

  if (editor.mode === "scalar") {
    const scalar = (editor.scalar || "").trim();
    const valid = scalar.length > 0;

    return {
      valid,
      message: valid ? "" : "Введите текстовое значение",
      fields: {
        scalar: !valid,
      },
    };
  }

  if (editor.mode === "range") {
    const min = Number(editor.min);
    const max = Number(editor.max);

    const minInvalid = Number.isNaN(min);
    const maxInvalid = Number.isNaN(max);
    const orderInvalid = !minInvalid && !maxInvalid && min >= max;

    return {
      valid: !minInvalid && !maxInvalid && !orderInvalid,
      message:
        minInvalid || maxInvalid
          ? "Введите обе границы диапазона"
          : orderInvalid
          ? "Левая граница должна быть меньше правой"
          : "",
      fields: {
        min: minInvalid || orderInvalid,
        max: maxInvalid || orderInvalid,
      },
    };
  }

  return {
    valid: false,
    message: "Неизвестный тип значения",
    fields: {},
  };
};

export const formatValueEditor = (editor) => {
  if (!editor || editor.mode === "empty") {
    return "";
  }

  if (editor.mode === "scalar") {
    return (editor.scalar || "").trim();
  }

  const left = editor.minInclusive ? "[" : "(";
  const right = editor.maxInclusive ? "]" : ")";

  return `${left}${String(editor.min).trim()};${String(editor.max).trim()}${right}`;
};
export function isDateField(fieldPath) {
  return /(^|\.)date(_|$)/i.test(String(fieldPath || ""));
}

export function toFrDate(value) {
  if (value == null || value === "") return "";

  if (value instanceof Date && !Number.isNaN(value.getTime())) {
    const dd = String(value.getDate()).padStart(2, "0");
    const mm = String(value.getMonth() + 1).padStart(2, "0");
    const yyyy = String(value.getFullYear());
    return `${dd}/${mm}/${yyyy}`;
  }

  const raw = String(value);
  const isoDateMatch = raw.match(/^(\d{4})-(\d{2})-(\d{2})$/);
  if (isoDateMatch) return `${isoDateMatch[3]}/${isoDateMatch[2]}/${isoDateMatch[1]}`;

  const isoDateTimeMatch = raw.match(/^(\d{4})-(\d{2})-(\d{2})T/);
  if (isoDateTimeMatch)
    return `${isoDateTimeMatch[3]}/${isoDateTimeMatch[2]}/${isoDateTimeMatch[1]}`;

  return raw;
}

export function toDate(input) {
  if (!input) return null;
  if (input instanceof Date) {
    const d = new Date(input);
    d.setHours(0, 0, 0, 0);
    return d;
  }
  const s = String(input);
  const dmyMatch = s.match(/^(\d{1,2})\/(\d{1,2})\/(\d{4})$/);
  if (dmyMatch) {
    const d = new Date(Number(dmyMatch[3]), Number(dmyMatch[2]) - 1, Number(dmyMatch[1]));
    d.setHours(0, 0, 0, 0);
    return d;
  }
  const isoMatch = s.match(/^(\d{4})-(\d{2})-(\d{2})/);
  if (isoMatch) {
    const d = new Date(Number(isoMatch[1]), Number(isoMatch[2]) - 1, Number(isoMatch[3]));
    d.setHours(0, 0, 0, 0);
    return d;
  }
  return null;
}

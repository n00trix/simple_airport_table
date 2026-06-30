import readline from 'node:readline/promises';
import { stdin as input, stdout as output } from 'node:process';

const airport = (
  await readline
    .createInterface({ input, output })
    .question('Введите аэропорт (например SVO): ')
).trim();
const url =
  `https://timetable.kupibilet.ru/api/v1/schedule/departure/${airport}`;
const res = await fetch(url);
if (!res.ok) throw new Error(`HTTP ${res.status}`);

const data = await res.json();
const rows = Array.isArray(data) ? data : [data];

const tableRows = [];
for (const item of rows) {
  tableRows.push({
    time: `${item.arrival_time ?? ''}`,
    race: `${item.operating_carrier ?? ''} ${item.number ?? ''}`.trim(),
    terminal: `${item.arrival_terminal ?? ''}`,
    departure: `${item.arrival_city_name ?? ''}`,
    gate: `${item.arrival_gate ?? ''}`,
  });
}

console.log(
  [
    '| Время | Рейс | Терминал | Направление | Ворота |',
    ...tableRows.map(
      (r) =>
        `| ${r.time} | ${r.race} | ${r.terminal} | ${r.departure} | ${r.gate} |`,
    ),
  ].join('\n'),
);

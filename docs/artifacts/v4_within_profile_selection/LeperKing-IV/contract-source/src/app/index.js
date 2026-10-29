// Import required libraries
const moment = require('moment-jalaali');
const express = require('express');

// Create an Express app and set the port to 8000
const app = express();
const port = 8000;

// Load Persian settings for moment.js
moment.loadPersian({ dialect: 'persian-modern' });

// Set Express to use both JSON and URL-encoded formats
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// GET /today: Return today's date in various formats
app.get('/today', (req, res) => {
  const date = moment();
  res.json({
    data: {
      year: date.format('jYYYY'),
      month: date.format('jMM'),
      day: date.format('jDD'),
      dayName: date.format('dddd'),
      monthName: date.format('jMMMM'),
      time: date.format('LTS'),
    },
  });
});

// POST /format: Format a date in Miladi format to Jalaali format
app.post('/format', (req, res) => {
  const { date, format } = req.body;
  const formattedDate = moment(date).format(format);
  res.json({ data: formattedDate });
});

// GET /calendar/:year: Return a calendar for the given year
app.get('/calendar/:year', (req, res) => {
  const year = req.params.year;
  const data = [];

  for (let month = 1; month <= 12; month++) {
    const monthName = moment(`${year}/${month}`, 'jYYYY/jM');
    const startMonth = moment(`${year}/${month}`, 'jYYYY/jM');
    const startMonthWeek = startMonth.startOf('week');

    const weeks = [];
    for (let i = 0; i < 6; i++) {
      weeks.push([]);
      for (let j = 0; j < 7; j++) {
        weeks[i].push(startMonthWeek.format('jDD'));
        startMonthWeek.add(1, 'day');
      }
    }

    data.push({
      year,
      monthName: monthName.format('jMMMM'),
      weeks,
    });
  }

  res.json({ data });
});

// GET /calendar/:year/:month: Return a calendar for the given month
app.get('/calendar/:year/:month', (req, res) => {
  const year = req.params.year;
  const month = req.params.month;
  const data = [];

  const monthName = moment(`${year}/${month}`, 'jYYYY/jM');
  const startMonth = moment(`${year}/${month}`, 'jYYYY/jM');
  const startMonthWeek = startMonth.startOf('week').add(1, 'day');

  const weeks = [];
  for (let i = 0; i < 6; i++) {
    weeks.push([]);
    for (let j = 0; j < 7; j++) {
      weeks[i].push(startMonthWeek.format('jDD'));
      startMonthWeek.add(1, 'day');
    }
  }

  data.push({
    year,
    monthName: monthName.format('jMMMM'),
    weeks,
  });

  res.json({ data });
});

// GET /calendar/:year/:month/:day: Return information about the given day
app.get('/calendar/:year/:month/:day', (req, res) => {
  const year = req.params.year;
  const month = req.params.month;
  const day = req.params.day;
  const date = `${year}/${month}/${day}`;
  const mome = moment(date, 'jYYYY/jM/jD');
  const info = {
    year,
    month,
    day,
    date,
    dayOfMonth: mome.format('jD'),
    dayOfMonth_th: mome.format('jDo'),
    dayOfYear: mome.format('jDDD'),
    dayName: mome.format('dddd'),
    dayOfWeek: mome.format('do'),
  };

  res.json({ date: info });
});

// Start the app
app.listen(port, () => {
  console.log(`App listening on port ${port}`);
});
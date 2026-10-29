### Calendar-api
Calendar api with express.js that use the moment-jalali to indicate the date jalali. The api contains these endpoints:
* /today - return today date in jalali
* /format - convert a date to jalali
* /calendar/:year - return calendar of the year
* /calendar/:year/:month - return calendar of the moth
* /calendar/:year/:month/:day - return the detail of date

### Deployment
Deployment is wih docker which you can find docker file in the root directory
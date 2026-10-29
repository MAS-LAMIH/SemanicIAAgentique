const httpStatus = require('http-status');
const catchAsync = require('../utils/catchAsync');
const { eventService } = require('../services');
const ApiError = require('../utils/ApiError');

const createEvent = catchAsync(async (req, res) => {
  const event = await eventService.createEvent({
    ...req.body,
    createdBy: req.user.id,
  });
  res.status(httpStatus.CREATED).send(event);
});

const getEvent = catchAsync(async (req, res) => {
  const userId = req.user.id;

  const filter = {
    $or: [{ createdBy: userId }, { attendees: userId }],
    ...(req.query.startDate && { startTime: { $gte: new Date(req.query.startDate) } }),
    ...(req.query.endDate && { endTime: { $lte: new Date(req.query.endDate) } }),
    ...(req.query.status && { status: req.query.status }),
  };

  const events = await eventService.queryEvent(filter);
  res.send(events);
});

const getEventById = catchAsync(async (req, res) => {
  const event = await eventService.getEventById(req.params.id);
  if (!event) {
    throw new ApiError(httpStatus.NOT_FOUND, 'Event not found');
  }
  res.send(event);
});

const updateEvent = catchAsync(async (req, res) => {
  const event = await eventService.updateEventById(req.params.id, req.body);
  res.send(event);
});

const deleteEvent = catchAsync(async (req, res) => {
  await eventService.deleteEventById(req.params.id);
  res.status(httpStatus.NO_CONTENT).send();
});

const inviteUser = catchAsync(async (req, res) => {
  const event = await eventService.inviteUserToEvent(req.params.id, req.user.id);
  res.send(event);
});

module.exports = {
  createEvent,
  getEvent,
  getEventById,
  updateEvent,
  deleteEvent,
  inviteUser,
};

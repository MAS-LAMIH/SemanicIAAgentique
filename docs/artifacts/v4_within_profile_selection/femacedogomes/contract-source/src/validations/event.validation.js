const Joi = require('joi');
const { objectId } = require('./custom.validation');

const createEvent = {
  body: Joi.object().keys({
    title: Joi.string().required(),
    description: Joi.string().required(),
    startTime: Joi.date().required(),
    endTime: Joi.date().greater(Joi.ref('startTime')).required(),
    attendees: Joi.array().items(Joi.string().custom(objectId)),
    status: Joi.string().valid('confirmed', 'pending', 'canceled'),
  }),
};

const getEvent = {
  query: Joi.object().keys({
    startDate: Joi.date(),
    endDate: Joi.date().greater(Joi.ref('startDate')),
    status: Joi.string().valid('confirmed', 'pending', 'canceled'),
    limit: Joi.number().integer(),
    page: Joi.number().integer(),
  }),
};

const updateEvent = {
  params: Joi.object().keys({
    id: Joi.string().custom(objectId).required(),
  }),
  body: Joi.object()
    .keys({
      title: Joi.string(),
      description: Joi.string(),
      startTime: Joi.date(),
      endTime: Joi.date().greater(Joi.ref('startTime')),
      status: Joi.string().valid('confirmed', 'pending', 'canceled'),
    })
    .min(1),
};

const deleteEvent = {
  params: Joi.object().keys({
    id: Joi.string().custom(objectId).required(),
  }),
};

const inviteUser = {
  params: Joi.object().keys({
    id: Joi.string().custom(objectId).required(),
  }),
};

module.exports = {
  createEvent,
  getEvent,
  updateEvent,
  deleteEvent,
  inviteUser,
};

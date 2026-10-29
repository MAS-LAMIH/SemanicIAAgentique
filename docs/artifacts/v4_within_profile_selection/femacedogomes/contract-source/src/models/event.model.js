const mongoose = require('mongoose');

const eventSchema = new mongoose.Schema({
  title: { type: String, required: true }, // Título do evento
  description: { type: String, required: true }, // Descrição do evento
  startTime: { type: Date, required: true }, // Hora de início
  endTime: { type: Date, required: true }, // Hora de término
  createdBy: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true }, // Criador do evento
  attendees: [{ type: mongoose.Schema.Types.ObjectId, ref: 'User' }], // Convidados (se implementado)
  status: { type: String, enum: ['confirmed', 'pending', 'canceled'], default: 'confirmed' }, // Status do evento
  createdAt: { type: Date, default: Date.now }, // Data de criação
  updatedAt: { type: Date, default: Date.now }, // Última atualização
});

/**
 * @typedef Event
 */
const Event = mongoose.model('Event', eventSchema);

module.exports = Event;

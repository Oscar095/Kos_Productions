const { Controller, Get } = require('@nestjs/common');

function AppController() {}

AppController.prototype.getRoot = function () {
  return { message: 'KX API' };
};

Controller()(AppController);
Get()(AppController.prototype, 'getRoot', Object.getOwnPropertyDescriptor(AppController.prototype, 'getRoot'));

module.exports.AppController = AppController;

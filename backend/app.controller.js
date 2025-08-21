const { Controller, Get } = require('@nestjs/common');

function AppController() {}

AppController.prototype.getRoot = function () {
  return { message: 'KX API' };
};

AppController.prototype.getProducts = function () {
  return [
    { id: 1, name: 'Producto 1', price: 19.99 },
    { id: 2, name: 'Producto 2', price: 29.99 },
    { id: 3, name: 'Producto 3', price: 39.99 },
  ];
};

Controller()(AppController);
Get()(AppController.prototype, 'getRoot', Object.getOwnPropertyDescriptor(AppController.prototype, 'getRoot'));
Get('products')(AppController.prototype, 'getProducts', Object.getOwnPropertyDescriptor(AppController.prototype, 'getProducts'));

module.exports.AppController = AppController;

const { Module } = require('@nestjs/common');
const { AppController } = require('./app.controller');

class AppModule {}

module.exports.AppModule = Module({
  controllers: [AppController],
})(AppModule);

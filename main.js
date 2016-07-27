'use strict';

const electron = require('electron');
const app = electron.app;  // Module to control application life.
const BrowserWindow = electron.BrowserWindow;  // Module to create native browser window.
const crashReporter = electron.crashReporter;
const ipcMain = electron.ipcMain

const path = require('path');

require('./quranapp.js').init();

const appConfig = require('./config/appConfig');
const logger = require('./lib/modules/logger');

/* ------------------------------------------------
 * App initialization
 * ------------------------------------------------ */
let mainWindow;

crashReporter.start(); // Report crashes to our server.

ipcMain.on('set-title', (event, title) => {
  mainWindow.setTitle(title || appConfig.name);
});

ipcMain.on('quit', () => {
  app.quit();
});

app.on('window-all-closed', () => {
  // Quit when all windows are closed.
  // On OS X it is common for applications and their menu bar
  // to stay active until the user quits explicitly with Cmd + Q
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('ready', () => {
  mainWindow = new BrowserWindow({
    center: true
  });
  mainWindow.maximize();

  mainWindow.setMinimumSize(770, 400);

  mainWindow.loadURL('file://' + __dirname + '/index.html');

  // Open the DevTools.
  mainWindow.webContents.openDevTools();

  // if (appConfig.env !== 'production') mainWindow.openDevTools();

  mainWindow.on('close', () => {
    app.quit();
  });

  mainWindow.on('closed', () => {
    // Dereference the window object, usually you would store windows
    // in an array if your app supports multi windows, this is the time
    // when you should delete the corresponding element.
    mainWindow = null;
  });
});


/*var mongoClient = require('mongodb').MongoClient
 , assert = require('assert');

 var serverurl = 'mongodb://meisam:meisam@quranpalace.com:27017/test';*/

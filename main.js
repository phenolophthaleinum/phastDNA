// console.log('Hello from Electron 👋')

// Modules to control application life and create native browser window
const { app, BrowserWindow, dialog, ipcMain} = require('electron')
const path = require('path')
const child_process = require('child_process')

function createWindow () {
  // Create the browser window.
  const mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: true,
      contextIsolation: false,
      enableRemoteModule: true,
      titleBarStyle: 'hidden',
      titleBarOverlay: {
        color: '#2f3241',
        symbolColor: '#74b1be',
        height: 60
      }
    }
  })

  // and load the index.html of the app.
  // mainWindow.loadFile('index.html')
  
  var flask = child_process.spawn('python', ['./phastDNA_gui.py']);

  // and load the Flask app.
  mainWindow.loadURL('http://localhost:5000')
  // Open the DevTools.
  // mainWindow.webContents.openDevTools()
}

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.whenReady().then(() => {
  console.log('App is ready!');
  createWindow()

  app.on('activate', function () {
    // On macOS it's common to re-create a window in the app when the
    // dock icon is clicked and there are no other windows open.
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })

  console.log('App is ready!');
  ipcMain.on('open-dir-dialog', function (e) {
    dialog.showOpenDialog({
     title: 'Select a directory',
     properties: ['openDirectory']
    }).then(result => {
      const selectedDirectory = result.filePaths[0];
      console.log(e.sender)
      e.sender.send('selected-dir', selectedDirectory);
      // console.log(selectedDirectory);
      // Pass the selectedDirectory to the text field in the form
    }).catch(err => {
      console.log(err);
   });
  })
})

// Quit when all windows are closed, except on macOS. There, it's common
// for applications and their menu bar to stay active until the user quits
// explicitly with Cmd + Q.
app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') app.quit()
})

// In this file you can include the rest of your app's specific main process
// code. You can also put them in separate files and require them here.
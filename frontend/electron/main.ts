import { app, BrowserWindow, ipcMain, Notification, safeStorage } from 'electron'
import path from 'path'
import fs from 'fs'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

process.env.APP_ROOT = path.join(__dirname, '..')

// 🚧 Use ['ENV_NAME'] avoid vite:define plugin - SystemJS encouters problem
export const VITE_DEV_SERVER_URL = process.env['VITE_DEV_SERVER_URL']
export const MAIN_DIST = path.join(process.env.APP_ROOT || '', 'dist-electron')
export const RENDERER_DIST = path.join(process.env.APP_ROOT || '', 'dist')

process.env.VITE_PUBLIC = VITE_DEV_SERVER_URL ? path.join(process.env.APP_ROOT || '', 'public') : RENDERER_DIST

let win: BrowserWindow | null

function createWindow() {
  win = new BrowserWindow({
    icon: path.join(process.env.VITE_PUBLIC || '', 'electron-vite.svg'),
    width: 1200,
    height: 800,
    minWidth: 900,
    minHeight: 600,
    webPreferences: {
      preload: path.join(__dirname, 'preload.mjs'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  })

  // Test active push message to Renderer-process.
  win.webContents.on('did-finish-load', () => {
    win?.webContents.send('main-process-message', (new Date).toLocaleString())
  })

  if (VITE_DEV_SERVER_URL) {
    win.loadURL(VITE_DEV_SERVER_URL as string)
  } else {
    win.loadFile(path.join(RENDERER_DIST, 'index.html'))
  }
}

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
    win = null
  }
})

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow()
  }
})

app.whenReady().then(createWindow)

// IPC Listeners
ipcMain.handle('show-notification', (_, title: string, body: string) => {
  if (Notification.isSupported()) {
    new Notification({
      title,
      body,
    }).show()
  }
})

const secureStoragePath = path.join(app.getPath('userData'), 'secure-store.json')

function readSecureStore(): Record<string, string> {
  try {
    if (fs.existsSync(secureStoragePath)) {
      const data = fs.readFileSync(secureStoragePath, 'utf8')
      return JSON.parse(data)
    }
  } catch (err) {
    console.error('Error reading secure store:', err)
  }
  return {}
}

function writeSecureStore(store: Record<string, string>) {
  try {
    fs.writeFileSync(secureStoragePath, JSON.stringify(store), 'utf8')
  } catch (err) {
    console.error('Error writing secure store:', err)
  }
}

ipcMain.handle('secure-set', (_, key: string, value: string) => {
  const store = readSecureStore()
  if (safeStorage.isEncryptionAvailable()) {
    store[key] = safeStorage.encryptString(value).toString('base64')
  } else {
    store[key] = value // Fallback if OS encryption is unavailable
  }
  writeSecureStore(store)
})

ipcMain.handle('secure-get', (_, key: string) => {
  const store = readSecureStore()
  const val = store[key]
  if (!val) return null
  if (safeStorage.isEncryptionAvailable()) {
    try {
      return safeStorage.decryptString(Buffer.from(val, 'base64'))
    } catch {
      return null
    }
  }
  return val
})

ipcMain.handle('secure-delete', (_, key: string) => {
  const store = readSecureStore()
  delete store[key]
  writeSecureStore(store)
})

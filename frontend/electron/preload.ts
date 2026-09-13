import { ipcRenderer, contextBridge } from 'electron'

// --------- Expose some API to the Renderer process ---------
contextBridge.exposeInMainWorld('electron', {
  showNotification: (title: string, body: string) => ipcRenderer.invoke('show-notification', title, body),
  onMessage: (callback: (message: string) => void) => {
    ipcRenderer.on('main-process-message', (_event, message) => callback(message))
  },
  secureSet: (key: string, value: string) => ipcRenderer.invoke('secure-set', key, value),
  secureGet: (key: string) => ipcRenderer.invoke('secure-get', key),
  secureDelete: (key: string) => ipcRenderer.invoke('secure-delete', key),
})

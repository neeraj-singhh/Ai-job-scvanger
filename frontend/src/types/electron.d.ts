interface Window {
  electron: {
    showNotification: (title: string, body: string) => Promise<void>
    onMessage: (callback: (message: string) => void) => void
    secureSet: (key: string, value: string) => Promise<void>
    secureGet: (key: string) => Promise<string | null>
    secureDelete: (key: string) => Promise<void>
  }
}

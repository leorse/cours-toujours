import type { CapacitorConfig } from '@capacitor/cli'
import { config as loadDotenv } from 'dotenv'
import { resolve } from 'path'

// Charge .env.local si présent (contient SERVER_URL=http://192.168.x.x:8080)
loadDotenv({ path: resolve(__dirname, '.env.local') })

const serverUrl = process.env.SERVER_URL

const config: CapacitorConfig = {
  appId: 'fr.parcours.cours',
  appName: 'Parcours',
  // webDir pointe vers le build Spring Boot (utilisé en fallback si server.url absent)
  webDir: '../cours-back/src/main/resources/static',
  server: serverUrl
    ? {
        url: serverUrl,
        cleartext: true, // autorise HTTP (non-HTTPS) sur Android
      }
    : undefined,
  android: {
    allowMixedContent: true, // autorise HTTP dans la WebView Android
  },
}

export default config

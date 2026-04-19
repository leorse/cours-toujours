# Build Android (APK)

## Architecture

L'APK Android est une coquille Capacitor qui charge l'application depuis le serveur Spring Boot sur le réseau local :

```
APK Android (WebView Capacitor)
    │
    └─→ http://192.168.1.x:8080  ← Spring Boot (PC sur le réseau WiFi)
            ├── /api/**    → REST
            └── /**        → React app (compilé par npm run build)
```

L'APK n'embarque pas le code React — il pointe vers le serveur. Pour mettre à jour l'appli, `npm run build` suffit (pas besoin de recompiler l'APK).

---

## Prérequis

| Outil | Utilité |
|---|---|
| Android Studio | Compiler et signer l'APK |
| JDK 17+ | Gradle (inclus avec Android Studio) |
| Node.js 18+ | Build React |

---

## Configuration — première fois

### 1. Trouver l'IP du PC sur le réseau WiFi

```powershell
# Windows
ipconfig
# → chercher "Adresse IPv4" sur l'interface WiFi, ex : 192.168.1.42
```

### 2. Créer `.env.local` dans `cours-front/`

```bash
# cours-front/.env.local
SERVER_URL=http://192.168.1.42:8080
```

Ce fichier est ignoré par git (`.gitignore`). Chaque développeur a le sien.

### 3. S'assurer qu'Android Studio est installé

Télécharger depuis : https://developer.android.com/studio

---

## Workflow de build

### Build complet (1ère fois ou après changement de code)

```bash
cd cours-front

# 1. Compiler le React (copie dans cours-back/src/main/resources/static/)
npm run build

# 2. Synchroniser Capacitor (relit .env.local → server.url dans l'APK)
npx cap sync android

# 3. Ouvrir Android Studio
npx cap open android
```

Dans Android Studio :
- **Build → Build APK** pour un APK de debug
- **Build → Generate Signed Bundle/APK** pour un APK de release (signature requise)

### Raccourci (tout en une commande)

```bash
cd cours-front
npm run android:open    # build + sync + ouvre Android Studio
```

---

## Lancer le serveur (PC)

Le serveur Spring Boot doit tourner sur le PC avant d'ouvrir l'app Android :

```bash
cd cours-back
mvn spring-boot:run
```

L'app Android va charger `http://[SERVER_URL]` au démarrage. Si le serveur est éteint, l'app affichera une page d'erreur.

---

## Mettre à jour l'appli sans recompiler l'APK

```bash
cd cours-front
npm run build    # met à jour les fichiers dans cours-back/src/main/resources/static/
# Redémarrer le serveur Spring Boot si nécessaire
```

L'APK installé sur Android rechargera automatiquement le nouveau contenu au prochain lancement.

---

## Changer l'IP du serveur

Si le PC change d'IP sur le réseau :

```bash
# 1. Mettre à jour cours-front/.env.local
SERVER_URL=http://192.168.1.NOUVELLE_IP:8080

# 2. Re-synchroniser et recompiler l'APK
cd cours-front
npx cap sync android
npx cap open android   # Build → Build APK
```

---

## Structure générée

```
cours-front/
├── android/                  ← projet Android Studio (ignoré par git)
│   ├── app/
│   │   ├── src/main/
│   │   │   ├── AndroidManifest.xml
│   │   │   └── res/xml/network_security_config.xml  ← autorise HTTP
│   │   └── build.gradle
│   └── build.gradle
├── capacitor.config.ts       ← config Capacitor (lit .env.local)
└── .env.local                ← ignoré par git, contient SERVER_URL
```

---

## Troubleshooting

| Problème | Solution |
|---|---|
| App blanche au démarrage | Vérifier que Spring Boot tourne, IP correcte dans `.env.local` |
| Erreur réseau | Vérifier que PC et téléphone sont sur le même WiFi |
| `npx cap sync` ignore `.env.local` | Vérifier que `dotenv` est installé (`npm install`) |
| Build Gradle échoue | Ouvrir Android Studio → File → Sync Project with Gradle Files |
